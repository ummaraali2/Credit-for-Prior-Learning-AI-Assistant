"""
Simple Flask Server for CPL System
ONLY returns 4 fields: student_name, request_type, target_course, document_id
Watson Assistant passes these to LLM extension (which queries Milvus automatically)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
CORS(app)

# ==================== YOUR CONFIGURATION ====================
PRESTO_HOST = "dd963065-e56e-4069-90cb-46167114f4b1.ct7kqd4s0l8kkd26qgo0.lakehouse.ibmappdomain.cloud"
PRESTO_PORT = "30670"
USERNAME = "ibmlhapikey_syeda.umm@northeastern.edu"
PASSWORD = "oa6updVpfRktCbXRtxMwcLhYivPg4odcB8Gb03Eu8Pdt"

PRESTO_URL = f"https://{PRESTO_HOST}:{PRESTO_PORT}/v1/statement"

# ==================== PRESTO QUERY FUNCTION ====================

def query_presto(sql):
    """
    Execute Presto SQL query and handle nextUri pagination
    Returns: (result_dict, error_message)
    """
    try:
        print(f"\n[ICEBERG] Executing SQL: {sql[:100]}...")
        
        # Step 1: Submit query
        response = requests.post(
            PRESTO_URL,
            data=sql,
            auth=(USERNAME, PASSWORD),
            headers={
                'X-Presto-User': 'admin',
                'Content-Type': 'text/plain'
            },
            timeout=30
        )
        
        if response.status_code != 200:
            return None, f"Query submission failed: {response.status_code}"
        
        result = response.json()
        next_uri = result.get('nextUri')
        
        # Step 2: Poll for results (handle pagination)
        columns = []
        data = []
        attempts = 0
        max_attempts = 60
        
        while next_uri and attempts < max_attempts:
            attempts += 1
            time.sleep(0.5)
            
            print(f"  [POLLING] Polling attempt {attempts}...")
            
            result_response = requests.get(
                next_uri,
                auth=(USERNAME, PASSWORD),
                headers={'X-Presto-User': 'admin'},
                timeout=30
            )
            
            if result_response.status_code != 200:
                return None, f"Failed to fetch results: {result_response.status_code}"
            
            result = result_response.json()
            
            # Get column names
            if not columns and result.get('columns'):
                columns = [col['name'] for col in result['columns']]
            
            # Get data rows
            if result.get('data'):
                data.extend(result['data'])
            
            # Check if query is finished
            state = result.get('stats', {}).get('state')
            if state == 'FINISHED':
                print(f"  [SUCCESS] Query complete! Got {len(data)} rows")
                break
            
            next_uri = result.get('nextUri')
        
        return {'columns': columns, 'data': data}, None
        
    except Exception as e:
        return None, f"Query error: {str(e)}"


# ==================== API ENDPOINTS ====================

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'CPL Query Service',
        'endpoints': {
            '/query-student': 'POST {"nuid": "1"}',
            '/health': 'GET'
        }
    })


@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'service': 'CPL Query Service'})


@app.route('/query-student', methods=['POST'])
def query_student():
    """
    Query student by NUID - Returns ONLY 4 fields
    
    Request: {"nuid": "1"}
    
    Response: {
        "student_name": "John W. Smith",
        "request_type": "Experience-based waiver",
        "target_course": "PJM 5900",
        "document_id": "abc-123-def"
    }
    """
    try:
        data = request.json
        nuid = data.get('nuid')
        
        if not nuid:
            return jsonify({'error': 'NUID is required'}), 400
        
        print(f"\n{'='*60}")
        print(f"[QUERY] QUERY FOR NUID: {nuid}")
        print(f"{'='*60}")
        
        # Query Iceberg for ONLY 4 fields
        sql = f"""
            SELECT 
                student_name,
                request_type,
                target_course,
                document_id
            FROM iceberg_data.cpl_schema.cpl_requests
            WHERE nuid = '{nuid}'
            ORDER BY submitted_date DESC
            LIMIT 1
        """
        
        print("[ICEBERG] Querying Iceberg table...")
        result, error = query_presto(sql)
        
        if error:
            print(f"[ERROR] Error: {error}")
            return jsonify({'error': error}), 500
        
        if not result['data'] or len(result['data']) == 0:
            print(f"[WARNING]  No student found with NUID: {nuid}")
            return jsonify({'error': 'Student not found', 'nuid': nuid}), 404
        
        # Parse the 4 fields
        student_name = result['data'][0][0]
        request_type = result['data'][0][1]
        target_course = result['data'][0][2]
        document_id = result['data'][0][3]
        
        response = {
            'student_name': student_name,
            'request_type': request_type,
            'target_course': target_course,
            'document_id': document_id
        }
        
        print(f"[SUCCESS] Found student: {student_name}")
        print(f"   Request: {request_type}")
        print(f"   Course: {target_course}")
        print(f"   Document: {document_id}")
        print(f"{'='*60}\n")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ==================== START SERVER ====================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("[UPLOADING] CPL QUERY SERVICE (Simplified)")
    print("="*60)
    print(f"[ICEBERG] Presto: {PRESTO_HOST}")
    print(f"[COS KEY] Iceberg Table: iceberg_data.cpl_schema.cpl_requests")
    print(f"🌐 Server: http://localhost:5000")
    print("="*60)
    print("\nReturns ONLY 4 fields:")
    print("  - student_name")
    print("  - request_type")
    print("  - target_course")
    print("  - document_id")
    print("\nWatson passes these to LLM extension (grounded with Milvus)")
    print("="*60)
    print("\n Run 'ngrok http 5001' in another terminal!")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)