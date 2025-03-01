from rest_framework import serializers
from .models import Document, TextChunk

class TextChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextChunk
        fields = ['id', 'chunk_index', 'text']

class DocumentSerializer(serializers.ModelSerializer):
    chunks = TextChunkSerializer(many=True, read_only=True)
    
    class Meta:
        model = Document
        fields = ['id', 'file', 'uploaded_at', 'extracted_text', 'chunks']
        read_only_fields = ['extracted_text', 'chunks']