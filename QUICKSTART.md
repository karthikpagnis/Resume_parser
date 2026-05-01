# Quick Start Guide

## 30-Second Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Parse your first resume
python main.py your_resume.pdf
```

That's it! Your parsed data will be in `parsed_resume.json`

---

## Common Tasks

### Parse a single resume

```bash
python main.py resume.pdf -o output.json
```

### Parse with verbose output

```bash
python main.py resume.pdf -v --pretty
```

### Parse multiple resumes (batch)

```bash
python batch_processor.py ./resumes_folder -o ./output_folder
```

### Start REST API server

```bash
python app.py
# API available at http://localhost:5000
```

### Use in Python code

```python
from resume_parser import ResumeParser

parser = ResumeParser()
data = parser.parse_resume("resume.pdf")

# Access data
print(data['contact_information']['name'])
print(data['skills'])
print(data['work_experience'])
```

### Using REST API

```bash
# Upload and parse
curl -X POST -F "file=@resume.pdf" http://localhost:5000/parse

# Extract skills only
curl -X POST -F "file=@resume.pdf" http://localhost:5000/extract/skills

# Batch upload
curl -X POST -F "files=@resume1.pdf" -F "files=@resume2.pdf" \
  http://localhost:5000/parse/batch
```

---

## Docker Usage

```bash
# Build image
docker build -t resume-parser .

# Run container
docker run -v $(pwd)/uploads:/app/uploads resume-parser

# Or use Docker Compose
docker-compose up
```

---

## Output Format

```json
{
  "contact_information": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-123-4567",
    "location": "NYC",
    "linkedin": "linkedin.com/in/johndoe",
    "github": "github.com/johndoe"
  },
  "professional_summary": "...",
  "work_experience": [
    {
      "company": "Tech Corp",
      "position": "Senior Engineer",
      "duration": "2020-2024",
      "description": "..."
    }
  ],
  "education": [
    {
      "institution": "MIT",
      "degree": "B.S.",
      "field_of_study": "Computer Science",
      "graduation_year": "2018"
    }
  ],
  "skills": ["Python", "JavaScript", "React", ...],
  "certifications": [...],
  "projects": [...]
}
```

---

## File Support

- ✅ PDF files (.pdf)
- ✅ Microsoft Word (.docx)
- ✅ Microsoft Word (.doc, .docs)

---

## Supported Information

- Contact: Name, Email, Phone, Location, LinkedIn, GitHub
- Summary: Professional objective/summary
- Experience: Company, Position, Duration, Description
- Education: Institution, Degree, Field, Graduation Year
- Skills: Technical and professional skills
- Certifications: Name, Issuer, Date
- Projects: Title, Description, Technologies

---

## Troubleshooting

**Issue: "No module named 'torch'"**

```bash
pip install -r requirements.txt
```

**Issue: "File not found"**

```bash
# Make sure file is in current directory or use full path
python main.py /full/path/to/resume.pdf
```

**Issue: Slow processing**

- First run downloads models (~2GB) - be patient
- Subsequent runs are faster (~30-60 seconds per resume)
- Use GPU if available for faster processing

**Issue: Out of memory**

- Requires 4GB+ RAM
- Process one resume at a time if memory is limited

---

## Next Steps

1. Read **README.md** for full documentation
2. Check **SETUP.md** for detailed setup options
3. See **API_DOCUMENTATION.md** for API details
4. Explore **examples.py** for code samples

---

## Project Structure

```
Resume_parser/
├── main.py              # CLI tool
├── resume_parser.py     # Core parser
├── app.py              # REST API
├── batch_processor.py  # Batch tool
├── requirements.txt    # Dependencies
├── README.md           # Full docs
└── ... (other files)
```

---

**Ready to parse resumes!** 🚀

Start with: `python main.py your_resume.pdf`
