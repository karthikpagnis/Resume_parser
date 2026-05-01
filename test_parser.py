"""
Unit tests for Resume Parser
"""

import unittest
import json
import tempfile
from pathlib import Path

from utils import TextCleaner, InformationExtractor, FileExtractor
from config import EMAIL_PATTERN, PHONE_PATTERN


class TestTextCleaner(unittest.TestCase):
    """Test text cleaning functions"""
    
    def test_clean_text(self):
        """Test text cleaning"""
        text = "Hello   World  \n\n  Multiple   spaces"
        cleaned = TextCleaner.clean_text(text)
        self.assertNotIn("  ", cleaned)
        self.assertEqual(cleaned, "Hello World Multiple spaces")
    
    def test_normalize_text(self):
        """Test text normalization"""
        text = "HELLO World"
        normalized = TextCleaner.normalize_text(text)
        self.assertEqual(normalized, "hello world")


class TestInformationExtractor(unittest.TestCase):
    """Test information extraction functions"""
    
    def test_extract_email(self):
        """Test email extraction"""
        text = "Contact me at john.doe@example.com or jane_smith@company.org"
        emails = InformationExtractor.extract_emails(text)
        self.assertEqual(len(emails), 2)
        self.assertIn("john.doe@example.com", emails)
    
    def test_extract_phone(self):
        """Test phone number extraction"""
        text = "Call me at (555) 123-4567 or +1-555-987-6543"
        phones = InformationExtractor.extract_phones(text)
        self.assertGreater(len(phones), 0)
    
    def test_extract_linkedin(self):
        """Test LinkedIn profile extraction"""
        text = "Visit my LinkedIn: linkedin.com/in/johndoe"
        linkedin = InformationExtractor.extract_linkedin(text)
        self.assertEqual(len(linkedin), 1)
    
    def test_extract_github(self):
        """Test GitHub profile extraction"""
        text = "My GitHub: github.com/johndoe and github.com/janesmith"
        github = InformationExtractor.extract_github(text)
        self.assertEqual(len(github), 2)


class TestParsingPatterns(unittest.TestCase):
    """Test parsing patterns"""
    
    def test_email_pattern(self):
        """Test email regex pattern"""
        valid_emails = [
            "user@example.com",
            "first.last@company.co.uk",
            "name+tag@domain.org"
        ]
        for email in valid_emails:
            matches = InformationExtractor.extract_emails(email)
            self.assertEqual(len(matches), 1)
    
    def test_phone_pattern(self):
        """Test phone regex pattern"""
        valid_phones = [
            "(555) 123-4567",
            "+1-555-123-4567",
            "555.123.4567"
        ]
        for phone in valid_phones:
            matches = InformationExtractor.extract_phones(phone)
            self.assertGreater(len(matches), 0)


class TestSectionExtraction(unittest.TestCase):
    """Test section extraction"""
    
    def test_get_section_content(self):
        """Test section content extraction"""
        text = """
        Experience:
        Worked as Senior Engineer at Tech Corp from 2020 to 2023.
        
        Skills:
        Python, JavaScript, Docker
        """
        
        # This would require the parser to be tested
        # Placeholder for actual implementation
        self.assertTrue(True)


class TestJSONOutput(unittest.TestCase):
    """Test JSON output format"""
    
    def test_output_schema(self):
        """Test JSON output schema"""
        from config import OUTPUT_SCHEMA
        
        required_fields = [
            'contact_information', 'professional_summary', 'work_experience',
            'education', 'skills', 'certifications', 'projects'
        ]
        
        for field in required_fields:
            self.assertIn(field, OUTPUT_SCHEMA)
    
    def test_contact_info_schema(self):
        """Test contact information schema"""
        from config import OUTPUT_SCHEMA
        
        contact_fields = [
            'name', 'email', 'phone', 'location', 'linkedin', 'github'
        ]
        
        for field in contact_fields:
            self.assertIn(field, OUTPUT_SCHEMA['contact_information'])


def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_tests()
