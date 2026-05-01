# Project Structure and Files

## Core Application Files

### 1. **main.py** - Main Entry Point

- CLI interface for parsing resumes
- Argument parsing (verbose mode, output file, pretty printing)
- Summary printing functionality
- Best for: Command-line usage

### 2. **resume_parser.py** - Core Parser Implementation

- `ResumeParser` class with transformer models
- Information extraction methods for all sections
- NER-based entity recognition
- Section extraction and pattern matching
- Best for: Direct Python API usage

### 3. **config.py** - Configuration Settings

- Model names and paths
- Supported file formats
- Regex patterns for information extraction
- Output schema definition
- Best for: Customizing extraction behavior

### 4. **utils.py** - Utility Functions

- `FileExtractor` class for multi-format file reading
- `InformationExtractor` class for pattern-based extraction
- `TextCleaner` class for text normalization
- File I/O utilities
- Best for: File handling and text processing

## CLI Tools

### 5. **batch_processor.py** - Batch Processing Script

- Process multiple resumes from a directory
- Generate summary reports
- Statistics calculation
- Error handling and reporting
- Usage: `python batch_processor.py ./resumes -o ./output`

### 6. **examples.py** - Usage Examples

- 5 comprehensive examples of API usage
- Batch processing examples
- Filtering and searching examples
- JSON validation examples
- Usage: `python examples.py`

## Web API

### 7. **app.py** - Flask REST API

- HTTP endpoints for resume parsing
- Single file and batch upload support
- Section-specific extraction endpoints
- Health check and info endpoints
- Usage: `python app.py` (runs on port 5000)

## Testing

### 8. **test_parser.py** - Unit Tests

- Text cleaning tests
- Information extraction tests
- Pattern matching tests
- JSON output validation
- Usage: `python test_parser.py` or `pytest test_parser.py`

## Configuration Files

### 9. **requirements.txt** - Main Dependencies

- Core packages: transformers, torch, spacy, nltk
- File parsing: python-docx, PyPDF2
- Data processing: pandas, numpy, scikit-learn

### 10. **requirements-dev.txt** - Development Dependencies

- Testing: pytest, coverage
- Code quality: black, flake8, pylint
- Documentation: sphinx
- API: flask, gunicorn
- Performance: memory-profiler

### 11. **.env.example** - Environment Configuration Template

- Model configuration options
- File processing settings
- API settings
- Performance tuning options
- Copy to `.env` and modify as needed

### 12. **.gitignore** - Git Ignore Rules

- Excludes Python cache, virtual environments
- Ignores model files and outputs
- Excludes IDE files and temporary files

## Docker Files

### 13. **Dockerfile** - Container Image Definition

- Python 3.10 slim base image
- Installs dependencies
- Sets up application environment
- Health check configuration
- Usage: `docker build -t resume-parser .`

### 14. **docker-compose.yml** - Docker Compose Configuration

- Container orchestration
- Volume management
- Port mapping
- Health checks
- Usage: `docker-compose up`

## Documentation

### 15. **README.md** - Main Documentation

- Project overview
- Installation instructions
- Usage examples (CLI, Python API, REST API)
- Feature list
- Output format specification
- Troubleshooting guide
- Performance metrics

### 16. **SETUP.md** - Setup Guide

- Quick start (5 minutes)
- Detailed setup options
- Installation troubleshooting
- File format specific instructions
- Performance optimization tips
- Docker setup guide

### 17. **API_DOCUMENTATION.md** - API Reference

- Complete REST API documentation
- Endpoint specifications
- Request/response examples
- Error handling guide
- Code examples in cURL and Python

### 18. **PROJECT_STRUCTURE.md** - This File

- Lists all project files
- Describes file purposes
- Provides quick reference

## Complete Directory Structure

```
Resume_parser/
├── main.py                      # CLI entry point
├── resume_parser.py             # Core parser with transformer models
├── config.py                    # Configuration settings
├── utils.py                     # Utility functions
├── batch_processor.py           # Batch processing script
├── examples.py                  # Usage examples
├── app.py                       # Flask REST API
├── test_parser.py              # Unit tests
│
├── requirements.txt             # Core dependencies
├── requirements-dev.txt         # Development dependencies
├── .env.example                # Environment configuration template
├── .gitignore                  # Git ignore rules
│
├── Dockerfile                  # Docker container definition
├── docker-compose.yml          # Docker Compose configuration
│
├── README.md                   # Main documentation
├── SETUP.md                    # Setup guide
├── API_DOCUMENTATION.md        # REST API documentation
├── PROJECT_STRUCTURE.md        # This file
│
├── .git/                       # Git repository
└── Navtech_Python_with_ML_Coding_Assessment.pdf  # Assignment PDF
```

## Quick Reference

### To Parse a Single Resume

```bash
python main.py resume.pdf -o output.json -v
```

### To Batch Process Resumes

```bash
python batch_processor.py ./resumes -o ./output -v
```

### To Run REST API

```bash
python app.py
# Then: curl -X POST -F "file=@resume.pdf" http://localhost:5000/parse
```

### To Run Tests

```bash
python test_parser.py
```

### To Use in Python Code

```python
from resume_parser import ResumeParser
parser = ResumeParser()
data = parser.parse_resume("resume.pdf")
```

## Feature Summary

✅ **File Format Support**

- PDF, DOCX, DOC, DOCS

✅ **Information Extraction**

- Contact information
- Professional summary
- Work experience
- Education
- Skills
- Certifications
- Projects

✅ **Transformer Model Integration**

- BERT-based NER
- Zero-shot classification
- Named Entity Recognition
- Text understanding

✅ **Output Formats**

- JSON structured output
- CLI with formatting
- REST API endpoints
- Python API

✅ **Deployment Options**

- CLI tool
- Python library
- REST API (Flask)
- Docker containerization
- Batch processing

---

**Total Files Created:** 18  
**Project Status:** Production Ready  
**Last Updated:** May 2024
