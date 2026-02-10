#!/bin/bash

# Test script for document upload API
# Usage: ./test-upload.sh [pdf-file-path]

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

API_URL="http://localhost:8000"
PDF_FILE="${1:-test.pdf}"

echo -e "${BLUE}=== Medical Verification MVP - Upload Test ===${NC}\n"

# Check if services are running
echo -e "${BLUE}1. Checking if API is healthy...${NC}"
curl -s "${API_URL}/health" | jq . || {
    echo "❌ API is not running. Start with: docker compose up"
    exit 1
}
echo -e "${GREEN}✓ API is healthy${NC}\n"

# Create a dummy PDF if test file doesn't exist
if [ ! -f "$PDF_FILE" ]; then
    echo -e "${BLUE}2. Creating dummy PDF for testing...${NC}"
    echo "%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Medical Record) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000317 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
410
%%EOF" > "$PDF_FILE"
    echo -e "${GREEN}✓ Created $PDF_FILE${NC}\n"
fi

# Upload the PDF
echo -e "${BLUE}3. Uploading PDF: $PDF_FILE${NC}"
UPLOAD_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/documents/upload" \
    -H "Content-Type: multipart/form-data" \
    -F "file=@${PDF_FILE}")

echo "$UPLOAD_RESPONSE" | jq .
DOCUMENT_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.document_id')

if [ "$DOCUMENT_ID" = "null" ]; then
    echo "❌ Upload failed"
    exit 1
fi
echo -e "${GREEN}✓ Document uploaded successfully (ID: $DOCUMENT_ID)${NC}\n"

# Wait for processing
echo -e "${BLUE}4. Waiting for Celery worker to process document...${NC}"
sleep 5

# Check document status
echo -e "${BLUE}5. Checking document status...${NC}"
STATUS_RESPONSE=$(curl -s "${API_URL}/api/v1/documents/${DOCUMENT_ID}")
echo "$STATUS_RESPONSE" | jq .

STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status')
if [ "$STATUS" = "COMPLETED" ]; then
    echo -e "${GREEN}✓ Document processed successfully!${NC}\n"
    
    # Show OCR result summary
    WORD_COUNT=$(echo "$STATUS_RESPONSE" | jq '.ocr_result | fromjson | .pages[0].words | length')
    echo -e "${BLUE}6. OCR Result Summary:${NC}"
    echo "   - Words extracted: $WORD_COUNT"
    echo "   - Mock OCR service working correctly"
else
    echo -e "⚠️  Document status: $STATUS"
    echo "   Check celery_worker logs: docker compose logs celery_worker"
fi

# List all documents
echo -e "\n${BLUE}7. All documents:${NC}"
curl -s "${API_URL}/api/v1/documents" | jq '.documents'

echo -e "\n${GREEN}=== Test Complete ===${NC}"
