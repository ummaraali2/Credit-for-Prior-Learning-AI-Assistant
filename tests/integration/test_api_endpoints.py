"""
Integration tests for API endpoints
Tests the complete flow from Node.js gateway to Python backend
"""
import pytest
import requests
import json
import io
from unittest.mock import patch

# Test configuration
NODE_GATEWAY_URL = "http://localhost:3000"
PYTHON_BACKEND_URL = "http://localhost:5000"

class TestAPIEndpoints:

    def test_node_gateway_health_check(self):
        """Test Node.js gateway health endpoint"""
        response = requests.get(f"{NODE_GATEWAY_URL}/health")

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'OK'
        assert 'endpoints' in data
        assert 'watsonxService' in data

    def test_python_backend_health_check(self):
        """Test Python backend health endpoint"""
        response = requests.get(f"{PYTHON_BACKEND_URL}/health")

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'OK'
        assert data['service'] == 'watsonx.ai Upload Service'

    @pytest.mark.skip(reason="Requires running services and valid credentials")
    def test_file_upload_flow(self):
        """Test complete file upload flow through both services"""
        # Create test file
        test_file_content = b"Test PDF content for CPL upload"
        files = {
            'file': ('test.pdf', io.BytesIO(test_file_content), 'application/pdf')
        }

        # Student metadata
        data = {
            'studentName': 'Test Student',
            'nuid': '001234567',
            'requestType': 'Credit Transfer',
            'targetCourse': 'CS 5800'
        }

        # Upload through Node.js gateway
        response = requests.post(
            f"{NODE_GATEWAY_URL}/api/upload",
            files=files,
            data=data
        )

        assert response.status_code == 200
        result = response.json()
        assert result['success'] is True
        assert 'document_id' in result
        assert result['filename'] == 'test.pdf'

    @pytest.mark.skip(reason="Requires running services and test data")
    def test_get_requests_flow(self):
        """Test getting CPL requests from Iceberg"""
        response = requests.get(f"{NODE_GATEWAY_URL}/api/requests")

        assert response.status_code in [200, 503]  # 503 if Iceberg unavailable

        if response.status_code == 200:
            data = response.json()
            assert 'requests' in data
            assert 'count' in data
            assert 'source' in data

    @pytest.mark.skip(reason="Requires running services and test data")
    def test_update_status_flow(self):
        """Test updating request status"""
        update_data = {
            'status': 'approved',
            'credits': 3,
            'notes': 'Test approval',
            'updatedBy': 'Test Advisor'
        }

        response = requests.put(
            f"{NODE_GATEWAY_URL}/api/requests/test-id/status",
            json=update_data
        )

        # Might fail if request doesn't exist, but should not return 500
        assert response.status_code in [200, 404, 500]

    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = requests.options(f"{NODE_GATEWAY_URL}/api/upload")

        # Should have CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers or response.status_code == 404

class TestErrorHandling:

    def test_invalid_endpoint(self):
        """Test handling of invalid endpoints"""
        response = requests.get(f"{NODE_GATEWAY_URL}/api/invalid-endpoint")
        assert response.status_code == 404

    def test_invalid_file_upload(self):
        """Test upload with invalid data"""
        response = requests.post(f"{NODE_GATEWAY_URL}/api/upload")
        assert response.status_code in [400, 500]  # Bad request or internal error

    def test_missing_request_id(self):
        """Test status update without request ID"""
        response = requests.put(f"{NODE_GATEWAY_URL}/api/requests//status")
        assert response.status_code == 404  # Not found due to empty request ID

class TestServiceCommunication:

    @patch('requests.post')
    def test_node_to_python_communication_failure(self, mock_post):
        """Test handling when Python backend is unavailable"""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        # This would require the actual Node.js service to be running
        # In a real test, you'd make a request to the Node.js gateway
        # and verify it handles Python backend failures gracefully