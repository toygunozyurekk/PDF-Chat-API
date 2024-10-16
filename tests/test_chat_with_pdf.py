import unittest
import os
from unittest.mock import patch, Mock
from fpdf import FPDF
from app import app, pdf_store

# Geçerli bir PDF dosyası oluşturma fonksiyonu
def create_valid_pdf(file_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Test PDF for Chat", ln=True, align="C")
    pdf.output(file_path)

class PDFChatTestCase(unittest.TestCase):
    def setUp(self):
        # Flask test istemcisini başlat
        self.app = app.test_client()
        self.app.testing = True

        # Test dosyalarının yükleneceği klasörü tanımla
        self.upload_folder = 'uploads'
        
        # Eğer uploads klasörü yoksa, oluştur
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

    def tearDown(self):
        # Testten sonra uploads klasöründeki dosyaları temizle
        for file_name in os.listdir(self.upload_folder):
            file_path = os.path.join(self.upload_folder, file_name)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error cleaning up test files: {e}")

    @patch('app.PineconeVectorStore')
    @patch('app.OpenAIEmbeddings')
    def test_chat_with_pdf(self, mock_openai_embeddings, mock_pinecone_vectorstore):
        # OpenAI ve Pinecone'u mock'la
        mock_openai_embeddings.return_value = Mock()
        mock_pinecone_vectorstore.return_value = Mock()

        # Geçerli bir PDF dosyası oluştur (2.pdf)
        pdf_name = '2.pdf'
        pdf_path = os.path.join(os.path.dirname(__file__), pdf_name)
        create_valid_pdf(pdf_path)  # Geçerli PDF dosyası oluştur

        # Dosyayı yükle
        with open(pdf_path, 'rb') as pdf_file:
            data = {
                'file': (pdf_file, pdf_name)
            }
            response = self.app.post('/v1/pdf', content_type='multipart/form-data', data=data)

        # Yükleme yanıtını kontrol et
        self.assertEqual(response.status_code, 200)

        response_data = response.get_json()
        pdf_id = response_data.get('pdf_id')

        # pdf_id'nin string bir integer olup olmadığını kontrol et
        self.assertTrue(pdf_id.isdigit(), "pdf_id string olmalı ve integer değer içermeli.")

        # Chat ile PDF'ye soru sorma işlemi
        chat_data = {
            "message": "What is this PDF about?"
        }

        chat_response = self.app.post(f'/v1/chat/{pdf_id}', json=chat_data)
        
        # Chat yanıtını kontrol et
        self.assertEqual(chat_response.status_code, 200)

        chat_response_data = chat_response.get_json()
        self.assertIn("response", chat_response_data)
        self.assertIsInstance(chat_response_data["response"], str)

        print(f"Chat Response: {chat_response_data['response']}")

if __name__ == '__main__':
    unittest.main()
