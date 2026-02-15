#!/usr/bin/env python3
"""
Find unused packages in requirements.txt.
This script checks which packages listed in requirements.txt are not imported
in any of the Python scripts in the repository.
"""

import re
import ast
from pathlib import Path
from typing import Set, Dict, List
import shutil

def parse_requirements(requirements_file: Path) -> Dict[str, str]:
    """Parse requirements.txt and return dict of package names to versions."""
    packages = {}
    
    if not requirements_file.exists():
        print(f"Requirements file not found: {requirements_file}")
        return packages
    
    with open(requirements_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Handle different requirement formats
            # package==1.0.0, package>=1.0.0, package, etc.
            match = re.match(r'^([a-zA-Z0-9_\-\.]+)', line)
            if match:
                package_name = match.group(1).lower()
                packages[package_name] = line
    
    return packages

def normalize_package_name(name: str) -> str:
    """Normalize package name (handle common variations)."""
    # Common package name mappings (PyPI name -> import name)
    mappings = {
        'pillow': 'PIL',
        'beautifulsoup4': 'bs4',
        'python-dateutil': 'dateutil',
        'attrs': 'attr',
        'pyyaml': 'yaml',
        'scikit-learn': 'sklearn',
        'scikit-image': 'skimage',
        'opencv-python': 'cv2',
        'opencv-python-headless': 'cv2',
        'python-docx': 'docx',
        'python-pptx': 'pptx',
        'msgpack-python': 'msgpack',
        'pycrypto': 'Crypto',
        'pyjwt': 'jwt',
        'python-dotenv': 'dotenv',
        'sqlalchemy': 'sqlalchemy',
        'protobuf': 'google.protobuf',
        'pyqt5': 'PyQt5',
        'python-magic': 'magic',
    }
    
    name_lower = name.lower()
    
    # Check if there's a known mapping
    if name_lower in mappings:
        return mappings[name_lower].lower()
    
    # Remove common suffixes/prefixes
    name_clean = name_lower.replace('-', '_').replace('.', '_')
    
    return name_clean

def extract_imports_from_file(file_path: Path) -> Set[str]:
    """Extract all import statements from a Python file."""
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Try to parse with AST (more reliable)
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Get top-level package name
                        top_level = alias.name.split('.')[0]
                        imports.add(top_level.lower())
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Get top-level package name
                        top_level = node.module.split('.')[0]
                        imports.add(top_level.lower())
        except SyntaxError:
            # Fallback to regex if AST parsing fails
            import_patterns = [
                r'^\s*import\s+([a-zA-Z0-9_\.]+)',
                r'^\s*from\s+([a-zA-Z0-9_\.]+)\s+import',
            ]
            
            for line in content.split('\n'):
                for pattern in import_patterns:
                    match = re.match(pattern, line)
                    if match:
                        module = match.group(1).split('.')[0]
                        imports.add(module.lower())
    
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
    
    return imports

def find_python_files(repo_dir: Path) -> List[Path]:
    """Find all Python files in the repository."""
    python_files = []
    for file_path in repo_dir.rglob('*.py'):
        if file_path.is_file() and '.git' not in str(file_path):
            python_files.append(file_path)
    return python_files

def check_package_usage(python_files: List[Path], packages: Dict[str, str], repo_path: Path) -> tuple:
    """Check which packages are used and which files use them.
    
    Returns:
        tuple: (used_packages dict, package_usage_map dict)
        used_packages: {package_name: requirement_line}
        package_usage_map: {package_name: [list of py files that import it]}
    """
    all_imports = set()
    import_usage_map = {}  # Maps import name -> list of files
    
    # Collect all imports from all files
    for py_file in python_files:
        file_imports = extract_imports_from_file(py_file)
        all_imports.update(file_imports)
        
        # Track which file uses which import
        for imp in file_imports:
            if imp not in import_usage_map:
                import_usage_map[imp] = []
            rel_path = py_file.relative_to(repo_path)
            import_usage_map[imp].append(str(rel_path))
    
    used_packages = {}
    package_usage_map = {}
    
    # Check each package in requirements.txt
    for package_name, requirement_line in packages.items():
        normalized = normalize_package_name(package_name)
        
        # Check if this package is imported
        is_used = False
        
        # Check direct match
        if package_name.lower() in all_imports or normalized in all_imports:
            is_used = True
            used_key = package_name.lower() if package_name.lower() in all_imports else normalized
            package_usage_map[package_name] = import_usage_map.get(used_key, [])
        
        # Check if package name is a prefix of any import
        # (for packages like 'google-cloud-storage' imported as 'google.cloud.storage')
        if not is_used:
            package_parts = package_name.lower().replace('-', '_').split('_')
            for imp in all_imports:
                imp_parts = imp.replace('.', '_').split('_')
                if package_parts[0] == imp_parts[0]:
                    is_used = True
                    package_usage_map[package_name] = import_usage_map.get(imp, [])
                    break
        
        if is_used:
            used_packages[package_name] = requirement_line
    
    return used_packages, package_usage_map

def move_to_unused_requirements(requirements_file: Path, unused_packages: Dict[str, str]):
    """Create a separate unused_requirements.txt file."""
    unused_req_file = requirements_file.parent / "unused_requirements.txt"
    
    with open(unused_req_file, 'w', encoding='utf-8', errors='replace') as f:
        f.write("# Packages that appear to be unused (moved from requirements.txt)\n")
        f.write("# Review before deleting - some packages may be used indirectly\n\n")
        for package_name in sorted(unused_packages.keys()):
            f.write(f"{unused_packages[package_name]}\n")
    
    print(f"\n[OK] Created {unused_req_file} with unused packages")
    return unused_req_file

def main():
    # Set your repository path here
    repo_path = Path(r"C:\Users\rcxsm\Documents\python_scripts\covid19_seir_models\COVIDcases")
    # repo_path = Path(r"C:\Users\rcxsm\Documents\python_scripts\streamlit_scripts")
    #repo_path = Path(r"C:\Users\rcxsm\Documents\python_scripts\streamlit_scripts")
    requirements_file = repo_path / "requirements.txt"
    
    print("\n" + "="*70)
    print("ANALYZING REQUIREMENTS.TXT")
    print("="*70)
    
    # Parse requirements.txt
    packages = parse_requirements(requirements_file)
    print(f"\nFound {len(packages)} packages in requirements.txt")
    
    # Find all Python files
    python_files = find_python_files(repo_path)
    print(f"Found {len(python_files)} Python files in repository")
    
    # Check which packages are used
    print("\nScanning Python files for imports...")
    used_packages, package_usage_map = check_package_usage(python_files, packages, repo_path)
    
    # Find unused packages
    unused_packages = {k: v for k, v in packages.items() if k not in used_packages}
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    print(f"\n[OK] Used packages: {len(used_packages)}")
    print(f"[!] Unused packages: {len(unused_packages)}")
    
    if unused_packages:
        print(f"\n[!] Found {len(unused_packages)} potentially unused packages:\n")
        for package_name in sorted(unused_packages.keys()):
            print(f"  - {unused_packages[package_name]}")
    else:
        print("\n[OK] All packages in requirements.txt appear to be used!")
    
    # Show package usage map
    if package_usage_map:
        print("\n" + "="*70)
        print("PACKAGE USAGE MAP")
        print("="*70)
        print("\nShowing which Python scripts import which packages:")
        print("(Only showing file details for packages used in < 7 files)\n")
        
        for package_name in sorted(package_usage_map.keys()):
            py_files = package_usage_map[package_name]
            if py_files:
                unique_files = sorted(set(py_files))
                file_count = len(unique_files)
                
                print(f"[*] {package_name} (used in {file_count} file(s))")
                
                # Only show individual files if used in fewer than 7 files
                if file_count < 7:
                    for py_file in unique_files:
                        print(f"    - {py_file}")
                print()
        
        print("="*70)
    
    # Save detailed report
    report_file = repo_path / "unused_packages_report.txt"
    with open(report_file, 'w', encoding='utf-8', errors='replace') as f:
        f.write("UNUSED PACKAGES REPORT\n")
        f.write("="*70 + "\n\n")
        f.write(f"Repository: {repo_path}\n")
        f.write(f"Total packages in requirements.txt: {len(packages)}\n")
        f.write(f"Used packages: {len(used_packages)}\n")
        f.write(f"Unused packages: {len(unused_packages)}\n\n")
        
        # Package usage map
        f.write("="*70 + "\n")
        f.write("PACKAGE USAGE MAP (Which Python file imports which package)\n")
        f.write("="*70 + "\n\n")
        f.write("Note: Only showing file references for packages used in fewer than 7 files\n\n")
        
        for package_name in sorted(package_usage_map.keys()):
            py_files = package_usage_map[package_name]
            if py_files:
                unique_files = sorted(set(py_files))
                file_count = len(unique_files)
                
                f.write(f"[*] {package_name} (used in {file_count} file(s))\n")
                
                # Only show individual files if used in fewer than 7 files
                if file_count < 7:
                    for py_file in unique_files:
                        f.write(f"    - {py_file}\n")
                f.write("\n")
        
        # Unused packages
        f.write("\n" + "="*70 + "\n")
        if unused_packages:
            f.write("UNUSED PACKAGES\n")
            f.write("="*70 + "\n")
            f.write("WARNING: Some packages may be used indirectly or at runtime.\n")
            f.write("Review carefully before removing!\n\n")
            for package_name in sorted(unused_packages.keys()):
                f.write(f"{unused_packages[package_name]}\n")
        else:
            f.write("No unused packages found!\n")
            f.write("="*70 + "\n")
    
    print(f"\n[OK] Detailed report saved to: {report_file}")
    
    # Ask if user wants to create unused_requirements.txt
    if unused_packages:
        print("\n" + "="*70)
        response = input("\nCreate 'unused_requirements.txt' with unused packages? (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            unused_req_file = move_to_unused_requirements(requirements_file, unused_packages)
            print(f"\n[!] NOTE: Review {unused_req_file} carefully!")
            print("Some packages may be:")
            print("  - Used indirectly as dependencies")
            print("  - Imported dynamically at runtime")
            print("  - Required by deployment/production environments")
        else:
            print("\nSkipping unused_requirements.txt creation.")

if __name__ == "__main__":
    main()