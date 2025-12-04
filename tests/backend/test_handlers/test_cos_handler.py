"""
Tests for IBM Cloud Object Storage handler
"""
import pytest
from unittest.mock import Mock, patch
from handlers.cos_handler import COSHandler

class TestCOSHandler:

    @patch('handlers.cos_handler.ibm_boto3')
    def test_upload_document_success(self, mock_boto3, mock_cos_client, sample_student_data):
        """Test successful document upload to COS"""
        mock_boto3.client.return_value = mock_cos_client

        handler = COSHandler()
        result = handler.upload_document(
            file_bytes=b"test content",
            document_id="test-123",
            filename="test.pdf",
            metadata={
                'student_name': 'John Doe',
                'nuid': '001234567',
                'request_type': 'Credit Transfer',
                'target_course': 'CS 5800'
            }
        )

        assert result == "test-123/test.pdf"
        mock_cos_client.put_object.assert_called_once()

        # Verify call arguments
        call_args = mock_cos_client.put_object.call_args
        assert call_args[1]['Bucket'] == handler.bucket_name
        assert call_args[1]['Key'] == "test-123/test.pdf"
        assert call_args[1]['Body'] == b"test content"

    @patch('handlers.cos_handler.ibm_boto3')
    def test_get_document_success(self, mock_boto3, mock_cos_client):
        """Test successful document retrieval from COS"""
        mock_boto3.client.return_value = mock_cos_client

        handler = COSHandler()
        file_bytes, metadata = handler.get_document("test-123/test.pdf")

        assert file_bytes == b'test file content'
        assert metadata['student-name'] == 'Test Student'
        mock_cos_client.get_object.assert_called_once_with(
            Bucket=handler.bucket_name,
            Key="test-123/test.pdf"
        )

    @patch('handlers.cos_handler.ibm_boto3')
    def test_get_document_by_id(self, mock_boto3, mock_cos_client):
        """Test document retrieval using document ID and filename"""
        mock_boto3.client.return_value = mock_cos_client

        handler = COSHandler()
        file_bytes, metadata = handler.get_document_by_id("test-123", "test.pdf")

        assert file_bytes == b'test file content'
        mock_cos_client.get_object.assert_called_once_with(
            Bucket=handler.bucket_name,
            Key="test-123/test.pdf"
        )

    @patch('handlers.cos_handler.ibm_boto3')
    def test_upload_document_failure(self, mock_boto3):
        """Test document upload failure handling"""
        mock_client = Mock()
        mock_client.put_object.side_effect = Exception("COS upload failed")
        mock_boto3.client.return_value = mock_client

        handler = COSHandler()

        with pytest.raises(Exception) as exc_info:
            handler.upload_document(
                file_bytes=b"test content",
                document_id="test-123",
                filename="test.pdf",
                metadata={'student_name': 'John Doe'}
            )

        assert "COS upload failed" in str(exc_info.value)