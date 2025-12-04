-- ==================== STEP 1: CREATE SCHEMA ====================
-- This creates the schema in your iceberg_data catalog
CREATE SCHEMA IF NOT EXISTS iceberg_data.cpl_schema
WITH (location = 's3a://watsonx-data-dd963065-e56e-4069-90cb-46167114f4b1/cpl_schema');

-- ==================== STEP 2: VERIFY SCHEMA CREATED ====================
SHOW SCHEMAS IN iceberg_data;
-- Should see: cpl_schema in the list

-- ==================== STEP 3: CREATE CPL REQUESTS TABLE ====================
CREATE TABLE IF NOT EXISTS iceberg_data.cpl_schema.cpl_requests (
    request_id VARCHAR,
    document_id VARCHAR,
    student_name VARCHAR,
    nuid VARCHAR,
    request_type VARCHAR,
    target_course VARCHAR,
    status VARCHAR,
    credits_awarded DECIMAL(4,2),
    advisor_notes VARCHAR,
    submitted_date TIMESTAMP,
    updated_date TIMESTAMP,
    updated_by VARCHAR,
    document_count INT
) WITH (
    format = 'PARQUET',
    partitioned_by = ARRAY['status']
);

-- ==================== STEP 4: VERIFY TABLE CREATED ====================
SHOW TABLES IN iceberg_data.cpl_schema;
-- Should see: cpl_requests

-- ==================== STEP 5: TEST TABLE (Optional) ====================
-- Insert a test record
INSERT INTO iceberg_data.cpl_schema.cpl_requests VALUES (
    'TEST001',
    'test-doc-id-123',
    'Test Student',
    'N00000000',
    'Test Request',
    'TEST 0000',
    'pending',
    NULL,
    'Test record',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    'System',
    1
);

-- Query to see the test record
SELECT * FROM iceberg_data.cpl_schema.cpl_requests;

-- ==================== STEP 6: DELETE TEST RECORD (Clean up) ====================
DELETE FROM iceberg_data.cpl_schema.cpl_requests WHERE request_id = 'TEST001';

-- ==================== DONE! ====================
-- Your table is ready to receive student CPL requests!