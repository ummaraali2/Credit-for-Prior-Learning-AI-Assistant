"""
IBM Cloud Object Storage Handler
Stores and retrieves original student documents
"""

import os
import ibm_boto3
from ibm_botocore.client import Config
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class COSHandler:
    def __init__(self):
        self.cos_client = ibm_boto3.client(
            's3',
            ibm_api_key_id=os.getenv('COS_API_KEY'),
            ibm_service_instance_id=os.getenv('COS_INSTANCE_ID'),
            config=Config(signature_version='oauth'),
            endpoint_url=os.getenv('COS_ENDPOINT')
        )
        self.bucket_name = os.getenv('COS_BUCKET_NAME', 'cpl-documents')
        print(f"[SUCCESS] COS Handler initialized (bucket: {self.bucket_name})")
    
    def upload_document(self, file_bytes, document_id, filename, metadata):
        """
        Upload document to COS
        
        Args:
            file_bytes: File content as bytes
            document_id: Unique document ID
            filename: Original filename
            metadata: Dict with student info (nuid, student_name, etc.)
        
        Returns:
            str: COS object key
        """
        try:
            # Create unique object key: {document_id}/{filename}
            object_key = f"{document_id}/{filename}"
            
            # Prepare metadata for COS
            cos_metadata = {
                'document-id': document_id,
                'student-name': metadata.get('student_name', 'Unknown'),
                'nuid': metadata.get('nuid', 'N/A'),
                'request-type': metadata.get('request_type', 'Not Specified'),
                'target-course': metadata.get('target_course', 'Not Specified'),
                'upload-date': datetime.utcnow().isoformat()
            }
            
            # Upload to COS
            self.cos_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=file_bytes,
                Metadata=cos_metadata
            )
            
            print(f"      [SUCCESS] Uploaded to COS: {object_key}")
            return object_key
            
        except Exception as e:
            print(f"      [ERROR] COS upload failed: {str(e)}")
            raise
    
    def get_document(self, object_key):
        """
        Retrieve document from COS
        
        Args:
            object_key: COS object key (document_id/filename)
        
        Returns:
            tuple: (file_bytes, metadata_dict)
        """
        try:
            response = self.cos_client.get_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            
            file_bytes = response['Body'].read()
            metadata = response.get('Metadata', {})
            
            return file_bytes, metadata
            
        except Exception as e:
            print(f"[ERROR] COS retrieval failed: {str(e)}")
            raise
    
    def get_document_by_id(self, document_id, filename):
        """
        Retrieve document using document_id and filename
        
        Args:
            document_id: Document ID
            filename: Original filename
        
        Returns:
            tuple: (file_bytes, metadata_dict)
        """
        object_key = f"{document_id}/{filename}"
        return self.get_document(object_key)
    
    def list_documents(self, prefix=""):
        """
        List all documents in bucket
        
        Args:
            prefix: Optional prefix to filter (e.g., document_id)
        
        Returns:
            list: List of object keys
        """
        try:
            response = self.cos_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            return [obj['Key'] for obj in response['Contents']]
            
        except Exception as e:
            print(f"[ERROR] COS list failed: {str(e)}")
            return []
    
    def delete_document(self, object_key):
        """Delete document from COS"""
        try:
            self.cos_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            print(f"[SUCCESS] Deleted from COS: {object_key}")
            return True
        except Exception as e:
            print(f"[ERROR] COS delete failed: {str(e)}")
            return False


# Singleton instance
_cos_handler = None

def get_cos_handler():
    """Get or create COS handler instance"""
    global _cos_handler
    if _cos_handler is None:
        _cos_handler = COSHandler()
    return _cos_handler