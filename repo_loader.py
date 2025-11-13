import os
import shutil
import stat
import time
from git import Repo
from pathlib import Path
from typing import List, Dict

class RepoLoader:
    """Handles cloning and parsing GitHub repositories."""
    
    def __init__(self, base_dir: str = "repos"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Code file extensions to parse
        self.code_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h',
            '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala',
            '.r', '.m', '.sh', '.bash', '.sql', '.html', '.css', '.vue',
            '.json', '.yaml', '.yml', '.xml', '.md', '.txt'
        }
    
    def _remove_readonly(self, func, path, excinfo):
        """Error handler for Windows readonly file removal."""
        os.chmod(path, stat.S_IWRITE)
        func(path)
    
    def _safe_remove_dir(self, path: Path, max_retries: int = 3):
        """Safely remove directory with Windows-specific handling."""
        if not path.exists():
            return
        
        for attempt in range(max_retries):
            try:
                # On Windows, use onerror callback to handle readonly files
                shutil.rmtree(path, onerror=self._remove_readonly)
                return
            except PermissionError as e:
                if attempt < max_retries - 1:
                    print(f"Retry {attempt + 1}/{max_retries} removing {path}...")
                    time.sleep(0.5)
                else:
                    # Last resort: try to rename and ignore
                    try:
                        backup_path = path.parent / f"{path.name}_old_{int(time.time())}"
                        path.rename(backup_path)
                        print(f"Could not delete {path}, renamed to {backup_path}")
                    except:
                        print(f"Warning: Could not remove {path}, continuing anyway...")
    
    def clone_repo(self, repo_url: str) -> Path:
        """Clone a GitHub repository."""
        # Extract repo name from URL
        repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        repo_path = self.base_dir / repo_name
        
        # Remove existing repo if it exists
        self._safe_remove_dir(repo_path)
        
        # Clone the repository
        Repo.clone_from(repo_url, repo_path, depth=1)
        return repo_path
    
    def parse_files(self, repo_path: Path) -> List[Dict[str, str]]:
        """Parse all code files in the repository."""
        documents = []
        
        for file_path in repo_path.rglob('*'):
            # Skip directories and hidden files
            if file_path.is_dir() or file_path.name.startswith('.'):
                continue
            
            # Skip common non-code directories
            if any(skip in file_path.parts for skip in ['.git', 'node_modules', '__pycache__', 'venv', 'env', 'dist', 'build']):
                continue
            
            # Check if file has a code extension
            if file_path.suffix.lower() not in self.code_extensions:
                continue
            
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Skip empty files or very large files (>500KB)
                if not content.strip() or len(content) > 500000:
                    continue
                
                # Get relative path
                rel_path = file_path.relative_to(repo_path)
                
                documents.append({
                    'content': content,
                    'filepath': str(rel_path),
                    'filename': file_path.name,
                    'extension': file_path.suffix
                })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
        
        return documents
    
    def load_repo(self, repo_url: str) -> List[Dict[str, str]]:
        """Clone and parse a repository."""
        repo_path = self.clone_repo(repo_url)
        documents = self.parse_files(repo_path)
        return documents
