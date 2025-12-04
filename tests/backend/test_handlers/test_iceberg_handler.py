"""
Tests for Iceberg/watsonx.data handler
"""
import pytest
from unittest.mock import Mock, patch
from handlers.iceberg_handler import IcebergHandler

class TestIcebergHandler:

    @patch('handlers.iceberg_handler.prestodb')
    def test_insert_request_success(self, mock_prestodb, mock_iceberg_connection, sample_student_data):
        """Test successful request insertion"""
        mock_prestodb.dbapi.connect.return_value = mock_iceberg_connection

        handler = IcebergHandler()
        result = handler.insert_request(sample_student_data)

        assert result.startswith('REQ')
        mock_iceberg_connection.cursor().execute.assert_called_once()

    @patch('handlers.iceberg_handler.prestodb')
    def test_get_all_requests_success(self, mock_prestodb, mock_iceberg_connection):
        """Test successful request retrieval"""
        mock_prestodb.dbapi.connect.return_value = mock_iceberg_connection

        handler = IcebergHandler()
        requests = handler.get_all_requests()

        assert len(requests) == 1
        assert requests[0]['studentName'] == 'John Doe'
        assert requests[0]['nuid'] == '001234567'
        assert requests[0]['status'] == 'pending'

    @patch('handlers.iceberg_handler.prestodb')
    def test_update_status_success(self, mock_prestodb, mock_iceberg_connection):
        """Test successful status update"""
        mock_prestodb.dbapi.connect.return_value = mock_iceberg_connection

        handler = IcebergHandler()
        result = handler.update_status(
            request_id='REQ001',
            status='approved',
            credits=3,
            notes='Approved for credit transfer',
            updated_by='Dr. Smith'
        )

        assert result is True
        mock_iceberg_connection.cursor().execute.assert_called_once()

    @patch('handlers.iceberg_handler.prestodb')
    def test_connection_failure(self, mock_prestodb):
        """Test connection failure handling"""
        mock_prestodb.dbapi.connect.side_effect = Exception("Connection failed")

        handler = IcebergHandler()
        result = handler.connect()

        assert result is False

    def test_generate_request_id_no_connection(self):
        """Test request ID generation without database connection"""
        handler = IcebergHandler()
        handler.conn = None

        request_id = handler._generate_request_id()

        assert request_id.startswith('REQ')
        assert len(request_id) > 3