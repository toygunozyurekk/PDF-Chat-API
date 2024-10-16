# PDF Chat API

## 1. Project Overview

The PDF Chat API is a Flask-based application that allows users to upload PDF files and interact with them via a chat-based interface. The application leverages OpenAI's GPT-3.5 and Pinecone for embedding and storing the PDF content, enabling similarity-based search and question answering functionalities.



## 2. Features

- **2.1 PDF Upload**: Upload PDF files, which are processed and stored in Pinecone.
- **2.2 Chat Interface**: Interact with the uploaded PDFs using natural language queries.
- **2.3 OpenAI GPT-3.5 Integration**: Use OpenAI to process and respond to user queries.
- **2.4 Pinecone Storage**: Efficient storage and retrieval of PDF embeddings using Pinecone vector stores.



## 3. Setup Instructions

### 3.1 Clone the Repository
To begin, clone the repository to your local machine and navigate into the project directory:

```bash
git clone <repository-url>
cd PDF-Chat-API
```


### 3.2 Set up the Virtual Environment
In order to avoid conflicts with other Python projects and to manage dependencies more easily, we will set up a virtual environment. This ensures the project’s dependencies are isolated and won’t interfere with other projects.

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment (Linux/MacOS)
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```


### 3.3 Install Dependencies
Once the virtual environment is activated, install the project dependencies using pip. These dependencies are listed in the requirements.txt file.

```bash
pip install -r requirements.txt
```


### 3.4 Environment Configuration
You need to create a **.env** file to configure environment variables that include your OpenAI and Pinecone API keys.

Create a **.env** file in the root directory of the project.
Add the following variables:

```bash
OPENAI_API_KEY=<your_openai_api_key>
PINECONE_API_KEY=<your_pinecone_api_key>
PINECONE_ENVIRONMENT=<your_pinecone_environment>
```


Replace **<your_key>** with your actual API keys.

### 3.5 Run the Application
To start the Flask server locally, run the following command:

```bash
python app.py
```


The application will be accessible at **http://127.0.0.1:5000/** by default.


## 4. API Endpoints

### 4.1 Upload PDF - /v1/pdf
Method: POST
Description: Upload a PDF file to the server and store it in the Pinecone vector store for querying.

#### 4.1.1 Request Format:
file: Multipart form-data that includes the PDF file to be uploaded.

#### 4.1.2 Example Response:
```json
{
  "pdf_id": "1",
  "index_name": "sevenapps-1"
}
```


#### 4.1.3 Error Responses:
500 Internal Server Error: If the PDF cannot be processed or stored correctly.

### 4.2 Chat with PDF - /v1/chat/<pdf_id>
Method: POST
Description: Query a specific PDF by its pdf_id using natural language queries, and receive a response based on the PDF’s content.

#### 4.2.1 Request Format:
JSON body with a message field that contains the user's query.
Example:
```json
{
  "message": "What is this PDF about?"
}
```


#### 4.2.2 Example Response:

```json
{
  "response": "I'm sorry, but I don't have access to the content of the PDF file you are referring to."
}
```


#### 4.2.3 Error Responses:
404 Not Found: If the provided pdf_id does not exist.
500 Internal Server Error: If an issue occurs while processing the query.

##  5. Testing Procedures

### 5.1 Running the Test Suite
The project includes unit tests located in the tests/ directory. These tests validate the functionality of the PDF upload and chat features.

To run all tests, navigate to the root directory of the project and execute:

```bash
python -m unittest discover tests
```


### 5.2 Example Test Files
test_pdf_numeric.py: Tests the functionality of uploading PDFs and verifying the correct assignment of **pdf_id** and Pinecone index.
test_chat_with_pdf.py: Tests the ability to interact with a PDF through the chat interface after uploading it.

### 5.3 Creating Test PDFs
If needed, generate simple PDF files for testing using the FPDF library. Here’s an example function to create a test PDF:

```python 
from fpdf import FPDF

def create_test_pdf(file_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Test PDF", ln=True, align="C")
    pdf.output(file_path)
```


## 6. Contribution Guidelines

To contribute to the project, please adhere to the following guidelines:

### 6.1 Documentation
Ensure that the documentation is updated with any changes made to the codebase.

### 6.2 Testing
All contributions should be thoroughly tested. Include unit tests for any new features or bug fixes.

### 6.3 Code Quality
Follow Python's PEP 8 style guide for code quality. Write clean, maintainable, and efficient code.
























