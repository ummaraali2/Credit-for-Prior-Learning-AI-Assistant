"""
Iceberg Table Handler for watsonx.data
Stores student metadata in Apache Iceberg table using Presto
FIXED: Now properly handles document_name for COS downloads
"""

import prestodb  # Uses presto-python-client package
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class IcebergHandler:
    """Handle student metadata storage in Apache Iceberg tables"""
    
    def __init__(self):
        # Presto connection details for watsonx.data
        self.host = os.getenv('WATSONX_DATA_HOST', 'localhost')
        self.port = int(os.getenv('WATSONX_DATA_PORT', 8443))
        self.catalog = os.getenv('ICEBERG_CATALOG', 'iceberg_data')
        self.schema = os.getenv('ICEBERG_SCHEMA', 'cpl_schema')
        self.table = os.getenv('ICEBERG_TABLE', 'cpl_requests')
        self.user = os.getenv('WATSONX_DATA_USER', 'ibmlhapikey')
        self.password = os.getenv('WATSONX_DATA_PASSWORD')  # Your IBM API key
        
        # Connection
        self.conn = None
    
    def connect(self):
        """Connect to watsonx.data Presto"""
        try:
            self.conn = prestodb.dbapi.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                catalog=self.catalog,
                schema=self.schema,
                http_scheme='https',
                auth=prestodb.auth.BasicAuthentication(self.user, self.password)
            )
            print(f"[SUCCESS] Connected to Presto: {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[ERROR] Presto connection error: {str(e)}")
            return False
    
    def insert_request(self, request_data):
        """
        Insert student CPL request into Iceberg table
        
        Args:
            request_data (dict): {
                'document_id': str,
                'student_name': str,
                'nuid': str,
                'request_type': str,
                'target_course': str,
                'document_name': str,  # ← CRITICAL for downloads
                'cos_key': str (optional)
            }
        """
        if not self.conn:
            if not self.connect():
                return False
        
        try:
            cursor = self.conn.cursor()
            
            # Generate request ID
            request_id = self._generate_request_id()
            
            # Get values with defaults
            document_id = request_data.get('document_id', '')
            student_name = request_data.get('student_name', 'Unknown')
            nuid = request_data.get('nuid', 'N/A')
            request_type = request_data.get('request_type', 'Not Specified')
            target_course = request_data.get('target_course', 'Not Specified')
            document_name = request_data.get('document_name', 'document.pdf')  # ← CRITICAL
            
            # Build INSERT statement with document_name
            sql = f"""
            INSERT INTO {self.catalog}.{self.schema}.{self.table} 
            (
                request_id,
                document_id,
                document_name,
                student_name,
                nuid,
                request_type,
                target_course,
                status,
                credits_awarded,
                advisor_notes,
                submitted_date,
                updated_date,
                updated_by,
                document_count
            ) 
            VALUES (
                '{request_id}',
                '{document_id}',
                '{document_name}',
                '{student_name}',
                '{nuid}',
                '{request_type}',
                '{target_course}',
                'pending',
                NULL,
                '',
                CAST(CURRENT_TIMESTAMP AS TIMESTAMP),
                CAST(CURRENT_TIMESTAMP AS TIMESTAMP),
                'System',
                1
            )
            """
            
            cursor.execute(sql)
            
            print(f"[SUCCESS] Inserted request to Iceberg table:")
            print(f"   Request ID: {request_id}")
            print(f"   Student: {student_name} ({nuid})")
            print(f"   Type: {request_type}")
            print(f"   Document: {document_name}")  # ← Confirm stored
            
            return request_id
            
        except Exception as e:
            print(f"[ERROR] Insert error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_all_requests(self):
        """Get all CPL requests from Iceberg table"""
        if not self.conn:
            if not self.connect():
                return []
        
        try:
            cursor = self.conn.cursor()
            
            # SELECT with document_name
            sql = f"""
            SELECT 
                request_id,
                document_id,
                document_name,
                student_name,
                nuid,
                request_type,
                target_course,
                status,
                credits_awarded,
                advisor_notes,
                submitted_date,
                updated_date,
                updated_by,
                document_count
            FROM {self.catalog}.{self.schema}.{self.table}
            ORDER BY submitted_date DESC
            """
            
            cursor.execute(sql)
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            requests = []
            for row in rows:
                # Handle timestamps - Presto returns them as strings or datetime
                submitted = row[10]
                updated = row[11]
                
                # Convert to ISO format string if needed
                if submitted and hasattr(submitted, 'isoformat'):
                    submitted = submitted.isoformat()
                elif submitted:
                    submitted = str(submitted)
                
                if updated and hasattr(updated, 'isoformat'):
                    updated = updated.isoformat()
                elif updated:
                    updated = str(updated)
                
                requests.append({
                    'id': row[0],  # request_id
                    'documentId': row[1],  # document_id ← FOR DOWNLOAD
                    'documentName': row[2],  # document_name ← FOR DOWNLOAD
                    'studentName': row[3],  # student_name
                    'nuid': row[4],  # nuid
                    'requestType': row[5],  # request_type
                    'targetCourse': row[6],  # target_course
                    'status': row[7],  # status
                    'credits': row[8],  # credits_awarded
                    'notes': row[9] if row[9] else '',  # advisor_notes
                    'submittedDate': submitted,
                    'updatedDate': updated,
                    'updatedBy': row[12]  # updated_by
                })
            
            print(f"[SUCCESS] Retrieved {len(requests)} requests from Iceberg table")
            if len(requests) > 0:
                print(f"   Sample: {requests[0].get('documentName', 'NO NAME')}")
            
            return requests
            
        except Exception as e:
            print(f"[ERROR] Query error: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def update_status(self, request_id, status, credits=None, notes='', updated_by='Advisor'):
        """Update request status in Iceberg table"""
        if not self.conn:
            if not self.connect():
                return False
        
        try:
            cursor = self.conn.cursor()
            
            # Escape single quotes in notes
            notes = notes.replace("'", "''")
            
            # Build UPDATE statement with proper timestamp casting
            credits_sql = f"credits_awarded = {credits}" if credits else "credits_awarded = NULL"
            
            sql = f"""
            UPDATE {self.catalog}.{self.schema}.{self.table}
            SET 
                status = '{status}',
                {credits_sql},
                advisor_notes = '{notes}',
                updated_date = CAST(CURRENT_TIMESTAMP AS TIMESTAMP),
                updated_by = '{updated_by}'
            WHERE request_id = '{request_id}'
            """
            
            cursor.execute(sql)
            
            print(f"[SUCCESS] Updated status for {request_id} to '{status}'")
            return True
            
        except Exception as e:
            print(f"[ERROR] Update error: {str(e)}")
            return False
    
    def _generate_request_id(self):
        """Generate unique request ID"""
        if not self.conn:
            return f"REQ{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        try:
            cursor = self.conn.cursor()
            sql = f"SELECT COUNT(*) FROM {self.catalog}.{self.schema}.{self.table}"
            cursor.execute(sql)
            count = cursor.fetchone()[0]
            return f"REQ{str(count + 1).zfill(6)}"
        except:
            return f"REQ{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def close(self):
        """Close Presto connection"""
        if self.conn:
            self.conn.close()
            print("[DISCONNECTED] Disconnected from Presto")


# Singleton instance
_iceberg_handler = None

def get_iceberg_handler():
    """Get or create Iceberg handler instance"""
    global _iceberg_handler
    if _iceberg_handler is None:
        _iceberg_handler = IcebergHandler()
    return _iceberg_handler