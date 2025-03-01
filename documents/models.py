from django.db import models
import numpy as np
from pgvector.django import VectorField

class Document(models.Model):
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    extracted_text = models.TextField(blank=True)
    
    def __str__(self):
        return f"Document {self.id} - {self.file.name}"

class TextChunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.IntegerField()
    text = models.TextField()
    embedding = VectorField(dimensions=1536)  # For OpenAI embeddings
    
    class Meta:
        indexes = [
            models.Index(fields=["document"]),
            # Vector index will be added in a separate migration
        ]
    
    def set_embedding(self, embedding_list):
        """Convert list to NumPy array before storing"""
        if len(embedding_list) != 1536:  # Check for OpenAI's embedding dimension
            raise ValueError(f"Expected embedding dimension 1536, got {len(embedding_list)}")
        self.embedding = np.array(embedding_list)
    
    def __str__(self):
        return f"Chunk {self.chunk_index} of Document {self.document.id}"