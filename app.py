import time  # Import time for sleep
from flask import Flask, request, jsonify
from flask_cors import CORS
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os
import logging  # Add logging for debugging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV_KEY = os.getenv('PINECONE_ENVIRONMENT')

# Initialize Pinecone client
pc = Pinecone(
    api_key=PINECONE_API_KEY
)

app = Flask(__name__)

# Define directory for uploads
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Store PDF data by pdf_id for further use
pdf_store = {}
pdf_id_counter = 1  # Starting ID from 1

@app.route('/v1/pdf', methods=['POST'])
def upload_pdf():
    global pdf_id_counter  # Use the global counter

    logging.info(f"Received PDF upload request. Current pdf_id_counter: {pdf_id_counter}")
    
    for file_name, handle in request.files.items():
        # Define path where the file will be saved
        temp_path = os.path.join(UPLOAD_FOLDER, f'{pdf_id_counter}.pdf')
        
        # Check if the file already exists, if so increase the pdf_id_counter
        while os.path.exists(temp_path):
            logging.warning(f"File {temp_path} already exists, incrementing pdf_id_counter.")
            pdf_id_counter += 1
            temp_path = os.path.join(UPLOAD_FOLDER, f'{pdf_id_counter}.pdf')

        handle.save(temp_path)  # Save the new file
        logging.info(f"File saved to: {temp_path}")

        loader = PyPDFLoader(file_path=temp_path)
        data = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = text_splitter.split_documents(data)

        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        index_name = f"sevenapps-{pdf_id_counter}"  # Updated to use hyphen (-)

        logging.info(f"Attempting to create index: {index_name}")
        
        # List existing indexes
        existing_indexes = pc.list_indexes().names()
        logging.info(f"Existing indexes: {existing_indexes}")

        # Check if index already exists, if not create one
        if index_name not in existing_indexes:
            try:
                pc.create_index(
                    name=index_name,
                    dimension=1536,  # Adjusted dimension size
                    metric="cosine",  # Similarity metric as cosine
                    spec=ServerlessSpec(cloud="aws", region="us-east-1")  # Region and cloud provider
                )
                
                # Wait until the index is ready
                while not pc.describe_index(index_name).status["ready"]:
                    logging.info(f"Waiting for index {index_name} to be ready...")
                    time.sleep(1)

                logging.info(f"Index {index_name} is now ready.")

            except Exception as e:
                logging.error(f"Error creating index {index_name}: {str(e)}")
                return jsonify({"error": f"Failed to create index: {str(e)}"}), 500
        else:
            logging.info(f"Index {index_name} already exists, skipping creation.")

        # Initialize the vector store using the newly created or existing index
        docsearch = PineconeVectorStore.from_documents(texts, embeddings, index_name=index_name)
        
        # Store the document search object in memory with the pdf_id
        pdf_store[str(pdf_id_counter)] = docsearch

        # Increment the PDF ID counter for the next PDF
        pdf_id_counter += 1

        return jsonify({"pdf_id": str(pdf_id_counter - 1), "index_name": index_name})

@app.route('/v1/chat/<pdf_id>', methods=['POST'])
def chat_with_pdf(pdf_id):
    if pdf_id not in pdf_store:
        logging.error(f"PDF ID {pdf_id} not found.")
        return jsonify({"error": "PDF not found"}), 404
    
    query = request.json.get('message', '')
    logging.info(f"Received chat query: {query} for PDF ID: {pdf_id}")
    
    # Retrieve the document search object by pdf_id
    docsearch = pdf_store.get(pdf_id)
    if not docsearch:
        logging.error(f"Document search object not found for PDF ID: {pdf_id}")
        return jsonify({"error": "Document search object not found"}), 404
    
    # Perform similarity search
    docs = docsearch.similarity_search(query)
    if not docs:
        logging.error(f"No documents found in similarity search for query: {query}")
        return jsonify({"response": "No relevant documents found for the query."}), 404
    
    logging.info(f"Documents found: {docs}")
    
    # Create the chain for question answering
    llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
    chain = load_qa_chain(llm, chain_type="stuff")
    
    # Get the result from the chain
    try:
        result = chain.run(input_documents=docs, question=query)
        logging.info(f"Chat result: {result}")
    except Exception as e:
        logging.error(f"Error while generating response from chain: {str(e)}")
        return jsonify({"error": "Failed to generate response"}), 500
    
    return jsonify({"response": result})

if __name__ == '__main__':
    app.run(debug=True)
