import React, { useState, useEffect } from 'react';

const DocumentUpload = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [extractedText, setExtractedText] = useState('');
  const [documentId, setDocumentId] = useState(null);
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [answering, setAnswering] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  // Add this new function to clear all documents
  const clearAllDocuments = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/documents/clear_all/', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        console.error('Failed to clear documents');
        return;
      }

      // Clear local state as well
      setUploadedFiles([]);
      setExtractedText('');
      setDocumentId(null);
      setAnswer('');
      console.log('Database cleared successfully');
    } catch (err) {
      console.error('Error clearing database:', err);
    }
  };

  // Add this useEffect hook to clear documents when the component mounts
  useEffect(() => {
    clearAllDocuments();
  }, []); // Empty dependency array means this runs once when component mounts

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please select a PDF file');
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/documents/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      setExtractedText(data.extracted_text);
      setDocumentId(data.id);
      setUploadedFiles([...uploadedFiles, { id: data.id, name: file.name }]);
      setFile(null);
    } catch (err) {
      setError('Failed to upload document: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleQueryChange = (event) => {
    setQuery(event.target.value);
  };

  const handleAskQuestion = async () => {
    if (!query.trim()) {
      setError('Please enter a question');
      return;
    }

    setAnswering(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/documents/answer/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error('Failed to get answer');
      }

      const data = await response.json();
      setAnswer(data.answer);
    } catch (err) {
      setError('Failed to get answer: ' + err.message);
    } finally {
      setAnswering(false);
    }
  };

  // Rest of your component remains the same
  const containerStyle = {
    maxWidth: '800px',
    margin: '20px auto',
    padding: '20px'
  };

  const uploadAreaStyle = {
    border: '2px dashed #ccc',
    padding: '20px',
    marginBottom: '20px',
    textAlign: 'center'
  };

  const buttonStyle = {
    backgroundColor: loading ? '#ccc' : '#007bff',
    color: 'white',
    padding: '10px 20px',
    border: 'none',
    borderRadius: '4px',
    cursor: loading ? 'not-allowed' : 'pointer',
    width: '100%'
  };

  const errorStyle = {
    backgroundColor: '#ffebee',
    color: '#c62828',
    padding: '10px',
    marginTop: '10px',
    borderRadius: '4px'
  };

  const extractedTextStyle = {
    backgroundColor: '#f5f5f5',
    padding: '15px',
    marginTop: '20px',
    borderRadius: '4px',
    whiteSpace: 'pre-wrap',
    maxHeight: '300px',
    overflowY: 'auto'
  };

  const questionSectionStyle = {
    marginTop: '30px',
    padding: '15px',
    backgroundColor: '#e3f2fd',
    borderRadius: '4px'
  };

  const textareaStyle = {
    width: '100%',
    padding: '10px',
    marginBottom: '10px',
    borderRadius: '4px',
    border: '1px solid #ccc'
  };

  const answerStyle = {
    backgroundColor: '#f1f8e9',
    padding: '15px',
    marginTop: '20px',
    borderRadius: '4px',
    border: '1px solid #c5e1a5'
  };

  const fileListStyle = {
    marginTop: '20px',
    padding: '10px',
    backgroundColor: '#f9f9f9',
    borderRadius: '4px'
  };

  return (
    <div style={containerStyle}>
      <h1>Document Q&A System</h1>

      <div style={uploadAreaStyle}>
        <h2>Upload Documents</h2>
        <input
          type="file"
          onChange={handleFileChange}
          accept=".pdf"
        />
        {file && (
          <div style={{ marginTop: '10px' }}>
            Selected file: {file.name}
          </div>
        )}
      </div>

      <button
        onClick={handleUpload}
        disabled={!file || loading}
        style={buttonStyle}
      >
        {loading ? 'Uploading...' : 'Upload Document'}
      </button>

      {error && (
        <div style={errorStyle}>
          {error}
        </div>
      )}

      {uploadedFiles.length > 0 && (
        <div style={fileListStyle}>
          <h3>Uploaded Documents:</h3>
          <ul>
            {uploadedFiles.map((file) => (
              <li key={file.id}>{file.name}</li>
            ))}
          </ul>
        </div>
      )}

      {extractedText && (
        <div style={extractedTextStyle}>
          <h3>Document Preview:</h3>
          <div>
            {extractedText.length > 500 
              ? extractedText.substring(0, 500) + '...' 
              : extractedText}
          </div>
        </div>
      )}

      <div style={questionSectionStyle}>
        <h2>Ask Questions About Your Documents</h2>
        <textarea
          style={textareaStyle}
          rows="3"
          value={query}
          onChange={handleQueryChange}
          placeholder="Enter your question about the uploaded documents..."
        />
        <button
          onClick={handleAskQuestion}
          disabled={answering || !uploadedFiles.length}
          style={{
            ...buttonStyle,
            backgroundColor: answering || !uploadedFiles.length ? '#ccc' : '#28a745'
          }}
        >
          {answering ? 'Getting Answer...' : 'Ask Question'}
        </button>
      </div>

      {answer && (
        <div style={answerStyle}>
          <h3>Answer:</h3>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;