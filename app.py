from flask import Flask, request,jsonify
from flask_cors import CORS 
from pinecone import Pinecone,ServerlessSpec
from dotenv import load_dotenv
import uuid 
import os
from tempfile import NamedTemporaryFile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain



load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV_KEY = os.getenv('PINECONE_ENVIRONMENT')


app = Flask(__name__)




# Store PDF data by pdf_id for further use
pdf_store = {}
pdf_id_counter = 1  # Start ID from 1

@app.route('/v1/pdf', methods=['POST'])
def upload_pdf():
    global pdf_id_counter  # Use the global counter
    pdf_id = str(pdf_id_counter)  # Set current PDF ID
    
    for file_name, handle in request.files.items():
        temp_path = f'/tmp/{pdf_id}.pdf'
        handle.save(temp_path)

        loader = PyPDFLoader(file_path=temp_path)
        data = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = text_splitter.split_documents(data)

        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        index_name = "sevenapps"
        docsearch = PineconeVectorStore.from_documents(texts, embeddings, index_name=index_name)
        
        # Store the document search object in memory with the pdf_id
        pdf_store[pdf_id] = docsearch

    # Increment the PDF ID counter for the next PDF
    pdf_id_counter += 1

    return jsonify({"pdf_id": pdf_id})
    
@app.route('/v1/chat/<pdf_id>', methods=['POST'])
def chat_with_pdf(pdf_id):
    if pdf_id not in pdf_store:
        return jsonify({"error": "PDF not found"}), 404
    
    query = request.json.get('message', '')
    
    # Retrieve the document search object by pdf_id
    docsearch = pdf_store[pdf_id]
    
    # Perform similarity search
    docs = docsearch.similarity_search(query)
    
    # Create the chain for question answering
    llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
    chain = load_qa_chain(llm, chain_type="stuff")
    
    # Get the result from the chain
    result = chain.run(input_documents=docs, question=query)
    
    return jsonify({"response": result})




if __name__ == '__main__':
    app.run(debug=True)