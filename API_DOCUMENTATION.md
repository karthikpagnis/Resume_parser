# Resume Parser API Documentation

## Overview

The Resume Parser API provides RESTful endpoints for parsing resumes and extracting structured information. The API supports single file uploads, batch processing, and section-specific extraction.

## Base URL

```
http://localhost:5000
```

## Authentication

Currently, the API does not require authentication. For production deployment, consider adding API key authentication.

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check API health status

**Response:**

```json
{
	"status": "healthy",
	"timestamp": "2024-05-01T10:30:00.000000"
}
```

**Status Code:** `200 OK`

---

### 2. API Information

**Endpoint:** `GET /info`

**Description:** Get API information and available endpoints

**Response:**

```json
{
	"name": "Resume Parser API",
	"version": "1.0.0",
	"description": "REST API for parsing resumes and extracting structured information",
	"endpoints": {
		"POST /parse": "Parse a single resume file",
		"POST /parse/batch": "Parse multiple resume files",
		"POST /extract/<section>": "Extract specific section from resume",
		"GET /health": "Health check",
		"GET /info": "API information"
	},
	"supported_formats": ["pdf", "docx", "doc", "docs"],
	"max_file_size_mb": 50
}
```

**Status Code:** `200 OK`

---

### 3. Parse Single Resume

**Endpoint:** `POST /parse`

**Description:** Parse a single resume file and extract information

**Request:**

- **Method:** POST
- **Content-Type:** multipart/form-data
- **Parameters:**
  - `file` (required): Resume file (PDF, DOCX, DOC, DOCS)

**Example using cURL:**

```bash
curl -X POST -F "file=@resume.pdf" http://localhost:5000/parse
```

**Example using Python:**

```python
import requests

with open('resume.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/parse', files=files)
    data = response.json()
    print(data)
```

**Success Response:**

```json
{
  "success": true,
  "filename": "resume.pdf",
  "timestamp": "2024-05-01T10:30:00.000000",
  "data": {
    "contact_information": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-123-4567",
      "location": "New York, NY",
      "linkedin": "linkedin.com/in/johndoe",
      "github": "github.com/johndoe"
    },
    "professional_summary": "Experienced software engineer...",
    "work_experience": [...],
    "education": [...],
    "skills": [...],
    "certifications": [...],
    "projects": [...]
  }
}
```

**Status Code:** `200 OK`

**Error Response:**

```json
{
	"success": false,
	"error": "File type not allowed. Allowed: pdf, docx, doc, docs"
}
```

**Status Codes:**

- `200 OK` - Parsing successful
- `400 Bad Request` - Invalid file or no file provided
- `413 Payload Too Large` - File exceeds size limit
- `500 Internal Server Error` - Server error

---

### 4. Parse Multiple Resumes (Batch)

**Endpoint:** `POST /parse/batch`

**Description:** Parse multiple resume files in a single request

**Request:**

- **Method:** POST
- **Content-Type:** multipart/form-data
- **Parameters:**
  - `files` (required): Multiple resume files

**Example using cURL:**

```bash
curl -X POST \
  -F "files=@resume1.pdf" \
  -F "files=@resume2.docx" \
  -F "files=@resume3.doc" \
  http://localhost:5000/parse/batch
```

**Example using Python:**

```python
import requests

files = [
    ('files', open('resume1.pdf', 'rb')),
    ('files', open('resume2.docx', 'rb')),
]

response = requests.post('http://localhost:5000/parse/batch', files=files)
data = response.json()
print(f"Processed: {data['processed']}")
print(f"Errors: {data['errors']}")
```

**Success Response:**

```json
{
  "success": true,
  "total_files": 3,
  "processed": 3,
  "errors": 0,
  "timestamp": "2024-05-01T10:30:00.000000",
  "results": [
    {
      "filename": "resume1.pdf",
      "status": "success",
      "candidate_name": "John Doe",
      "email": "john@example.com",
      "skills_count": 15,
      "data": {...}
    },
    ...
  ],
  "errors_detail": []
}
```

**Status Code:** `200 OK`

**Partial Success Response (with errors):**

```json
{
  "success": true,
  "total_files": 3,
  "processed": 2,
  "errors": 1,
  "timestamp": "2024-05-01T10:30:00.000000",
  "results": [...],
  "errors_detail": [
    {
      "filename": "invalid.txt",
      "error": "File type not allowed"
    }
  ]
}
```

---

### 5. Extract Specific Section

**Endpoint:** `POST /extract/<section>`

**Description:** Extract a specific section from a resume

**Valid Sections:**

- `contact_information`
- `professional_summary`
- `work_experience`
- `education`
- `skills`
- `certifications`
- `projects`

**Request:**

- **Method:** POST
- **Content-Type:** multipart/form-data
- **Parameters:**
  - `file` (required): Resume file
  - `section` (URL parameter): Section to extract

**Example using cURL:**

```bash
# Extract skills only
curl -X POST -F "file=@resume.pdf" http://localhost:5000/extract/skills

# Extract education
curl -X POST -F "file=@resume.pdf" http://localhost:5000/extract/education

# Extract work experience
curl -X POST -F "file=@resume.pdf" http://localhost:5000/extract/work_experience
```

**Example using Python:**

```python
import requests

with open('resume.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/extract/skills', files=files)
    data = response.json()
    skills = data['data']
    print(f"Skills: {skills}")
```

**Success Response:**

```json
{
  "success": true,
  "section": "skills",
  "timestamp": "2024-05-01T10:30:00.000000",
  "data": [
    "Python",
    "JavaScript",
    "React",
    "Docker",
    "AWS",
    ...
  ]
}
```

**Status Code:** `200 OK`

**Error Response:**

```json
{
	"success": false,
	"error": "Invalid section. Valid: contact_information, professional_summary, work_experience, education, skills, certifications, projects"
}
```

---

## Response Format

All responses follow a consistent JSON format:

```json
{
  "success": boolean,
  "data": object|array|string,
  "error": string,
  "timestamp": ISO8601_timestamp
}
```

## Status Codes

| Code | Description                            |
| ---- | -------------------------------------- |
| 200  | Success                                |
| 400  | Bad Request (invalid input)            |
| 404  | Not Found (endpoint doesn't exist)     |
| 413  | Payload Too Large (file size exceeded) |
| 500  | Internal Server Error                  |

## Error Handling

**Common Errors:**

1. **No file provided:**

```json
{
	"success": false,
	"error": "No file provided"
}
```

2. **Unsupported file format:**

```json
{
	"success": false,
	"error": "File type not allowed. Allowed: pdf, docx, doc, docs"
}
```

3. **File too large:**

```json
{
	"success": false,
	"error": "File too large. Maximum size: 50.0 MB"
}
```

4. **Processing error:**

```json
{
	"success": false,
	"error": "Error message describing what went wrong"
}
```

## Rate Limiting

Currently, the API does not have rate limiting. For production use, consider implementing rate limiting.

## File Upload Limits

- **Maximum file size:** 50 MB
- **Supported formats:** PDF, DOCX, DOC, DOCS
- **Maximum batch files:** No hard limit (depends on server resources)

## Deployment

### Local Development

```bash
python app.py
```

Server runs on `http://localhost:5000`

### Production with Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment

```bash
docker-compose up
```

## Performance Considerations

- **Single resume:** 30-60 seconds
- **Batch processing:** ~45-90 seconds per resume
- **Memory usage:** 4-6 GB RAM
- **GPU support:** Automatically detected and used

## Security Considerations

1. **File Validation:** Only allows specific file types
2. **File Size Limits:** Maximum 50 MB per file
3. **Temporary File Cleanup:** Uploaded files are deleted after processing
4. **Input Sanitization:** Filenames are sanitized

For production:

- Add authentication/authorization
- Implement rate limiting
- Use HTTPS
- Set up proper logging and monitoring
- Configure firewall rules

## Examples

### Complete Workflow

```python
import requests
import json

BASE_URL = "http://localhost:5000"

# 1. Check API health
response = requests.get(f"{BASE_URL}/health")
print(f"API Status: {response.json()['status']}")

# 2. Get API info
response = requests.get(f"{BASE_URL}/info")
print(f"Supported formats: {response.json()['supported_formats']}")

# 3. Parse single resume
with open('resume.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post(f"{BASE_URL}/parse", files=files)
    result = response.json()

    if result['success']:
        data = result['data']
        print(f"Name: {data['contact_information']['name']}")
        print(f"Skills: {data['skills']}")
        print(f"Experience: {len(data['work_experience'])} positions")

# 4. Extract specific section
with open('resume.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post(f"{BASE_URL}/extract/skills", files=files)
    skills = response.json()['data']
    print(f"Extracted Skills: {skills}")
```

## Troubleshooting

### API not responding

- Check if server is running: `curl http://localhost:5000/health`
- Check port 5000 is not in use
- Check firewall settings

### File upload fails

- Verify file format is supported
- Check file size doesn't exceed 50 MB
- Ensure proper file permissions

### Slow processing

- GPU not being used: Check CUDA installation
- Server overloaded: Reduce batch size or add more workers

---

**API Version:** 1.0.0  
**Last Updated:** May 2024
