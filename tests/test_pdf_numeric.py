import unittest
import os
from unittest.mock import patch, Mock
from fpdf import FPDF
from app import app

# Geçerli bir PDF dosyası oluşturma fonksiyonu
def create_valid_pdf(file_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Test PDF", ln=True, align="C")
    pdf.output(file_path)

class PDFUploadTestCase(unittest.TestCase):
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
    def test_pdf_upload_numeric_name(self, mock_openai_embeddings, mock_pinecone_vectorstore):
        # OpenAI API'yi mock'la
        mock_openai_embeddings.return_value = Mock()
        mock_pinecone_vectorstore.return_value = Mock()

        # Geçerli bir PDF dosyası oluştur (1.pdf)
        pdf_name = '1.pdf'
        pdf_path = os.path.join(os.path.dirname(__file__), pdf_name)
        create_valid_pdf(pdf_path)  # Geçerli PDF dosyası oluştur

        # Dosyayı yükle
        with open(pdf_path, 'rb') as pdf_file:
            data = {
                'file': (pdf_file, pdf_name)
            }
            response = self.app.post('/v1/pdf', content_type='multipart/form-data', data=data)

        # Yanıtı logla
        print(f"Response Status: {response.status_code}")
        print(f"Response Data: {response.data}")

        # Yanıt durum kodunun 200 olduğunu kontrol et
        self.assertEqual(response.status_code, 200)

        # Yanıtı kontrol et
        response_data = response.get_json()
        pdf_id = response_data.get('pdf_id')

        # pdf_id'nin string bir integer olup olmadığını kontrol et
        self.assertTrue(pdf_id.isdigit(), "pdf_id string olmalı ve integer değer içermeli.")
        
        # İlgili index adının doğru oluşturulduğunu kontrol et
        index_name = response_data.get('index_name')
        self.assertTrue(index_name.startswith("sevenapps-"), "Index adı sevenapps- ile başlamalı.")

if __name__ == '__main__':
    unittest.main()
