"""
Main entry point for Resume Parser application
Provides both CLI and programmatic interfaces
"""

# Disable AVX/MKL instructions for CPU compatibility
import os
os.environ['OPENBLAS_CORETYPE'] = 'NEHALEM'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_THREADING_LAYER'] = 'GNU'
os.environ['TORCH_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Optional

from resume_parser import ResumeParser
from utils import save_json_output, load_json_output


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Resume Parser using Transformer Models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py resume.pdf
  python main.py resume.docx -o parsed_output.json
  python main.py resume.pdf -o output.json -v
        """
    )
    
    parser.add_argument(
        'resume_file',
        help='Path to resume file (PDF, DOCX, or DOC format)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='parsed_resume.json',
        help='Output JSON file path (default: parsed_resume.json)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty print JSON output to console'
    )
    
    return parser.parse_args()


def validate_input_file(file_path: str) -> bool:
    """Validate input file exists and has supported format"""
    path = Path(file_path)
    
    if not path.exists():
        print(f"Error: File '{file_path}' not found")
        return False
    
    supported_formats = ['.pdf', '.docx', '.doc', '.docs']
    if path.suffix.lower() not in supported_formats:
        print(f"Error: Unsupported file format '{path.suffix}'")
        print(f"Supported formats: {', '.join(supported_formats)}")
        return False
    
    return True


def print_summary(parsed_data: Dict, verbose: bool = False):
    """Print summary of parsed data"""
    print("\n" + "="*60)
    print("PARSING COMPLETE - SUMMARY")
    print("="*60)
    
    contact = parsed_data.get('contact_information', {})
    print(f"\nContact Information:")
    print(f"  Name: {contact.get('name', 'N/A')}")
    print(f"  Email: {contact.get('email', 'N/A')}")
    print(f"  Phone: {contact.get('phone', 'N/A')}")
    print(f"  Location: {contact.get('location', 'N/A')}")
    
    if contact.get('linkedin'):
        print(f"  LinkedIn: {contact.get('linkedin')}")
    if contact.get('github'):
        print(f"  GitHub: {contact.get('github')}")
    
    print(f"\nProfessional Summary:")
    summary = parsed_data.get('professional_summary', '')
    if summary:
        print(f"  {summary[:200]}...")
    else:
        print("  N/A")
    
    work_exp = parsed_data.get('work_experience', [])
    print(f"\nWork Experience: {len(work_exp)} entries")
    for i, exp in enumerate(work_exp[:3], 1):
        print(f"  {i}. {exp.get('company', 'N/A')} - {exp.get('position', 'N/A')}")
    if len(work_exp) > 3:
        print(f"  ... and {len(work_exp) - 3} more")
    
    education = parsed_data.get('education', [])
    print(f"\nEducation: {len(education)} entries")
    for i, edu in enumerate(education[:3], 1):
        print(f"  {i}. {edu.get('degree', 'N/A')} - {edu.get('institution', 'N/A')}")
    if len(education) > 3:
        print(f"  ... and {len(education) - 3} more")
    
    skills = parsed_data.get('skills', [])
    print(f"\nSkills: {len(skills)} identified")
    if skills:
        print(f"  {', '.join(skills[:10])}")
        if len(skills) > 10:
            print(f"  ... and {len(skills) - 10} more")
    
    certs = parsed_data.get('certifications', [])
    print(f"\nCertifications: {len(certs)} entries")
    
    projects = parsed_data.get('projects', [])
    print(f"\nProjects: {len(projects)} entries")
    
    print("\n" + "="*60)


def main():
    """Main application entry point"""
    args = parse_arguments()
    
    # Validate input file
    if not validate_input_file(args.resume_file):
        sys.exit(1)
    
    try:
        # Initialize parser
        if args.verbose:
            print(f"Initializing Resume Parser...")
            print(f"Input file: {args.resume_file}")
            print(f"Output file: {args.output}")
        
        parser = ResumeParser()
        
        # Parse resume
        if args.verbose:
            print(f"\nStarting parse process...")
        
        parsed_data = parser.parse_resume(args.resume_file)
        
        # Save results
        save_json_output(parsed_data, args.output)
        
        if args.verbose:
            print(f"Results saved to: {args.output}")
        
        # Print summary
        print_summary(parsed_data, verbose=args.verbose)
        
        # Pretty print if requested
        if args.pretty:
            print("\n" + "="*60)
            print("FULL JSON OUTPUT")
            print("="*60)
            print(json.dumps(parsed_data, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
