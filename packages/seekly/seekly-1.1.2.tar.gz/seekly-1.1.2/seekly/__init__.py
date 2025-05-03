"""
Seekly: A semantic code search tool.
"""

# Configuration constants for Seekly
# These constants define the behavior of the application without hardcoding values

# Default model configuration
DEFAULT_MODEL = "all-MiniLM-L6-v2"

# Enable this flag to show detailed model loading information
DEBUG_MODEL_LOADING = False

DEFAULT_MAX_LENGTH = 512


# Supported file extensions - centralized configuration
SUPPORTED_EXTENSIONS = {
    # Programming languages
    '.py', '.ipynb', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.cc',
    '.h', '.hpp', '.cs', '.go', '.rb', '.php', '.rs', '.swift', '.kt', '.scala',
    '.m', '.mm', '.pl', '.pm', '.sh', '.bash', '.zsh', '.fish', '.ps1', '.groovy',
    '.r', '.lua', '.tcl', '.dart', '.ex', '.exs', '.erl', '.clj', '.cljs', '.coffee',
    '.elm', '.f', '.f90', '.hs', '.jl', '.lisp', '.ls', '.nim', '.ml', '.pas',
    '.re', '.sol', '.v', '.vhdl', '.zig',
    
    # Web development
    '.html', '.htm', '.css', '.scss', '.sass', '.less', '.svg', '.vue', '.svelte',
    '.json', '.xml', '.wasm',
    
    # Documentation
    '.md', '.markdown', '.rst', '.txt', '.adoc', '.tex',
    
    # Config files
    '.yml', '.yaml', '.toml', '.ini', '.conf', '.cfg', '.properties',
    '.env', '.lock', '.gradle', '.sbt',
    
    # CI/CD & DevOps
    '.tf', '.tfvars', '.hcl', '.jenkinsfile', '.dockerfile', '.Dockerfile',
    '.gitlab-ci.yml', '.travis.yml', '.circleci', '.github', '.azure-pipelines.yml',
    '.kube', '.helm', '.k8s',
    
    # Misc
    '.graphql', '.proto', '.thrift', '.sql', '.bat', '.csv', '.json5', '.plist'
}

# Directories to ignore during indexing - centralized configuration
IGNORED_DIRECTORIES = {
    'venv', 'env', '.git', '.github', '__pycache__', 
    'node_modules', '.vscode', '.idea', 'dist', 'build',
    '.eggs', '.mypy_cache', '.pytest_cache', '.tox'
}

# Generic file categorization mapping
FILE_CATEGORIES = {
    "code": [
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.cc',
        '.cs', '.go', '.rb', '.php', '.swift', '.kt', '.scala', '.rs'
    ],
    "documentation": ['.txt', '.md', '.adoc', '.rst'],
    "config": ['.json', '.yaml', '.yml', '.toml', '.ini'],
    "markup": ['.html', '.htm', '.xml', '.svg'],
    "data": ['.csv', '.tsv', '.json', '.xml']
}

# Generic code relevance keywords - these are not language specific
# but help identify programmatic content across languages
CODE_RELEVANCE_KEYWORDS = {
    # Core programming concepts
    'algorithm', 'function', 'class', 'method', 'implement', 'search', 
    'binary', 'sort', 'tree', 'graph', 'list', 'array', 'hash', 
    'stack', 'queue', 'heap', 'recursion', 'loop', 'variable',
    'inheritance', 'interface', 'abstract', 'static', 'public', 'private',
    
    # File operations
    'file', 'process', 'read', 'write', 'open', 'close', 'parse',
    'load', 'save', 'path', 'directory', 'folder',
    
    # Data handling
    'json', 'xml', 'yaml', 'csv', 'database', 'query', 'model',
    'serialize', 'deserialize', 'encode', 'decode',
    
    # Web development
    'api', 'rest', 'http', 'request', 'response', 'component',
    'client', 'server', 'auth', 'token',
    
    # DevOps & CI/CD
    'pipeline', 'build', 'deploy', 'release', 'version', 'container',
    'test', 'unit', 'integration'
}

# Common text patterns that appear across programming languages
# These are generic enough to work with any language
CODE_PATTERNS = {
    "function_def": r'(?:function|def|void|int|class|public|private|static)\s+\w+\s*\(',
    "loop": r'(?:for|while|foreach)\s*\(',
    "condition": r'(?:if|else|switch|case)\s*[\(\{]',
    "variable": r'(?:var|let|const|int|float|double|string|boolean|char|long)\s+\w+\s*=',
    "return": r'return\s+[\w\(\[]',
    "import": r'(?:import|include|require|using|from)\s+[\w\.]+'
}

# Required for Python package
__version__ = '0.1.0'

# Import cli function from the root seekly.py file
import os
import importlib.util

# Get the path to the root seekly.py file
_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_seekly_py_path = os.path.join(_root_dir, "seekly.py")

# Dynamically import the seekly.py module
_spec = importlib.util.spec_from_file_location("seekly_root", _seekly_py_path)
_seekly_root = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_seekly_root)

# Export the cli function to make it available as seekly.cli
cli = _seekly_root.cli