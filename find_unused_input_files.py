#!/usr/bin/env python3
"""
Find unused files in the input directory of a GitHub repository.
This script clones the repo and checks which files in 'input' are not referenced
in any of the Python scripts, then moves them to an 'unused' directory.
"""

import os
import re
import subprocess
import sys
import shutil
from pathlib import Path
from typing import Set, List

def clone_repo(repo_url: str, target_dir: str) -> bool:
    """Clone the GitHub repository."""
    try:
        print(f"Cloning repository: {repo_url}")
        subprocess.run(['git', 'clone', repo_url, target_dir], 
                      check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        return False

def get_input_files(input_dir: Path) -> Set[str]:
    """Get all files in the input directory."""
    if not input_dir.exists():
        print(f"Input directory not found: {input_dir}")
        return set()
    
    files = set()
    for file_path in input_dir.rglob('*'):
        if file_path.is_file():
            # Store relative path from input directory
            rel_path = file_path.relative_to(input_dir)
            files.add(str(rel_path))
            # Also store just the filename
            files.add(file_path.name)
    
    return files

def find_python_files(repo_dir: Path) -> List[Path]:
    """Find all Python files in the repository."""
    python_files = []
    for file_path in repo_dir.rglob('*.py'):
        if file_path.is_file() and '.git' not in str(file_path):
            python_files.append(file_path)
    return python_files

def check_file_references(python_files: List[Path], input_files: Set[str], repo_path: Path):
    """Check which input files are referenced in Python scripts.
    
    Returns:
        tuple: (referenced_files set, file_usage_map dict)
        file_usage_map: {input_file: [list of py files that use it]}
    """
    referenced_files = set()
    file_usage_map = {}  # Maps input file -> list of python files that use it
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Check for each input file
                for input_file in input_files:
                    # Look for the filename in various contexts
                    patterns = [
                        re.escape(input_file),  # Exact match
                        f"['\"].*{re.escape(input_file)}.*['\"]",  # In quotes
                        f"input.*{re.escape(input_file)}",  # With 'input' prefix
                    ]
                    
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            referenced_files.add(input_file)
                            
                            # Track which python file uses this input file
                            if input_file not in file_usage_map:
                                file_usage_map[input_file] = []
                            
                            # Store relative path from repo root
                            rel_py_path = py_file.relative_to(repo_path)
                            if rel_py_path not in file_usage_map[input_file]:
                                file_usage_map[input_file].append(str(rel_py_path))
                            break
        except Exception as e:
            print(f"Warning: Could not read {py_file}: {e}")
    
    return referenced_files, file_usage_map

def move_unused_files(input_dir: Path, unused_files: Set[str], repo_path: Path) -> int:
    """Move unused files to 'unused' directory."""
    unused_dir = repo_path / "unused"
    
    # Create unused directory if it doesn't exist
    if not unused_dir.exists():
        print(f"\nCreating directory: {unused_dir}")
        unused_dir.mkdir(parents=True, exist_ok=True)
    
    moved_count = 0
    
    for file_name in unused_files:
        # Find the actual file (could be in subdirectory)
        source_path = None
        
        # Check if it's a path with subdirectories
        if '/' in file_name or '\\' in file_name:
            potential_path = input_dir / file_name
            if potential_path.exists():
                source_path = potential_path
        else:
            # Search for the file in input directory
            for file_path in input_dir.rglob(file_name):
                if file_path.is_file() and file_path.name == file_name:
                    source_path = file_path
                    break
        
        if source_path and source_path.exists():
            # Preserve directory structure in unused folder
            rel_path = source_path.relative_to(input_dir)
            dest_path = unused_dir / rel_path
            
            # Create parent directories if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                shutil.move(str(source_path), str(dest_path))
                print(f"  ✓ Moved: {rel_path}")
                moved_count += 1
            except Exception as e:
                print(f"  ✗ Error moving {rel_path}: {e}")
    
    return moved_count

def main():
    repo_url = "https://github.com/rcsmit/streamlit_scripts"
    target_dir = "/home/claude/streamlit_scripts_analysis"
    if 1==2:
        # Clean up if directory exists
        if os.path.exists(target_dir):
            print(f"Removing existing directory: {target_dir}")
            subprocess.run(['rm', '-rf', target_dir], check=True)
        
        # Clone the repository
        if not clone_repo(repo_url, target_dir):
            sys.exit(1)
        
        repo_path = Path(target_dir)
    
    repo_path = Path(r"C:\Users\rcxsm\Documents\python_scripts\covid19_seir_models\COVIDcases")
    # repo_path = Path(r"C:\Users\rcxsm\Documents\python_scripts\streamlit_scripts")
    input_dir = repo_path / "input"
    
    print("\n" + "="*70)
    print("ANALYZING REPOSITORY")
    print("="*70)
    
    # Get all files in input directory
    input_files = get_input_files(input_dir)
    print(f"\nFound {len(input_files)} files/references in input directory")
    
    # Find all Python files
    python_files = find_python_files(repo_path)
    print(f"Found {len(python_files)} Python files in repository")
    
    # Check which files are referenced
    print("\nScanning Python files for references...")
    referenced_files, file_usage_map = check_file_references(python_files, input_files, repo_path)
    print(f"Found {len(referenced_files)} referenced files")
    
    # Find unused files - only include actual filenames, not duplicates
    all_actual_files = set()
    for file_path in input_dir.rglob('*'):
        if file_path.is_file():
            all_actual_files.add(file_path.name)
    
    unused_files = all_actual_files - referenced_files
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    if unused_files:
        print(f"\n** Found {len(unused_files)} potentially unused files:\n")
        for file in sorted(unused_files):
            # Find the actual file to get size
            for file_path in input_dir.rglob(file):
                if file_path.is_file() and file_path.name == file:
                    size = file_path.stat().st_size
                    print(f"  • {file} ({size:,} bytes)")
                    break
    else:
        print("\n* All files in the input directory appear to be used!")
    
    print("\n" + "="*70)
    print(f"Summary: {len(unused_files)} unused out of {len(all_actual_files)} total files")
    print("="*70)
    
    # Show file usage map
    if file_usage_map:
        print("\n" + "="*70)
        print("FILE USAGE MAP")
        print("="*70)
        print("\nShowing which Python scripts use which input files:\n")
        
        for input_file in sorted(file_usage_map.keys()):
            py_files = file_usage_map[input_file]
            print(f"📄 {input_file}")
            for py_file in sorted(py_files):
                print(f"   → {py_file}")
            print()
        
        print("="*70)
    
    # Ask user if they want to move files
    if unused_files:
        print("\n" + "="*70)
        response = input("\nDo you want to move these unused files to 'unused' directory? (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            print("\nMoving unused files...")
            moved_count = move_unused_files(input_dir, unused_files, repo_path)
            print(f"\n* Successfully moved {moved_count} files to 'unused' directory")
        else:
            print("\nSkipping file movement.")
    
    # Save results to file
    results_file = "unused_files_report.txt"
    with open(results_file, 'w') as f:
        f.write("UNUSED FILES REPORT\n")
        f.write("="*70 + "\n\n")
        f.write(f"Repository: {repo_url}\n")
        f.write(f"Total files in input/: {len(all_actual_files)}\n")
        f.write(f"Referenced files: {len(referenced_files)}\n")
        f.write(f"Unused files: {len(unused_files)}\n\n")
        
        # Add file usage mapping section
        f.write("="*70 + "\n")
        f.write("FILE USAGE MAP (Which Python file uses which input file)\n")
        f.write("="*70 + "\n\n")
        
        # Sort by input filename
        for input_file in sorted(file_usage_map.keys()):
            f.write(f"- {input_file}\n")
            for py_file in sorted(file_usage_map[input_file]):
                f.write(f"   -> {py_file}\n")
            f.write("\n")
        
        f.write("\n" + "="*70 + "\n")
        if unused_files:
            f.write("UNUSED FILES\n")
            f.write("="*70 + "\n")
            for file in sorted(unused_files):
                for file_path in input_dir.rglob(file):
                    if file_path.is_file() and file_path.name == file:
                        size = file_path.stat().st_size
                        f.write(f"{file} ({size:,} bytes)\n")
                        break
        else:
            f.write("No unused files found!\n")
            f.write("="*70 + "\n")
    
    print(f"\nDetailed report saved to: {results_file}")

if __name__ == "__main__":
    main()