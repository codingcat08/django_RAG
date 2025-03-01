from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
import os
import tempfile
from .models import Document, TextChunk

class DocumentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create a temporary PDF file for testing
        self.pdf_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        self.pdf_file.write(b'%PDF-1.5\n%Test PDF content')  # Minimal PDF header
        self.pdf_file.close()
    
    def tearDown(self):
        # Clean up the temporary file
        os.unlink(self.pdf_file.name)
    
    @patch('pdfplumber.open')
    def test_document_upload(self, mock_pdf_open):
        # Mock PDF extraction
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test document content."
        mock_pdf.pages = [mock_page]
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf
        
        # Mock the text processor to avoid actual embedding generation
        with patch('documents.views.DocumentViewSet._get_text_processor') as mock_get_processor:
            mock_processor = MagicMock()
            mock_processor.create_text_chunks.return_value = ["Test document content."]
            mock_processor.store_document_chunks.return_value = [1]
            mock_get_processor.return_value = mock_processor
            
            # Upload the PDF file
            with open(self.pdf_file.name, 'rb') as pdf:
                file_content = pdf.read()
                
            upload_file = SimpleUploadedFile(
                "test.pdf", 
                file_content,
                content_type="application/pdf"
            )
            
            url = reverse('document-list')
            response = self.client.post(url, {'file': upload_file}, format='multipart')
            
            # Check response
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Document.objects.count(), 1)
            
            # Verify the document was processed
            mock_get_processor.assert_called_once()
            mock_processor.create_text_chunks.assert_called_once()
            mock_processor.store_document_chunks.assert_called_once()
    
    @patch('documents.text_processing.TextProcessor.generate_embeddings')
    @patch('documents.text_processing.TextProcessor.find_similar_chunks')
    def test_document_search(self, mock_find_chunks, mock_generate_embeddings):
        # Create a test document
        document = Document.objects.create(
            file="test.pdf",
            extracted_text="Test document content."
        )
        
        # Mock embedding generation and similarity search
        mock_generate_embeddings.return_value = [0.1] * 1536
        mock_find_chunks.return_value = [
            {
                "chunk_id": 1,
                "text": "Test document content.",
                "chunk_index": 0,
                "document_id": document.id,
                "similarity": 0.95
            }
        ]
        
        # Test search endpoint
        url = reverse('document-search')
        response = self.client.post(url, {'query': 'test query'}, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['text'], "Test document content.")