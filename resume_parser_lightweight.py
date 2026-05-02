"""
Lightweight Resume Parser - No Transformer Models
Uses regex, spaCy NLP, and heuristics instead of transformer models
"""

import os
os.environ['OPENBLAS_CORETYPE'] = 'NEHALEM'
os.environ['OMP_NUM_THREADS'] = '1'

import json
import re
from typing import Dict, List
from pathlib import Path

from utils import FileExtractor, InformationExtractor, TextCleaner, save_json_output
from config import OUTPUT_SCHEMA

# Optional: spaCy (much lighter than transformers)
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except:
    SPACY_AVAILABLE = False
    print("Warning: spaCy not available, using regex-only extraction")


class LightweightResumeParser:
    """Resume Parser without heavy transformer models - CPU compatible"""
    
    def __init__(self):
        """Initialize with lightweight utilities only"""
        self.text_cleaner = TextCleaner()
        self.info_extractor = InformationExtractor()
        self.spacy_available = SPACY_AVAILABLE
    
    def parse_resume(self, file_path: str) -> Dict:
        """Parse resume file with lightweight methods"""
        
        # Validate file format
        if not self._validate_file_format(file_path):
            raise ValueError(f"Unsupported file format")
        
        # Extract text
        print(f"Extracting text from {file_path}...")
        raw_text = FileExtractor.extract_text(file_path)
        cleaned_text = self.text_cleaner.clean_text(raw_text)
        
        # Initialize output
        output = OUTPUT_SCHEMA.copy()
        
        # Extract information
        print("Extracting contact information...")
        output['contact_information'] = self._extract_contact_info(raw_text, cleaned_text)
        
        print("Extracting professional summary...")
        output['professional_summary'] = self._extract_professional_summary(cleaned_text)
        
        print("Extracting work experience...")
        output['work_experience'] = self._extract_work_experience(cleaned_text)
        
        print("Extracting education...")
        output['education'] = self._extract_education(cleaned_text)
        
        print("Extracting skills...")
        output['skills'] = self._extract_skills(cleaned_text)
        
        print("Extracting certifications...")
        output['certifications'] = self._extract_certifications(cleaned_text)
        
        print("Extracting projects...")
        output['projects'] = self._extract_projects(cleaned_text)
        
        return output
    
    def _validate_file_format(self, file_path: str) -> bool:
        """Validate file format"""
        return Path(file_path).suffix.lower() in ['.pdf', '.docx', '.doc', '.docs']
    
    def _extract_contact_info(self, raw_text: str, cleaned_text: str) -> Dict:
        """Extract contact information using regex and spaCy"""
        contact = {
            'name': '',
            'email': '',
            'phone': '',
            'location': '',
            'linkedin': '',
            'github': ''
        }
        
        # Emails
        emails = self.info_extractor.extract_emails(raw_text)
        if emails:
            contact['email'] = emails[0]
        
        # Phones
        phones = self.info_extractor.extract_phones(raw_text)
        if phones:
            contact['phone'] = phones[0]
        
        # LinkedIn
        linkedin = self.info_extractor.extract_linkedin(raw_text)
        if linkedin:
            contact['linkedin'] = linkedin[0]
        
        # GitHub
        github = self.info_extractor.extract_github(raw_text)
        if github:
            contact['github'] = github[0]
        
        # Extract name and location using spaCy if available
        if self.spacy_available:
            try:
                doc = nlp(raw_text[:2000])  # Only process first 2000 chars for speed
                for ent in doc.ents:
                    if ent.label_ == 'PERSON' and not contact['name']:
                        contact['name'] = ent.text
                    elif ent.label_ == 'GPE' and not contact['location']:
                        contact['location'] = ent.text
            except:
                pass
        
        # Fallback: Try to extract name from first line
        if not contact['name']:
            first_line = raw_text.split('\n')[0].strip()
            if first_line and len(first_line) < 100:
                contact['name'] = first_line
        
        return contact
    
    def _extract_professional_summary(self, text: str) -> str:
        """Extract professional summary"""
        keywords = ['summary', 'objective', 'overview', 'professional profile', 'about']
        
        for keyword in keywords:
            pattern = rf'{keyword}[:\-]?\s*(.{{0,500}}?)(?=\n\n|\n[A-Z]|$)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                summary = match.group(1).strip()
                if summary and len(summary) > 10:
                    return summary[:500]
        
        return ""
    
    def _extract_work_experience(self, text: str) -> List[Dict]:
        """Extract work experience"""
        experience = []
        
        keywords = ['work experience', 'employment', 'experience', 'professional history']
        work_section = self._get_section(text, keywords)
        
        if not work_section:
            return experience
        
        # Split entries by common patterns
        entries = re.split(r'\n(?=[A-Z][A-Za-z\s,\.]+(?:\||–|—|,)?)', work_section)
        
        for entry in entries[:10]:
            if len(entry) < 10:
                continue
            
            lines = entry.strip().split('\n')
            exp = {
                'company': '',
                'position': '',
                'duration': '',
                'description': ''
            }
            
            if lines:
                first_line = lines[0]
                if '|' in first_line or '–' in first_line or '—' in first_line:
                    parts = re.split(r'\s*[\|–—]\s*', first_line)
                    exp['company'] = parts[0].strip()
                    exp['position'] = parts[1].strip() if len(parts) > 1 else ''
                else:
                    exp['company'] = first_line.strip()
            
            # Extract duration
            duration_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}.*?(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|present|current))', 
                                     entry, re.IGNORECASE)
            if duration_match:
                exp['duration'] = duration_match.group(1)
            
            if len(lines) > 1:
                exp['description'] = '\n'.join(lines[1:])[:300]
            
            if exp['company'] or exp['position']:
                experience.append(exp)
        
        return experience
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education"""
        education = []
        
        keywords = ['education', 'academic', 'degree', 'university', 'college']
        edu_section = self._get_section(text, keywords)
        
        if not edu_section:
            return education
        
        entries = re.split(r'\n(?=[A-Z][A-Za-z\s,\.]+(?:\(|,)?)', edu_section)
        
        for entry in entries[:10]:
            if len(entry) < 10:
                continue
            
            edu = {
                'institution': '',
                'degree': '',
                'field_of_study': '',
                'graduation_year': ''
            }
            
            lines = entry.strip().split('\n')
            if lines:
                edu['institution'] = lines[0].strip()
            
            # Degree
            degree_match = re.search(r'(B\.?S\.?|B\.?A\.?|M\.?S\.?|M\.?A\.?|Ph\.?D\.?|Bachelor|Master|Doctorate)', 
                                    entry, re.IGNORECASE)
            if degree_match:
                edu['degree'] = degree_match.group(1)
            
            # Year
            year_match = re.search(r'(\d{4})', entry)
            if year_match:
                edu['graduation_year'] = year_match.group(1)
            
            if len(lines) > 1:
                edu['field_of_study'] = lines[1].strip()
            
            if edu['institution'] or edu['degree']:
                education.append(edu)
        
        return education
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills"""
        skills = []
        
        keywords = ['skills', 'technical skills', 'core competencies', 'expertise']
        skills_section = self._get_section(text, keywords)
        
        if skills_section:
            skill_items = re.split(r'[,•\-\n]', skills_section)
            
            for skill in skill_items[:30]:
                skill = skill.strip()
                if skill and len(skill) > 2 and len(skill) < 100:
                    skill = re.sub(r'\([^)]*\)', '', skill).strip()
                    if skill:
                        skills.append(skill)
        
        # Remove duplicates
        seen = set()
        unique_skills = []
        for skill in skills:
            if skill.lower() not in seen:
                seen.add(skill.lower())
                unique_skills.append(skill)
        
        return unique_skills[:30]
    
    def _extract_certifications(self, text: str) -> List[Dict]:
        """Extract certifications"""
        certs = []
        
        keywords = ['certifications', 'certificates', 'certified']
        cert_section = self._get_section(text, keywords)
        
        if cert_section:
            entries = re.split(r'\n(?=[A-Z])', cert_section)
            
            for entry in entries[:15]:
                if len(entry) < 5:
                    continue
                
                lines = entry.strip().split('\n')
                if lines:
                    cert = {
                        'name': lines[0].strip(),
                        'issuer': '',
                        'date': ''
                    }
                    
                    year_match = re.search(r'(\d{4})', entry)
                    if year_match:
                        cert['date'] = year_match.group(1)
                    
                    certs.append(cert)
        
        return certs
    
    def _extract_projects(self, text: str) -> List[Dict]:
        """Extract projects"""
        projects = []
        
        keywords = ['projects', 'portfolio', 'notable projects']
        project_section = self._get_section(text, keywords)
        
        if project_section:
            entries = re.split(r'\n(?=[A-Z][a-zA-Z\s]+[\-:])', project_section)
            
            for entry in entries[:10]:
                if len(entry) < 10:
                    continue
                
                lines = entry.strip().split('\n')
                project = {
                    'title': '',
                    'description': '',
                    'technologies': []
                }
                
                if lines:
                    project['title'] = lines[0].strip()
                
                if len(lines) > 1:
                    project['description'] = '\n'.join(lines[1:3]).strip()[:300]
                
                if project['title']:
                    projects.append(project)
        
        return projects
    
    def _get_section(self, text: str, keywords: List[str]) -> str:
        """Extract section text"""
        for keyword in keywords:
            pattern = rf'(?:^|\n)({keyword})[:\-]?\s*\n(.*?)(?=\n(?:[A-Z][A-Za-z\s]+[:\-]|$))'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(2).strip()
        return ""


def main():
    """Main function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python resume_parser_lightweight.py <file_path> [output_json]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "parsed_resume.json"
    
    try:
        parser = LightweightResumeParser()
        print(f"Parsing: {file_path}")
        
        data = parser.parse_resume(file_path)
        save_json_output(data, output_file)
        
        print(f"\n✓ Parsing complete!")
        print(f"Output saved to: {output_file}")
        print(json.dumps(data, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
