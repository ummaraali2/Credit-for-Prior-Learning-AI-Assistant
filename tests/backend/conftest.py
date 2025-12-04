"""
pytest configuration and shared fixtures for backend tests
"""
import pytest
import sys
import os
from unittest.mock import Mock

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

@pytest.fixture
def mock_cos_client():
    """Mock IBM COS client"""
    mock_client = Mock()
    mock_client.put_object.return_value = {'ETag': 'test-etag'}
    mock_client.get_object.return_value = {
        'Body': Mock(read=lambda: b'test file content'),
        'Metadata': {'student-name': 'Test Student'}
    }
    return mock_client

@pytest.fixture
def mock_iceberg_connection():
    """Mock Presto/Iceberg connection"""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [
        ('REQ001', 'doc-123', 'test.pdf', 'John Doe', '001234567',
         'Credit Transfer', 'CS 5800', 'pending', None, '',
         '2024-01-01T10:00:00', '2024-01-01T10:00:00', 'System')
    ]
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn

@pytest.fixture
def sample_pdf_bytes():
    """Sample PDF file content as bytes"""
    return b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n'

@pytest.fixture
def sample_student_data():
    """Sample student data for testing"""
    return {
        'document_id': 'test-doc-123',
        'student_name': 'John Doe',
        'nuid': '001234567',
        'request_type': 'Credit Transfer',
        'target_course': 'CS 5800',
        'document_name': 'transcript.pdf'
    }