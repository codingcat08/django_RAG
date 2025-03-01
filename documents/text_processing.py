from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from django.conf import settings
import numpy as np
import logging
from typing import List, Dict, Any
from .models import TextChunk, Document

logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self):
        try:
            # Initialize OpenAI embeddings
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=settings.OPENAI_API_KEY
            )
            
            # Test embedding creation to verify API key
            test_embed = self.embeddings.embed_query("Test")
            if not test_embed or len(test_embed) == 0:
                raise ValueError("Embedding generation failed")
                
        except Exception as e:
            logger.error(f"Error initializing OpenAI Embeddings: {str(e)}")
            raise ValueError(f"OpenAI API key error: {str(e)}")
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Increased from 100
            chunk_overlap=200,  # Increased from 20
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def create_text_chunks(self, text: str) -> List[str]:
        """Split text into smaller chunks using RecursiveCharacterTextSplitter"""
        if not text or len(text.strip()) == 0:
            logger.warning("Empty text provided for chunking")
            return []
            
        chunks = self.text_splitter.split_text(text)
        
        # Filter out chunks that are too small
        filtered_chunks = [chunk for chunk in chunks if len(chunk.strip()) > 50]
        print('then open ai api key is',settings.OPENAI_API_KEY)
        print(filtered_chunks)
        return filtered_chunks
    
    def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for a single piece of text"""
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple text chunks"""
        if not texts:
            return []
            
        try:
            # Use OpenAI's batch embedding to be more efficient
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise
    
    def store_document_chunks(self, document: Document, chunks: List[str]) -> List[int]:
        if not chunks:
            logger.warning(f"No chunks to store for document {document.id}")
            return []
            
        chunk_ids = []
        try:
            # Generate embeddings for all chunks
            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            embeddings = self.generate_embeddings_batch(chunks)
            
            if len(embeddings) != len(chunks):
                logger.error(f"Embedding count mismatch: {len(embeddings)} embeddings for {len(chunks)} chunks")
                return []

            # Store chunks and embeddings
            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                # Make sure the embedding is valid
                if embedding is None or len(embedding) == 0:
                    logger.error(f"Invalid embedding for chunk {i}")
                    continue
                    
                # Create the chunk and directly set the embedding value
                chunk = TextChunk.objects.create(
                    document=document,
                    chunk_index=i,
                    text=chunk_text,
                    embedding=np.array(embedding)  # Set embedding directly here
                )
                chunk_ids.append(chunk.id)
            
            return chunk_ids
        except Exception as e:
            logger.error(f"Error storing document chunks: {str(e)}")
            raise
    '''    
    def store_document_chunks(self, document: Document, chunks: List[str]) -> List[int]:
        """
        Store document chunks and their embeddings in the database.
        Returns a list of created chunk IDs.
        """
        if not chunks:
            logger.warning(f"No chunks to store for document {document.id}")
            return []
            
        chunk_ids = []
        try:
            # Generate embeddings for all chunks
            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            print('the number of chunks here is',len(chunks))
            embeddings = self.generate_embeddings_batch(chunks)
            
            if len(embeddings) != len(chunks):
                logger.error(f"Embedding count mismatch: {len(embeddings)} embeddings for {len(chunks)} chunks")
                return []

            # Store chunks and embeddings
            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                chunk = TextChunk.objects.create(
                    document=document,
                    chunk_index=i,
                    text=chunk_text
                )
                # Use the set_embedding method
                chunk.set_embedding(embedding)
                chunk.save()
                chunk_ids.append(chunk.id)
            
            return chunk_ids
        except Exception as e:
            logger.error(f"Error storing document chunks: {str(e)}")
            raise
    '''
    def find_similar_chunks(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find chunks similar to the query using vector similarity search."""
        try:
            query_embedding = np.array(self.generate_embeddings(query))
            
            # Use Django ORM with pgvector's cosine_distance function
            from pgvector.django import CosineDistance
            
            chunks = TextChunk.objects.annotate(
                similarity=1 - CosineDistance('embedding', query_embedding)
            ).order_by('-similarity')[:limit]
            
            # Format the results
            results_list = []
            for chunk in chunks:
                results_list.append({
                    "chunk_id": chunk.id,
                    "text": chunk.text,
                    "chunk_index": chunk.chunk_index,
                    "document_id": chunk.document_id,
                    "similarity": float(chunk.similarity)
                })
            
            return results_list
        except Exception as e:
            logger.error(f"Error finding similar chunks: {str(e)}")
            raise
    
    def answer_query(self, query: str) -> Dict[str, Any]:
        """
        Find most relevant chunks and use LLM to generate an answer.
        """
        try:
            relevant_chunks = self.find_similar_chunks(query, limit=3)
            
            if not relevant_chunks:
                return {
                    "answer": "I couldn't find any relevant information to answer your query.",
                    "source_chunks": []
                }
            
            # Combine context from chunks
            context = "\n\n".join([
                f"Document {chunk['document_id']}, Chunk {chunk['chunk_index']}: {chunk['text']}" 
                for chunk in relevant_chunks
            ])
            
            try:
                # Initialize ChatOpenAI
                llm = ChatOpenAI(
                    temperature=0,
                    openai_api_key=settings.OPENAI_API_KEY,
                    model="gpt-3.5-turbo"
                )
                
                # Generate answer
                prompt = f"""
                Answer the following question based on the provided context. If you cannot answer
                the question from the context, say "I don't have enough information to answer this question."
                
                Context:
                {context}
                
                Question: {query}
                """
                
                response = llm.invoke(prompt)
                answer = response.content
                
                return {
                    "answer": answer,
                    "source_chunks": relevant_chunks
                }
            except Exception as e:
                logger.error(f"Error generating answer with LLM: {str(e)}")
                # Fallback to using the most relevant chunk as the answer
                return {
                    "answer": f"Based on the documents, I found this information: {relevant_chunks[0]['text']}",
                    "source_chunks": relevant_chunks,
                    "error": str(e)
                }
        except Exception as e:
            logger.error(f"Error in answer_query: {str(e)}")
            return {
                "answer": "An error occurred while processing your query.",
                "error": str(e)
            }