"""
Full Code Audit Script
Comprehensive check for:
- Code quality
- Security vulnerabilities
- Deprecated functions
- Unused files
- Best practices
"""

import os
import re
import ast
import sys
from pathlib import Path
from collections import defaultdict

class CodeAuditor:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.issues = defaultdict(list)
        self.deprecated_functions = [
            'datetime.utcnow()',
            'datetime.utcfromtimestamp()',
            '@validator',  # Pydantic V1
            'min_items',  # Pydantic V1
            'max_items',  # Pydantic V1
        ]
        self.security_patterns = [
            (r'eval\s*\(', 'eval() - dangerous code execution'),
            (r'exec\s*\(', 'exec() - dangerous code execution'),
            (r'__import__\s*\(', '__import__() - dynamic import (check if safe)'),
            (r'compile\s*\(', 'compile() - code compilation'),
            (r'subprocess\.(call|Popen|run)\s*\(', 'subprocess - command execution'),
            (r'pickle\.(loads|load)\s*\(', 'pickle.loads() - unsafe deserialization'),
            (r'yaml\.(load|load_all)\s*\(', 'yaml.load() - unsafe deserialization (use safe_load)'),
            (r'os\.system\s*\(', 'os.system() - command execution'),
            (r'os\.popen\s*\(', 'os.popen() - command execution'),
        ]
        
    def scan_file(self, file_path):
        """Scan a single file for issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Check for deprecated functions
            for i, line in enumerate(lines, 1):
                for dep in self.deprecated_functions:
                    if dep in line and not line.strip().startswith('#'):
                        self.issues['deprecated'].append(
                            f"{file_path}:{i} - {dep}"
                        )
                
                # Check for security issues
                for pattern, description in self.security_patterns:
                    if re.search(pattern, line):
                        # Check if it's in a comment or safe context
                        if not line.strip().startswith('#') and 'TODO' not in line.upper():
                            # Check for __import__ in check scripts (usually safe)
                            if '__import__' in pattern and ('check_setup' in str(file_path) or 'production_checklist' in str(file_path)):
                                continue
                            self.issues['security'].append(
                                f"{file_path}:{i} - {description}"
                            )
                
                # Check for common issues
                if 'TODO' in line or 'FIXME' in line or 'XXX' in line:
                    self.issues['todos'].append(f"{file_path}:{i} - {line.strip()}")
                
                # Check for print statements (should use logger)
                if re.search(r'^\s*print\s*\(', line) and 'venv' not in str(file_path):
                    self.issues['code_quality'].append(
                        f"{file_path}:{i} - Use logger instead of print()"
                    )
                
                # Check for hardcoded secrets
                if re.search(r'(password|secret|api[_-]?key|token)\s*=\s*["\'][^"\']+["\']', line, re.IGNORECASE):
                    if 'example' not in line.lower() and 'test' not in line.lower():
                        self.issues['security'].append(
                            f"{file_path}:{i} - Potential hardcoded secret"
                        )
                
                # Check for missing error handling
                if 'request.json' in line or 'request.form' in line:
                    # Check if it's in try-except
                    context = '\n'.join(lines[max(0, i-5):min(len(lines), i+5)])
                    if 'try:' not in context or 'except' not in context:
                        self.issues['code_quality'].append(
                            f"{file_path}:{i} - request.json without explicit error handling"
                        )
                        
        except Exception as e:
            self.issues['errors'].append(f"{file_path} - Error scanning: {e}")
    
    def find_unused_files(self):
        """Find potentially unused files"""
        python_files = list(self.root_dir.rglob('*.py'))
        imports = set()
        
        # Collect all imports
        for py_file in python_files:
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Find imports
                    tree = ast.parse(content, filename=str(py_file))
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.add(alias.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.add(node.module.split('.')[0])
            except:
                pass
        
        # Check for files not imported
        unused = []
        for py_file in python_files:
            if 'venv' in str(py_file) or '__pycache__' in str(py_file) or 'test' in str(py_file):
                continue
            
            file_name = py_file.stem
            if file_name not in imports and file_name not in ['app', '__init__', 'main']:
                # Check if it's actually a module that could be imported
                if py_file.parent.name not in imports:
                    unused.append(str(py_file.relative_to(self.root_dir)))
        
        if unused:
            self.issues['unused_files'] = unused
    
    def find_duplicate_files(self):
        """Find duplicate or similar files"""
        files_by_name = defaultdict(list)
        for py_file in self.root_dir.rglob('*.py'):
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
            files_by_name[py_file.name].append(str(py_file.relative_to(self.root_dir)))
        
        duplicates = {k: v for k, v in files_by_name.items() if len(v) > 1}
        if duplicates:
            self.issues['duplicates'] = duplicates
    
    def check_gitignore(self):
        """Check .gitignore for common issues"""
        gitignore_path = self.root_dir / '.gitignore'
        if not gitignore_path.exists():
            self.issues['gitignore'].append(".gitignore file not found")
            return
        
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
        
        required_patterns = [
            '__pycache__',
            '*.pyc',
            '.env',
            'venv',
            '*.log'
        ]
        
        missing = []
        for pattern in required_patterns:
            if pattern not in gitignore_content:
                missing.append(pattern)
        
        if missing:
            self.issues['gitignore'].append(f"Missing patterns: {', '.join(missing)}")
    
    def run(self):
        """Run full audit"""
        print("=" * 70)
        print("FULL CODE AUDIT - AI Ticket Classifier")
        print("=" * 70)
        print()
        
        # Scan Python files
        print("Scanning Python files...")
        python_files = list(self.root_dir.rglob('*.py'))
        for py_file in python_files:
            if 'venv' in str(py_file) or '__pycache__' in str(py_file) or 'venv312' in str(py_file):
                continue
            self.scan_file(py_file)
        
        print(f"Scanned {len(python_files)} Python files")
        
        # Find unused files
        print("\nFinding unused files...")
        self.find_unused_files()
        
        # Find duplicates
        print("Finding duplicate files...")
        self.find_duplicate_files()
        
        # Check .gitignore
        print("Checking .gitignore...")
        self.check_gitignore()
        
        # Print results
        print("\n" + "=" * 70)
        print("AUDIT RESULTS")
        print("=" * 70)
        
        total_issues = sum(len(v) for v in self.issues.values())
        
        if total_issues == 0:
            print("\n✅ No issues found! Code is clean.")
        else:
            for category, items in sorted(self.issues.items()):
                if items:
                    print(f"\n⚠️ {category.upper()} ({len(items)} issues):")
                    for item in items[:20]:  # Limit output
                        print(f"  - {item}")
                    if len(items) > 20:
                        print(f"  ... and {len(items) - 20} more")
        
        print(f"\nTotal issues found: {total_issues}")
        print("=" * 70)
        
        return self.issues

if __name__ == '__main__':
    auditor = CodeAuditor()
    issues = auditor.run()
    
    # Exit with error code if issues found
    if any(v for v in issues.values() if v):
        sys.exit(1)
    else:
        sys.exit(0)

