import os
import chainlit as cl
from chainlit.types import AskFileResponse
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.chroma import Chroma
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_groq import ChatGroq


# Loading environment variables from .env file
load_dotenv() 

# Function to initialize conversation chain with GROQ language model
groq_api_key = os.environ['GROQ_API_KEY']

# Initializing GROQ chat with provided API key, model name, and settings
llm_groq = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-70b-8192", temperature=0.2)

# Initialize embeddings model
embeddings_model = OpenAIEmbeddings(api_key=os.environ['OPENAI_API_KEY'])

@cl.on_chat_start
async def start():
    await cl.Message(content="Hello. Please upload a PDF file or a Word document using the button in the chat box.").send()

async def handle_file_upload(file: AskFileResponse):
    await process_file(file)

async def process_file(file: AskFileResponse):
    print("File type is ", file.mime)
    if file.mime == "application/pdf":
        loader = PyMuPDFLoader(file.path)
    elif file.mime == "text/plain":
        loader = TextLoader(file.path)
    elif file.mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        loader = Docx2txtLoader(file.path)
    elif file.mime == "text/csv":
        loader = CSVLoader(file.path)

    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    doc_search = Chroma.from_documents(docs, embeddings)
    return doc_search

def process_pdfs(pdf_paths):
    docs = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    
    for pdf_path in pdf_paths:
        loader = PyMuPDFLoader(pdf_path)
        documents = loader.load()
        docs.extend(text_splitter.split_documents(documents))
    
    doc_search = Chroma.from_documents(docs, embeddings_model)
    return doc_search

@cl.on_message
async def on_message(msg: cl.Message):
    doc_search = cl.user_session.get("doc_search")
    # handle file attachment
    if msg.elements:
        # Clear existing documents
        my_db = Chroma()
        for collection in my_db._client.list_collections():
            ids = collection.get()['ids']
            print('REMOVE %s document(s) from %s collection' % (str(len(ids)), collection.name))
            if len(ids): collection.delete(ids)

        # Processing images exclusively
        await cl.Message(content="Processing the document. Please wait ...").send()
        documents = [file.path for file in msg.elements if file.mime.endswith("pdf") or file.name.endswith("docx") or file.mime == "text/csv"] 

        # print(msg.elements)

        if not documents:
            await cl.Message(content="Please select a PDF or a Word document").send()
            return
        
        doc_search = process_pdfs(documents)

        cl.user_session.set("doc_search", doc_search)
        await cl.Message(content="Done. One sec, let me think about your comment... ").send()
    
    # handle text message
    # Retrieve the chain from user session
    chain = cl.user_session.get("doc_search") 

    #call backs happens asynchronously/parallel 
    cb = cl.AsyncLangchainCallbackHandler()
    

    # Initialize message history for conversation
    message_history = ChatMessageHistory()
    
    # Memory for conversational context
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        chat_memory=message_history,
        return_messages=True,
    )

    # Create a chain that uses the Chroma vector store
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm_groq,
        chain_type="stuff",
        retriever=doc_search.as_retriever(),
        memory=memory,
        return_source_documents=True,
    )


    # call the chain with user's message content
    res = await chain.ainvoke(msg.content, callbacks=[cb])
    answer = res["answer"]

    msg = cl.Message(content="")
    await msg.send()
    
    for token in answer:
        await msg.stream_token(token)

    await msg.update()