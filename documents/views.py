from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Document, TextChunk
from .serializers import DocumentSerializer
import pdfplumber
import os
import re
import logging

# Set up logging
logger = logging.getLogger(__name__)

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize these components only when needed
        self.text_processor = None
        
    def _get_text_processor(self):
        if not self.text_processor:
            from .text_processing import TextProcessor
            self.text_processor = TextProcessor()
        return self.text_processor

    def create(self, request, *args, **kwargs):
        """
        Handles document upload and text extraction.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            document = serializer.save()
            
            # Extract text if the document is a PDF
            if document.file.name.endswith('.pdf'):
                try:
                    logger.info(f"Extracting text from PDF: {document.file.name}")
                    
                    # Use the new extraction method
                    extracted_text = self.extract_text_from_pdf(document.file.path)
                    document.extracted_text = extracted_text
                    document.save()
                    
                    # Process the document to create chunks and embeddings
                    success = self.process_document(document)
                    
                    if not success:
                        return Response(
                            {'warning': 'Document was saved but there was an error processing it for search.'},
                            status=status.HTTP_201_CREATED
                        )
                    
                except Exception as e:
                    logger.error(f"Error extracting text from PDF: {str(e)}")
                    return Response(
                        {'error': f'Error extracting text: {str(e)}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            return Response(
                DocumentSerializer(document).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from PDF with improved handling of layout and spacing.
        """
        full_text = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text.append(page_text)
        
        # Join pages with clear page separators
        joined_text = "\n\n".join(full_text)
        
        # Clean up text
        joined_text = self.clean_text(joined_text)
        
        return joined_text
    
    def clean_text(self, text):
        """Clean up extracted text to fix common PDF extraction issues"""
        if not text:
            return ""
            
        # Fix excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix hyphenation issues common in PDFs
        text = text.replace(' - ', '-')
        
        # Fix paragraph boundaries
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)  # Single newlines become spaces
        text = re.sub(r'\n{3,}', '\n\n', text)  # Multiple newlines reduced to double
        
        # Clean up other common issues
        text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)  # Remove leading spaces
        
        return text.strip()
    
    def process_document(self, document):
        """
        Processes the document text: splits it into chunks and generates embeddings.
        """
        try:
            logger.info(f"Processing document: {document.id}")
            
            text_processor = self._get_text_processor()
            
            # Split text into chunks
            chunks = text_processor.create_text_chunks(document.extracted_text)
            logger.info(f"Created {len(chunks)} chunks for document {document.id}")
            
            if not chunks:
                logger.warning(f"No chunks created for document {document.id}")
                return False
            
            # Store chunks and embeddings using the text processor
            chunk_ids = text_processor.store_document_chunks(document, chunks)
            logger.info(f"Stored {len(chunk_ids)} chunks and embeddings for document {document.id}")
            
            return len(chunk_ids) > 0
        except Exception as e:
            logger.error(f"Error processing document {document.id}: {str(e)}")
            return False
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """
        Searches for similar chunks based on a query.
        """
        query = request.data.get('query')
        limit = request.data.get('limit', 5)
        
        if not query:
            return Response(
                {"error": "Query is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            logger.info(f"Searching for similar chunks for query: {query}")
            
            text_processor = self._get_text_processor()
            
            # Find similar chunks using the text processor
            results = text_processor.find_similar_chunks(query, limit)
            logger.info(f"Found {len(results)} similar chunks")
            
            return Response(results)
                
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return Response(
                {"error": f"Search error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def answer(self, request):
        """
        Answers a query based on the content of uploaded documents.
        """
        query = request.data.get('query')
        
        if not query:
            return Response(
                {"error": "Query is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            logger.info(f"Answering query: {query}")
            
            text_processor = self._get_text_processor()
            
            # Get the answer from the text processor
            result = text_processor.answer_query(query)
            logger.info(f"Answer found with {len(result.get('source_chunks', []))} source chunks")
            
            return Response(result)
                
        except Exception as e:
            logger.error(f"Error answering query: {str(e)}")
            return Response(
                {"error": f"Error answering query: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """
        Clear all documents from the database.
        """
        try:
            count = Document.objects.count()
            Document.objects.all().delete()
            logger.info(f"Deleted all {count} documents from the database")
            return Response(
                {"message": f"Successfully deleted all {count} documents"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error clearing documents: {str(e)}")
            return Response(
                {"error": f"Error clearing documents: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )