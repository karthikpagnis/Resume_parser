"""Configuration settings for Resume Parser"""

# Model Configuration
MODEL_NAME = "distilbert-base-uncased"  # Using DistilBERT for efficiency
NER_MODEL = "dbmdz/bert-base-cased-finetuned-conll03-english"

# Supported file formats
SUPPORTED_FORMATS = ['.pdf', '.docx', '.doc', '.docs']

# NER Tags of interest
NER_TAGS = {
    'PER': 'PERSON',
    'ORG': 'ORGANIZATION',
    'MISC': 'MISCELLANEOUS',
    'LOC': 'LOCATION'
}

# Regex patterns for information extraction
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
PHONE_PATTERN = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
LINKEDIN_PATTERN = r'linkedin\.com/in/[\w-]+'
GITHUB_PATTERN = r'github\.com/[\w-]+'

# JSON Output fields
OUTPUT_SCHEMA = {
    'contact_information': {
        'name': '',
        'email': '',
        'phone': '',
        'location': '',
        'linkedin': '',
        'github': ''
    },
    'professional_summary': '',
    'work_experience': [],
    'education': [],
    'skills': [],
    'certifications': [],
    'projects': []
}
