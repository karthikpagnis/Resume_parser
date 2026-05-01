# Setup Guide for Resume Parser

## Quick Start (5 minutes)

### 1. Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- 4GB RAM minimum (8GB recommended)
- 2GB disk space for models

### 2. Installation Steps

**Step 1: Clone the repository**
```bash
git clone <repository-url>
cd Resume_parser
```

**Step 2: Create a virtual environment**
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

**Step 3: Install dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Step 4: Download NLP models (optional but recommended)**
```bash
python -m spacy download en_core_web_sm
```

### 3. Test Installation

**Test with a single resume:**
```bash
# Create a test resume file first, then:
python main.py your_resume.pdf -v

# If successful, you should see:
# - Parsing progress messages
# - Summary of extracted information
# - parsed_resume.json file created
```

## Detailed Setup Options

### Option A: Minimal Installation (Fast)
For quick testing without GPU support:

```bash
pip install -r requirements.txt
```

### Option B: GPU Support (Recommended for large batches)

**Install PyTorch with CUDA:**
```bash
# For NVIDIA GPU with CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For NVIDIA GPU with CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**Then install other requirements:**
```bash
pip install -r requirements.txt
```

### Option C: Development Setup

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Usage Examples

### CLI Usage

**1. Parse a single resume:**
```bash
python main.py resume.pdf
```

**2. Parse with custom output:**
```bash
python main.py resume.pdf -o output/result.json -v
```

**3. Pretty print output:**
```bash
python main.py resume.pdf --pretty
```

**4. Batch processing:**
```bash
python batch_processor.py ./resumes_directory -o ./output_directory -v
```

### Python API Usage

```python
from resume_parser import ResumeParser

# Initialize
parser = ResumeParser()

# Parse resume
data = parser.parse_resume("resume.pdf")

# Access data
print(data['contact_information'])
print(data['skills'])
```

### REST API Usage

**1. Start the Flask server:**
```bash
pip install flask flask-cors
python app.py
```

**2. Parse via HTTP:**
```bash
# Single file upload
curl -X POST -F "file=@resume.pdf" http://localhost:5000/parse

# Batch upload
curl -X POST -F "files=@resume1.pdf" -F "files=@resume2.pdf" http://localhost:5000/parse/batch

# Extract specific section
curl -X POST -F "file=@resume.pdf" http://localhost:5000/extract/skills
```

**3. Check API health:**
```bash
curl http://localhost:5000/health
```

## Troubleshooting

### Issue 1: ModuleNotFoundError

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall requirements
pip install -r requirements.txt
```

### Issue 2: Model Download Errors

**Solution:**
```bash
# Clear cache
rm -rf ~/.cache/huggingface/transformers/

# Set offline mode off
export HF_HUB_OFFLINE=0

# Reinstall transformers
pip install --upgrade transformers
```

### Issue 3: PDF Parsing Errors

**Solution:**
```bash
# Update PyPDF2
pip install --upgrade PyPDF2

# Try converting PDF to DOCX first using online tools
# Then parse the DOCX file
```

### Issue 4: Out of Memory

**Solution:**
- Run on a machine with more RAM (8GB+)
- Process resumes one at a time instead of batch
- Use a smaller model variant

### Issue 5: Slow Processing

**Solution:**
```bash
# Use GPU if available
pip install torch --index-url https://download.pytorch.org/whl/cu121

# Check GPU usage
python -c "import torch; print(torch.cuda.is_available())"
```

## File Format Specific Instructions

### PDF Files
- Works with most PDF formats
- Scanned PDFs may have lower accuracy
- Solution: Convert scanned PDF to DOCX for better results

### DOCX Files
- Fully supported
- Works with tables and formatting
- Recommended format for best accuracy

### DOC Files
- Supported on all platforms
- May require additional system libraries on Linux
- Fallback: Convert to DOCX format

## Environment Variables

Optional configuration via environment variables:

```bash
# Disable GPU
export CUDA_VISIBLE_DEVICES=""

# Set cache directory
export HF_HOME=/path/to/cache

# Enable debug logging
export DEBUG=1
```

## Running Tests

```bash
# Run unit tests
python -m pytest test_parser.py -v

# Or using unittest
python test_parser.py
```

## Performance Optimization

### For Single Resume Processing
- Expected time: 30-60 seconds
- Memory: 4GB

### For Batch Processing (10+ resumes)
```bash
# Use batch processor for best performance
python batch_processor.py ./resumes -o ./output -v
```

### For API Deployment
```bash
# Install production server
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Docker Setup (Advanced)

**Build Docker image:**
```bash
docker build -t resume-parser .
```

**Run container:**
```bash
docker run -v /path/to/resumes:/app/resumes \
           -v /path/to/output:/app/output \
           resume-parser python main.py /app/resumes/resume.pdf
```

## Next Steps

1. **Read the README.md** for detailed feature documentation
2. **Check examples.py** for usage examples
3. **Review config.py** to customize extraction patterns
4. **Start parsing resumes!**

## Getting Help

- Check README.md for comprehensive documentation
- Review examples.py for sample code
- Check GitHub issues for common problems
- Run with `-v` flag for verbose output and debugging info

## Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed without errors
- [ ] NLP models downloaded successfully
- [ ] Sample resume parsed successfully
- [ ] JSON output generated correctly

---

**Setup Complete!** You're ready to parse resumes. Start with:
```bash
python main.py your_resume.pdf -v
```
