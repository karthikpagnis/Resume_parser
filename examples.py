"""
Example usage of Resume Parser
Demonstrates various ways to use the parser
"""

import json
from pathlib import Path
from resume_parser import ResumeParser
from utils import save_json_output, load_json_output


def example_1_single_resume():
    """Example 1: Parse a single resume"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Parse Single Resume")
    print("="*60)
    
    parser = ResumeParser()
    
    # You would replace this with your actual resume file
    resume_file = "sample_resume.pdf"  # or .docx, .doc
    
    try:
        print(f"Parsing resume: {resume_file}")
        parsed_data = parser.parse_resume(resume_file)
        
        # Display extracted information
        print("\nExtracted Information:")
        print(f"Name: {parsed_data['contact_information']['name']}")
        print(f"Email: {parsed_data['contact_information']['email']}")
        print(f"Phone: {parsed_data['contact_information']['phone']}")
        
        print(f"\nSkills: {', '.join(parsed_data['skills'][:5])}")
        print(f"Work Experience: {len(parsed_data['work_experience'])} entries")
        print(f"Education: {len(parsed_data['education'])} entries")
        
        # Save to JSON
        save_json_output(parsed_data, "example_output_1.json")
        print("\nOutput saved to: example_output_1.json")
        
    except FileNotFoundError:
        print(f"Resume file not found: {resume_file}")


def example_2_access_specific_fields():
    """Example 2: Access specific extracted fields"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Access Specific Fields")
    print("="*60)
    
    # Assuming you already have parsed data
    parsed_data = {
        "contact_information": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1-555-123-4567"
        },
        "work_experience": [
            {
                "company": "Tech Corp",
                "position": "Senior Engineer",
                "duration": "2020-2024"
            }
        ],
        "skills": ["Python", "JavaScript", "React"]
    }
    
    # Access contact information
    contact = parsed_data['contact_information']
    print(f"Candidate: {contact['name']}")
    print(f"Email: {contact['email']}")
    
    # Access work experience
    for i, job in enumerate(parsed_data['work_experience'], 1):
        print(f"\nJob {i}: {job['position']} at {job['company']}")
    
    # Access skills
    print(f"\nSkills: {', '.join(parsed_data['skills'])}")


def example_3_batch_processing():
    """Example 3: Batch process multiple resumes"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Batch Process Multiple Resumes")
    print("="*60)
    
    parser = ResumeParser()
    resume_dir = Path("resumes")  # Directory containing resume files
    
    if not resume_dir.exists():
        print(f"Create a '{resume_dir}' directory with resume files to test batch processing")
        return
    
    # Process all PDF files in directory
    resumes = list(resume_dir.glob("*.pdf")) + list(resume_dir.glob("*.docx"))
    
    if not resumes:
        print(f"No resume files found in {resume_dir}")
        return
    
    results = []
    
    for i, resume_file in enumerate(resumes, 1):
        print(f"\n[{i}/{len(resumes)}] Processing: {resume_file.name}")
        
        try:
            parsed_data = parser.parse_resume(str(resume_file))
            results.append({
                "filename": resume_file.name,
                "candidate_name": parsed_data['contact_information']['name'],
                "email": parsed_data['contact_information']['email'],
                "skills_count": len(parsed_data['skills']),
                "experience_count": len(parsed_data['work_experience']),
                "data": parsed_data
            })
            print(f"  ✓ Success")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Save batch results
    output_file = "batch_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\nBatch processing complete!")
    print(f"Processed: {len(results)} resumes")
    print(f"Results saved to: {output_file}")
    
    # Print summary
    print("\nSummary:")
    for result in results:
        print(f"  {result['filename']}: {result['candidate_name']}")


def example_4_filter_and_search():
    """Example 4: Filter candidates by criteria"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Filter and Search Candidates")
    print("="*60)
    
    # Load batch results
    results_file = "batch_results.json"
    
    try:
        with open(results_file, 'r') as f:
            candidates = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {results_file}")
        print("Please run Example 3 first to generate batch results")
        return
    
    # Filter by skill
    target_skill = "Python"
    python_developers = []
    
    for candidate in candidates:
        skills = candidate['data']['skills']
        if any(target_skill.lower() in skill.lower() for skill in skills):
            python_developers.append(candidate)
    
    print(f"\nCandidates with {target_skill} skill: {len(python_developers)}")
    for candidate in python_developers:
        print(f"  - {candidate['candidate_name']} ({candidate['email']})")
    
    # Filter by experience level
    print("\nCandidates with 3+ years experience:")
    experienced = [c for c in candidates if c['experience_count'] >= 3]
    for candidate in experienced:
        print(f"  - {candidate['candidate_name']}: {candidate['experience_count']} positions")


def example_5_json_validation():
    """Example 5: Validate and inspect JSON output"""
    print("\n" + "="*60)
    print("EXAMPLE 5: JSON Output Validation")
    print("="*60)
    
    # Example parsed output structure
    sample_output = {
        "contact_information": {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "phone": "+1-555-987-6543",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/janesmith",
            "github": "github.com/janesmith"
        },
        "professional_summary": "Full-stack developer with 5+ years experience...",
        "work_experience": [
            {
                "company": "Startup Inc",
                "position": "Full Stack Developer",
                "duration": "2022-Present",
                "description": "Developed microservices using Python and Node.js..."
            }
        ],
        "education": [
            {
                "institution": "State University",
                "degree": "B.S.",
                "field_of_study": "Computer Science",
                "graduation_year": "2019"
            }
        ],
        "skills": ["Python", "JavaScript", "React", "Docker"],
        "certifications": [],
        "projects": []
    }
    
    # Validate structure
    required_fields = [
        'contact_information', 'professional_summary', 'work_experience',
        'education', 'skills', 'certifications', 'projects'
    ]
    
    print("Validating JSON structure...")
    all_valid = True
    for field in required_fields:
        if field in sample_output:
            print(f"  ✓ {field}")
        else:
            print(f"  ✗ {field} (MISSING)")
            all_valid = False
    
    if all_valid:
        print("\n✓ JSON structure is valid!")
        print(f"Output saved to: sample_output.json")
        save_json_output(sample_output, "sample_output.json")


def main():
    """Run all examples"""
    print("\n" + "#"*60)
    print("# Resume Parser - Usage Examples")
    print("#"*60)
    
    print("""
This script demonstrates different ways to use the Resume Parser:

1. Parse a single resume
2. Access specific extracted fields
3. Batch process multiple resumes
4. Filter and search candidates
5. JSON output validation

Note: Some examples require sample resume files.
    """)
    
    # Uncomment the examples you want to run:
    
    # example_1_single_resume()
    example_2_access_specific_fields()
    # example_3_batch_processing()
    # example_4_filter_and_search()
    example_5_json_validation()
    
    print("\n" + "#"*60)
    print("# Examples complete!")
    print("#"*60 + "\n")


if __name__ == "__main__":
    main()
