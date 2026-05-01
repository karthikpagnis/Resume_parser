"""Resume Parser with Transformer Model Integration"""

import json
import re
from typing import Dict, List, Tuple
from pathlib import Path

from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import torch
import numpy as np

from config import (
    MODEL_NAME, NER_MODEL, SUPPORTED_FORMATS, OUTPUT_SCHEMA,
    EMAIL_PATTERN, PHONE_PATTERN, LINKEDIN_PATTERN, GITHUB_PATTERN
)
from utils import (
    FileExtractor, InformationExtractor, TextCleaner,
    save_json_output, load_json_output
)


class ResumeParser:
    """Main Resume Parser using Transformer Models"""
    
    def __init__(self):
        """Initialize parser with transformer models"""
        self.device = 0 if torch.cuda.is_available() else -1
        
        # Initialize NER pipeline
        self.ner_pipeline = pipeline(
            "token-classification",
            model=NER_MODEL,
            aggregation_strategy="simple",
            device=self.device
        )
        
        # Initialize Zero-shot classification pipeline
        self.zero_shot_pipeline = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=self.device
        )
        
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.text_cleaner = TextCleaner()
        self.info_extractor = InformationExtractor()
        
    def parse_resume(self, file_path: str) -> Dict:
        """Parse resume file and extract information"""
        
        # Validate file format
        if not self._validate_file_format(file_path):
            raise ValueError(f"Unsupported file format. Supported: {SUPPORTED_FORMATS}")
        
        # Extract text from file
        print(f"Extracting text from {file_path}...")
        raw_text = FileExtractor.extract_text(file_path)
        
        # Clean text
        cleaned_text = self.text_cleaner.clean_text(raw_text)
        
        # Initialize output structure
        output = OUTPUT_SCHEMA.copy()
        
        # Extract information
        print("Extracting contact information...")
        output['contact_information'] = self._extract_contact_info(raw_text)
        
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
        """Validate if file format is supported"""
        return Path(file_path).suffix.lower() in SUPPORTED_FORMATS
    
    def _extract_contact_info(self, text: str) -> Dict:
        """Extract contact information using regex and NER"""
        contact_info = {
            'name': '',
            'email': '',
            'phone': '',
            'location': '',
            'linkedin': '',
            'github': ''
        }
        
        # Extract emails
        emails = self.info_extractor.extract_emails(text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Extract phones
        phones = self.info_extractor.extract_phones(text)
        if phones:
            contact_info['phone'] = phones[0]
        
        # Extract LinkedIn
        linkedin = self.info_extractor.extract_linkedin(text)
        if linkedin:
            contact_info['linkedin'] = linkedin[0]
        
        # Extract GitHub
        github = self.info_extractor.extract_github(text)
        if github:
            contact_info['github'] = github[0]
        
        # Extract name and location using NER on first few lines
        lines = text.split('\n')[:10]
        first_part = '\n'.join(lines)
        
        try:
            ner_results = self.ner_pipeline(first_part)
            
            for entity in ner_results:
                if entity['entity_group'] == 'PER' and not contact_info['name']:
                    contact_info['name'] = entity['word'].strip()
                elif entity['entity_group'] == 'LOC' and not contact_info['location']:
                    contact_info['location'] = entity['word'].strip()
        except Exception as e:
            print(f"NER extraction error: {e}")
        
        return contact_info
    
    def _extract_professional_summary(self, text: str) -> str:
        """Extract professional summary from resume"""
        summary_keywords = ['summary', 'objective', 'overview', 'professional profile']
        
        for keyword in summary_keywords:
            pattern = rf'{keyword}[:\-]?\s*(.{{0,500}}?)(?=\n\n|\n[A-Z]|$)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                summary = match.group(1).strip()
                if summary:
                    return summary[:500]
        
        # If no section found, use first meaningful paragraph
        sentences = self.info_extractor.extract_sentences(text)
        for sentence in sentences[:3]:
            if len(sentence) > 20:
                return sentence[:500]
        
        return ""
    
    def _extract_work_experience(self, text: str) -> List[Dict]:
        """Extract work experience using NER and patterns"""
        experience = []
        
        work_keywords = ['work experience', 'employment', 'experience', 'professional history']
        
        # Find work experience section
        work_section = self._get_section_text(text, work_keywords)
        
        if not work_section:
            return experience
        
        # Split by common patterns (company name followed by position)
        entries = re.split(r'\n(?=[A-Z][A-Za-z\s,\.]+(?:\||–|—|,)?)', work_section)
        
        for entry in entries[:10]:  # Limit to 10 entries
            if len(entry) < 10:
                continue
            
            lines = entry.strip().split('\n')
            work_exp = {
                'company': '',
                'position': '',
                'duration': '',
                'description': ''
            }
            
            # Try to extract company and position
            if len(lines) > 0:
                first_line = lines[0]
                # Company often appears with position
                if '|' in first_line or '–' in first_line or '—' in first_line:
                    parts = re.split(r'\s*[\|–—]\s*', first_line)
                    work_exp['company'] = parts[0].strip()
                    work_exp['position'] = parts[1].strip() if len(parts) > 1 else ''
                else:
                    work_exp['company'] = first_line.strip()
            
            # Extract duration (dates)
            duration_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}.*?(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|present|current))'
            duration_match = re.search(duration_pattern, entry, re.IGNORECASE)
            if duration_match:
                work_exp['duration'] = duration_match.group(1)
            
            # Description is the rest of the entry
            if len(lines) > 1:
                description = '\n'.join(lines[1:])
                work_exp['description'] = description.strip()[:300]
            
            if work_exp['company'] or work_exp['position']:
                experience.append(work_exp)
        
        return experience
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education information"""
        education = []
        
        education_keywords = ['education', 'academic', 'degree', 'university']
        
        # Find education section
        edu_section = self._get_section_text(text, education_keywords)
        
        if not edu_section:
            return education
        
        # Split by common patterns
        entries = re.split(r'\n(?=[A-Z][A-Za-z\s,\.]+(?:\(|,)?)', edu_section)
        
        for entry in entries[:10]:  # Limit to 10 entries
            if len(entry) < 10:
                continue
            
            edu_entry = {
                'institution': '',
                'degree': '',
                'field_of_study': '',
                'graduation_year': ''
            }
            
            lines = entry.strip().split('\n')
            
            # Institution is usually first line
            if lines:
                edu_entry['institution'] = lines[0].strip()
            
            # Find degree type
            degree_pattern = r'(B\.?S\.?|B\.?A\.?|M\.?S\.?|M\.?A\.?|Ph\.?D\.?|Bachelor|Master|Doctorate)'
            degree_match = re.search(degree_pattern, entry, re.IGNORECASE)
            if degree_match:
                edu_entry['degree'] = degree_match.group(1)
            
            # Extract graduation year
            year_pattern = r'(?:Class of |Graduated?|GPA|20\d{2}|19\d{2}).*?(\d{4})'
            year_match = re.search(year_pattern, entry, re.IGNORECASE)
            if year_match:
                edu_entry['graduation_year'] = year_match.group(1)
            
            # Extract field of study
            if len(lines) > 1:
                edu_entry['field_of_study'] = lines[1].strip()
            
            if edu_entry['institution'] or edu_entry['degree']:
                education.append(edu_entry)
        
        return education
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills using zero-shot classification"""
        skills = []
        
        skill_keywords = ['skills', 'technical skills', 'core competencies', 'expertise', 'programming']
        
        # Find skills section
        skills_section = self._get_section_text(text, skill_keywords)
        
        if skills_section:
            # Split by common delimiters
            skill_items = re.split(r'[,•\-\n]', skills_section)
            
            for skill in skill_items[:30]:  # Limit to 30 skills
                skill = skill.strip()
                if skill and len(skill) > 2:
                    # Clean skill text
                    skill = re.sub(r'\([^)]*\)', '', skill).strip()
                    if skill and len(skill) < 100:
                        skills.append(skill)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in skills:
            if skill.lower() not in seen:
                seen.add(skill.lower())
                unique_skills.append(skill)
        
        return unique_skills[:30]
    
    def _extract_certifications(self, text: str) -> List[Dict]:
        """Extract certifications"""
        certifications = []
        
        cert_keywords = ['certifications', 'certificates', 'certified', 'certifications & licenses']
        
        # Find certifications section
        cert_section = self._get_section_text(text, cert_keywords)
        
        if cert_section:
            # Split by lines and common patterns
            entries = re.split(r'\n(?=[A-Z])', cert_section)
            
            for entry in entries[:15]:  # Limit to 15 certifications
                if len(entry) < 5:
                    continue
                
                lines = entry.strip().split('\n')
                if lines:
                    cert = {
                        'name': lines[0].strip(),
                        'issuer': '',
                        'date': ''
                    }
                    
                    # Look for issuer and date
                    if len(lines) > 1:
                        issuer_match = re.search(r'(?:from|by|issued by|issuer)\s*:?\s*(.+?)(?:\d{4}|$)', 
                                                entry, re.IGNORECASE)
                        if issuer_match:
                            cert['issuer'] = issuer_match.group(1).strip()
                    
                    # Extract year
                    year_match = re.search(r'(\d{4})', entry)
                    if year_match:
                        cert['date'] = year_match.group(1)
                    
                    certifications.append(cert)
        
        return certifications
    
    def _extract_projects(self, text: str) -> List[Dict]:
        """Extract projects"""
        projects = []
        
        project_keywords = ['projects', 'portfolio', 'notable projects', 'key projects']
        
        # Find projects section
        project_section = self._get_section_text(text, project_keywords)
        
        if project_section:
            # Split by lines and common patterns
            entries = re.split(r'\n(?=[A-Z][a-zA-Z\s]+[\-:])', project_section)
            
            for entry in entries[:10]:  # Limit to 10 projects
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
                
                # Description is usually in the first few lines
                if len(lines) > 1:
                    description = '\n'.join(lines[1:3])
                    project['description'] = description.strip()[:300]
                
                # Try to extract technologies
                tech_keywords = ['technologies', 'tools', 'stack', 'built with', 'using']
                for keyword in tech_keywords:
                    tech_match = re.search(rf'{keyword}\s*[:\-]?\s*(.+?)(?:\n|$)', 
                                          entry, re.IGNORECASE)
                    if tech_match:
                        techs = re.split(r'[,•]', tech_match.group(1))
                        project['technologies'] = [t.strip() for t in techs if t.strip()]
                        break
                
                if project['title']:
                    projects.append(project)
        
        return projects
    
    def _get_section_text(self, text: str, section_keywords: List[str]) -> str:
        """Extract text content of a section"""
        for keyword in section_keywords:
            # Pattern to match section header and content until next section
            pattern = rf'(?:^|\n)({keyword})[:\-]?\s*\n(.*?)(?=\n(?:[A-Z][A-Za-z\s]+[:\-]|$))'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(2).strip()
        
        return ""


def main():
    """Main function to demonstrate parser usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python resume_parser.py <resume_file_path> [output_json_path]")
        sys.exit(1)
    
    resume_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "parsed_resume.json"
    
    try:
        parser = ResumeParser()
        print(f"\nParsing resume: {resume_file}")
        
        parsed_data = parser.parse_resume(resume_file)
        
        print(f"\nSaving results to: {output_file}")
        save_json_output(parsed_data, output_file)
        
        print("\nParsing complete!")
        print(json.dumps(parsed_data, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
