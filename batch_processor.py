"""
Batch processing script for Resume Parser
Processes multiple resumes from a directory
"""

import json
import sys
from pathlib import Path
from typing import List, Dict
import argparse
from datetime import datetime

from resume_parser import ResumeParser
from utils import save_json_output


class BatchProcessor:
    """Batch process multiple resumes"""
    
    def __init__(self, verbose: bool = False):
        self.parser = ResumeParser()
        self.verbose = verbose
        self.results = []
        self.errors = []
    
    def process_directory(self, directory: str, output_dir: str = None) -> Dict:
        """Process all resumes in a directory"""
        dir_path = Path(directory)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if output_dir is None:
            output_dir = dir_path / "parsed_output"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find all resume files
        supported_extensions = ['*.pdf', '*.docx', '*.doc', '*.docs']
        resume_files = []
        for ext in supported_extensions:
            resume_files.extend(dir_path.glob(ext))
            resume_files.extend(dir_path.glob(ext.upper()))
        
        if not resume_files:
            print(f"No resume files found in {directory}")
            return {"success": False, "message": "No resume files found"}
        
        print(f"\nFound {len(resume_files)} resume files")
        print(f"Output directory: {output_path}\n")
        
        # Process each file
        for i, resume_file in enumerate(resume_files, 1):
            self._process_file(resume_file, output_path, i, len(resume_files))
        
        # Generate summary report
        summary = self._generate_summary(output_path)
        
        return {
            "success": True,
            "total_processed": len(self.results),
            "total_errors": len(self.errors),
            "output_directory": str(output_path),
            "summary": summary
        }
    
    def _process_file(self, file_path: Path, output_dir: Path, index: int, total: int):
        """Process a single resume file"""
        try:
            file_name = file_path.name
            print(f"[{index}/{total}] Processing: {file_name}...", end=" ", flush=True)
            
            # Parse resume
            parsed_data = self.parser.parse_resume(str(file_path))
            
            # Extract key info
            candidate_name = parsed_data['contact_information'].get('name', 'Unknown')
            
            # Create output filename
            base_name = file_path.stem
            output_file = output_dir / f"{base_name}_parsed.json"
            
            # Save to file
            save_json_output(parsed_data, str(output_file))
            
            # Store result
            result = {
                "filename": file_name,
                "candidate_name": candidate_name,
                "email": parsed_data['contact_information'].get('email', ''),
                "phone": parsed_data['contact_information'].get('phone', ''),
                "location": parsed_data['contact_information'].get('location', ''),
                "skills": len(parsed_data['skills']),
                "experience": len(parsed_data['work_experience']),
                "education": len(parsed_data['education']),
                "certifications": len(parsed_data['certifications']),
                "projects": len(parsed_data['projects']),
                "output_file": str(output_file),
                "status": "success"
            }
            
            self.results.append(result)
            print("✓")
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            error = {
                "filename": file_path.name,
                "error": str(e),
                "status": "failed"
            }
            self.errors.append(error)
    
    def _generate_summary(self, output_dir: Path) -> Dict:
        """Generate processing summary"""
        summary_file = output_dir / "processing_summary.json"
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_processed": len(self.results),
            "total_errors": len(self.errors),
            "success_rate": f"{(len(self.results) / (len(self.results) + len(self.errors)) * 100):.1f}%" if (len(self.results) + len(self.errors)) > 0 else "0%",
            "statistics": self._calculate_statistics(),
            "results": self.results,
            "errors": self.errors
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary
    
    def _calculate_statistics(self) -> Dict:
        """Calculate statistics from results"""
        if not self.results:
            return {}
        
        total_skills = sum(r['skills'] for r in self.results)
        total_experience = sum(r['experience'] for r in self.results)
        total_education = sum(r['education'] for r in self.results)
        
        avg_skills = total_skills / len(self.results) if self.results else 0
        avg_experience = total_experience / len(self.results) if self.results else 0
        avg_education = total_education / len(self.results) if self.results else 0
        
        return {
            "average_skills_per_resume": round(avg_skills, 2),
            "average_experience_entries": round(avg_experience, 2),
            "average_education_entries": round(avg_education, 2),
            "total_unique_candidates": len(set(r['candidate_name'] for r in self.results))
        }
    
    def print_summary(self):
        """Print processing summary to console"""
        print("\n" + "="*70)
        print("BATCH PROCESSING SUMMARY")
        print("="*70)
        
        print(f"\nTotal Processed: {len(self.results)}")
        print(f"Total Errors: {len(self.errors)}")
        
        if self.results:
            print("\nSuccessful Candidates:")
            print("-" * 70)
            for result in self.results[:10]:
                print(f"  {result['filename']}")
                print(f"    Name: {result['candidate_name']}")
                print(f"    Email: {result['email']}")
                print(f"    Skills: {result['skills']} | Experience: {result['experience']}")
            
            if len(self.results) > 10:
                print(f"\n  ... and {len(self.results) - 10} more")
        
        if self.errors:
            print("\nErrors:")
            print("-" * 70)
            for error in self.errors[:5]:
                print(f"  ✗ {error['filename']}: {error['error']}")
            
            if len(self.errors) > 5:
                print(f"\n  ... and {len(self.errors) - 5} more")
        
        print("\n" + "="*70)


def main():
    """Main batch processing entry point"""
    parser = argparse.ArgumentParser(
        description="Batch process multiple resume files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_processor.py ./resumes
  python batch_processor.py ./resumes -o ./output
  python batch_processor.py ./resumes -v
        """
    )
    
    parser.add_argument(
        'directory',
        help='Directory containing resume files'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output directory (default: <input_dir>/parsed_output)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    try:
        processor = BatchProcessor(verbose=args.verbose)
        result = processor.process_directory(args.directory, args.output)
        processor.print_summary()
        
        if result['success']:
            print(f"\n✓ Batch processing completed successfully!")
            print(f"Output saved to: {result['output_directory']}")
            return 0
        else:
            print(f"\n✗ Batch processing failed: {result.get('message', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
