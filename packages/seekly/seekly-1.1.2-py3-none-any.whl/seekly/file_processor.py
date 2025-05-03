"""
File processing utilities for Seekly CLI.
Handles file traversal, reading, and content chunking.
"""

import os
import re
import numpy as np # type: ignore
from typing import List, Tuple

def list_files(directory: str, exclude_dirs: List[str] = None) -> List[str]:
    """
    List all files in a directory recursively.
    
    Args:
        directory: Directory path to search
        exclude_dirs: List of directory names to exclude
        
    Returns:
        List of absolute file paths
    """
    if exclude_dirs is None:
        exclude_dirs = [".git", ".github", "__pycache__", "node_modules"]
    
    files = []
    for root, dirs, filenames in os.walk(directory):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for filename in filenames:
            file_path = os.path.join(root, filename)
            files.append(file_path)
    
    return files

def normalize_embedding(embedding):
    """
    Normalize embedding vector to unit length.
    """
    norm = np.linalg.norm(embedding)
    if norm > 0:
        return embedding / norm
    return embedding

def process_file(file_path: str) -> str:
    """
    Process a file and return its content as a string.
    
    Args:
        file_path: Path to the file to process
        
    Returns:
        File content as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Skip binary files
        return ""
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return ""

def get_relative_path(file_path: str, base_dir: str) -> str:
    """
    Convert an absolute file path to a path relative to the base directory.
    
    Args:
        file_path: Absolute file path
        base_dir: Base directory path
        
    Returns:
        Relative file path
    """
    abs_base = os.path.abspath(base_dir)
    abs_file = os.path.abspath(file_path)
    
    # Handle case where file_path is already a relative path
    if not os.path.isabs(file_path):
        return file_path
    
    try:
        rel_path = os.path.relpath(abs_file, abs_base)
        return rel_path
    except ValueError:
        # If on different drives (Windows), return the absolute path
        return abs_file

def reformulate_query(query: str) -> str:
    """
    Reformulate a search query to enhance search accuracy.
    
    Args:
        query: Original search query
        
    Returns:
        Reformulated query
    """
    # Simple reformulation: add "code" or "function" if those concepts are implied
    lower_query = query.lower()
    if any(term in lower_query for term in ['algorithm', 'implementation', 'code for', 'program for']):
        if not any(term in lower_query for term in ['code', 'function', 'method']):
            return f"code {query}"
    return query

def augment_code_context(text: str, query: str) -> str:
    """
    Augment code with additional context based on the query.
    
    Args:
        text: Code text
        query: Search query
        
    Returns:
        Augmented code text
    """
    # Add query-specific context to the code text
    # This simple implementation just prepends the query as a comment
    query_keywords = set(query.lower().split())
    important_keywords = {'function', 'class', 'method', 'algorithm', 'check', 'determine'}
    
    matched_keywords = query_keywords.intersection(important_keywords)
    if matched_keywords:
        keyword_context = f"# Context: {', '.join(matched_keywords)}\n"
        return keyword_context + text
    
    return text

def extract_relevant_code_snippet(file_path: str, query: str, context_lines: int = 5) -> List[str]:
    """
    Extract a relevant code snippet from a file based on query.
    
    Args:
        file_path: Path to the file to extract snippet from
        query: Query to find in content
        context_lines: Number of context lines to include before and after match
        
    Returns:
        List of relevant code lines with line numbers
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return ["Binary file - cannot display content"]
    except FileNotFoundError:
        return [f"File not found: {file_path}"]
    except Exception as e:
        return [f"Error reading file: {str(e)}"]
    
    lines = content.split('\n')
    query_lower = query.lower()
    
    # Find the most relevant line number
    best_line_idx = -1
    highest_match_score = 0
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        match_score = 0
        
        # Simple relevance scoring
        if query_lower in line_lower:
            match_score = line_lower.count(query_lower) * 10
        
        # Check for partial matches of query terms
        for term in query_lower.split():
            if term in line_lower:
                match_score += 3
        
        if match_score > highest_match_score:
            highest_match_score = match_score
            best_line_idx = i
    
    # If no match found, return first few lines
    if best_line_idx == -1 or highest_match_score == 0:
        return lines[:min(10, len(lines))]
    
    # Calculate context window
    start_idx = max(0, best_line_idx - context_lines)
    end_idx = min(len(lines), best_line_idx + context_lines + 1)
    
    # Return snippet with line numbers
    return lines[start_idx:end_idx]

class FileProcessor:
    """
    Processes files for analysis and embedding generation.
    Handles file reading, content extraction, and function detection.
    """
    
    def __init__(self):
        """Initialize the file processor."""
        pass
        
    def process_file(self, file_path: str) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Process a file and extract its content and functions.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Tuple of (file_content, list_of_functions)
            where list_of_functions is a list of (function_name, function_content) tuples
        """
        # Read file content
        content = ""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Skip binary files
            return "", []
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return "", []
            
        # Extract functions based on file extension
        functions = []
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Import SUPPORTED_EXTENSIONS from the parent package
        from seekly import SUPPORTED_EXTENSIONS
        
        # Group file extensions by language family for more efficient processing
        if file_ext not in SUPPORTED_EXTENSIONS:
            # If the extension is not supported, return the content without functions
            return content, []
            
        # Python family
        if file_ext in ['.py', '.ipynb']:
            functions = self._extract_python_functions(content)
            
        # JavaScript/TypeScript family
        elif file_ext in ['.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte']:
            functions = self._extract_js_functions(content)
            
        # Java family
        elif file_ext in ['.java', '.kt', '.groovy', '.scala']:
            functions = self._extract_java_functions(content)
            
        # C/C++ family
        elif file_ext in ['.c', '.cpp', '.cc', '.h', '.hpp', '.m', '.mm']:
            functions = self._extract_c_functions(content)
            
        # C# family
        elif file_ext in ['.cs', '.vb']:
            functions = self._extract_csharp_functions(content)
            
        # Go
        elif file_ext in ['.go']:
            functions = self._extract_go_functions(content)
            
        # Ruby
        elif file_ext in ['.rb']:
            functions = self._extract_ruby_functions(content)
            
        # PHP
        elif file_ext in ['.php']:
            functions = self._extract_php_functions(content)
            
        # Rust
        elif file_ext in ['.rs']:
            functions = self._extract_rust_functions(content)
            
        # Swift
        elif file_ext in ['.swift']:
            functions = self._extract_swift_functions(content)
            
        # Shell scripts
        elif file_ext in ['.sh', '.bash', '.zsh', '.fish', '.ps1']:
            functions = self._extract_shell_functions(content)
            
        # Functional languages
        elif file_ext in ['.hs', '.ml', '.clj', '.cljs', '.lisp', '.el']:
            functions = self._extract_functional_language_functions(content)
            
        # Other scripting languages
        elif file_ext in ['.pl', '.pm', '.r', '.lua', '.tcl', '.dart', '.coffee']:
            functions = self._extract_script_language_functions(content)
            
        # Markup/web languages
        elif file_ext in ['.html', '.htm', '.xml', '.css', '.scss', '.sass', '.less']:
            functions = self._extract_markup_functions(content)
            
        # Configuration files
        elif file_ext in ['.json', '.yml', '.yaml', '.toml', '.ini', '.conf', '.cfg', '.properties']:
            functions = self._extract_config_sections(content, file_ext)
            
        # Use a generic extractor for any other supported file types
        else:
            functions = self._extract_generic_functions(content)
        
        return content, functions
        
    def _extract_python_functions(self, content: str) -> List[Tuple[str, str]]:
        """Extract functions from Python code."""
        functions = []
        # Simple regex-based extraction for functions and methods
        pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*:'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            func_name = match.group(1)
            start_pos = match.start()
            
            # Find the end of the function (next def at the same indentation level)
            # This is a simplified approach and might not work for all cases
            next_def = content.find('\ndef ', start_pos + 1)
            if next_def == -1:
                # If no next function, use the rest of the content
                func_content = content[start_pos:]
            else:
                func_content = content[start_pos:next_def]
                
            functions.append((func_name, func_content))
            
        return functions
        
    def _extract_js_functions(self, content: str) -> List[Tuple[str, str]]:
        """Extract functions from JavaScript/TypeScript code."""
        functions = []
        # Match both function declarations and arrow functions
        patterns = [
            r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*{',
            r'(const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*function\s*\([^)]*\)\s*{'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                if match.group(0).startswith(('const', 'let', 'var')):
                    func_name = match.group(2)
                else:
                    func_name = match.group(1)
                    
                start_pos = match.start()
                
                # Find matching closing brace
                open_count = 1
                end_pos = start_pos + match.group(0).find('{') + 1
                
                while open_count > 0 and end_pos < len(content):
                    if content[end_pos] == '{':
                        open_count += 1
                    elif content[end_pos] == '}':
                        open_count -= 1
                    end_pos += 1
                    
                if open_count == 0:
                    func_content = content[start_pos:end_pos]
                    functions.append((func_name, func_content))
        
        return functions
        
    def _extract_java_functions(self, content: str) -> List[Tuple[str, str]]:
        """Extract methods from Java code."""
        # Simplified pattern for Java methods
        pattern = r'(?:public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *\{'
        return self._extract_with_brace_matching(content, pattern)
        
    def _extract_c_functions(self, content: str) -> List[Tuple[str, str]]:
        """Extract functions from C/C++ code."""
        # Simplified pattern for C/C++ functions
        pattern = r'(?:\w+\s+)+(\w+)\s*\([^;]*\)\s*\{'
        return self._extract_with_brace_matching(content, pattern)
        
    def _extract_go_functions(self, content: str) -> List[Tuple[str, str]]:
        """Extract functions from Go code."""
        # Simplified pattern for Go functions
        pattern = r'func\s+(\w+)\s*\([^)]*\)\s*(?:\([^)]*\))?\s*\{'
        return self._extract_with_brace_matching(content, pattern)
        
    def _extract_ruby_functions(self, content: str) -> List[Tuple[str, str]]:
        """Extract methods from Ruby code."""
        functions = []
        # Ruby method pattern
        pattern = r'def\s+(\w+)(?:\s*\([^\)]*\))?\s*'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            func_name = match.group(1)
            start_pos = match.start()
            
            # Find the end of the method (next def or end keyword)
            next_def = content.find('\ndef ', start_pos + 1)
            method_end = content.find('\nend', start_pos + 1)
            
            if next_def == -1 and method_end == -1:
                # If no next method or end keyword, use the rest of the content
                func_content = content[start_pos:]
            elif next_def == -1:
                # Only end keyword found
                func_content = content[start_pos:method_end + 4]  # Include 'end'
            elif method_end == -1:
                # Only next method found
                func_content = content[start_pos:next_def]
            else:
                # Both found, use the closest one
                end_pos = min(next_def, method_end + 4)
                func_content = content[start_pos:end_pos]
                
            functions.append((func_name, func_content))
            
        return functions
        
    def _extract_php_functions(self, content: str) -> List[Tuple[str, str]]:
        """Extract functions from PHP code."""
        # PHP function pattern
        pattern = r'function\s+(\w+)\s*\([^\)]*\)\s*\{'
        return self._extract_with_brace_matching(content, pattern)
        
    def _extract_rust_functions(self, content: str) -> List[Tuple[str, str]]:
        """Extract functions from Rust code."""
        # Rust function pattern
        pattern = r'fn\s+(\w+)\s*(?:<[^>]*>)?\s*\([^\)]*\)\s*(?:->\s*[^\{]*\s*)?\{'
        return self._extract_with_brace_matching(content, pattern)
        
    def _extract_swift_functions(self, content: str) -> List[Tuple[str, str]]:
        """Extract functions from Swift code."""
        # Swift function pattern covering various function types and access levels
        pattern = r'(?:public\s+|private\s+|fileprivate\s+|internal\s+|open\s+)?(?:func|class\s+func|static\s+func)\s+(\w+)\s*\([^\)]*\)\s*(?:->(?:\s*[^{]*)?)?\s*\{'
        return self._extract_with_brace_matching(content, pattern)
        
    def _extract_with_brace_matching(self, content: str, pattern: str) -> List[Tuple[str, str]]:
        """
        Extract functions using the given pattern and brace matching.
        
        Args:
            content: Code content
            pattern: Regex pattern with function name as first capturing group
            
        Returns:
            List of (function_name, function_content) tuples
        """
        functions = []
        matches = re.finditer(pattern, content)
        
        for match in matches:
            func_name = match.group(1)
            start_pos = match.start()
            
            # Find matching closing brace
            open_count = 1
            end_pos = start_pos + match.group(0).find('{') + 1
            
            while open_count > 0 and end_pos < len(content):
                if content[end_pos] == '{':
                    open_count += 1
                elif content[end_pos] == '}':
                    open_count -= 1
                end_pos += 1
                
            if open_count == 0:
                func_content = content[start_pos:end_pos]
                functions.append((func_name, func_content))
        
        return functions
    
    def _extract_csharp_functions(self, content: str) -> List[Tuple[str, str]]:
        """Extract methods from C# code in a language-agnostic way."""
        # C# methods pattern covering various access modifiers and return types
        pattern = r'(?:public|private|protected|internal|static|virtual|override|abstract|\s)+\s+[\w\<\>\[\]\.]+\s+(\w+)\s*\([^\)]*\)\s*(?:\s*where\s+[^{]+)?\s*\{'
        return self._extract_with_brace_matching(content, pattern)
    
    def _extract_shell_functions(self, content: str) -> List[Tuple[str, str]]:
        """Extract functions from shell scripts."""
        functions = []
        # Shell function patterns (covers bash, zsh, etc.)
        patterns = [
            r'function\s+(\w+)\s*\(\)\s*\{',  # function name() {
            r'(\w+)\s*\(\)\s*\{'              # name() {
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                func_name = match.group(1)
                start_pos = match.start()
                
                # Find matching closing brace
                end_pos = content.find('\n}', start_pos + 1)
                if end_pos == -1:
                    # Try to find brace at same line
                    same_line_end = content.find('}', start_pos + 1)
                    if same_line_end == -1:
                        continue
                    end_pos = same_line_end + 1
                else:
                    end_pos += 2  # Include the closing brace
                    
                func_content = content[start_pos:end_pos]
                functions.append((func_name, func_content))
                
        return functions
    
    def _extract_functional_language_functions(self, content: str) -> List[Tuple[str, str]]:
        """Extract functions from functional programming languages (Haskell, ML, Lisp, Clojure, etc.)."""
        functions = []
        
        # Try to match function definitions across multiple functional languages
        # This is a simplified approach that captures common patterns
        patterns = [
            # Haskell-like
            r'(\w+)\s*::.+\n\1\s+(?:\w+\s+)*=',
            # ML-like (OCaml, F#)
            r'let\s+(\w+)(?:\s+\w+)*\s*=',
            # Lisp/Clojure-like
            r'\(defn?\s+(\w+)',
            # General functional pattern (name + args)
            r'(\w+)\s*=\s*(?:function|lambda)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                func_name = match.group(1)
                start_pos = match.start()
                
                # Find the end of the function (next blank line or next definition)
                next_blank = content.find('\n\n', start_pos + 1)
                next_def = -1
                
                # Look for another definition pattern
                for p in patterns:
                    pos = content.find('\n' + p.split('\\')[0], start_pos + 1)
                    if pos != -1 and (next_def == -1 or pos < next_def):
                        next_def = pos
                
                if next_blank == -1 and next_def == -1:
                    # If no clear end, use a reasonable chunk
                    end_pos = min(start_pos + 500, len(content))
                elif next_blank == -1:
                    end_pos = next_def
                elif next_def == -1:
                    end_pos = next_blank
                else:
                    # Use the closest endpoint
                    end_pos = min(next_blank, next_def)
                
                func_content = content[start_pos:end_pos].strip()
                functions.append((func_name, func_content))
        
        return functions
    
    def _extract_script_language_functions(self, content: str) -> List[Tuple[str, str]]:
        """Extract functions from various scripting languages (Perl, R, Lua, Tcl, Dart, etc.)."""
        functions = []
        
        # Multi-language pattern that captures common function definition styles across scripting languages
        patterns = [
            # Perl/Tcl style
            r'sub\s+(\w+)\s*\{',
            # R style
            r'(\w+)\s*<-\s*function\s*\(',
            # Lua style
            r'function\s+(\w+)\s*\([^\)]*\)',
            # Dart style
            r'(?:void|int|double|String|bool|var|dynamic)?\s+(\w+)\s*\([^\)]*\)\s*(?:async\s*)?\{',
            # CoffeeScript style
            r'(\w+)\s*[=:]\s*(?:\([^\)]*\)\s*)?->',
            # General pattern for unnamed functions assigned to variables
            r'(?:var|let|my|local|)\s+(\w+)\s*=\s*function'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                func_name = match.group(1)
                start_pos = match.start()
                
                # Find the function end - either by brace matching or blank lines
                if '{' in match.group(0):
                    # Use brace matching for C-style languages
                    end_pos = start_pos
                    open_count = 0
                    brace_pos = match.group(0).find('{')
                    
                    if brace_pos != -1:
                        open_count = 1
                        end_pos = start_pos + brace_pos + 1
                        
                        while open_count > 0 and end_pos < len(content):
                            if content[end_pos] == '{':
                                open_count += 1
                            elif content[end_pos] == '}':
                                open_count -= 1
                            end_pos += 1
                else:
                    # For languages without braces, use blank lines or next function as delimiter
                    end_pos = content.find('\n\n', start_pos + 1)
                    if end_pos == -1:
                        end_pos = min(start_pos + 500, len(content))
                
                func_content = content[start_pos:end_pos]
                functions.append((func_name, func_content))
        
        return functions
    
    def _extract_markup_functions(self, content: str) -> List[Tuple[str, str]]:
        """Extract structured elements from markup languages (HTML, XML, CSS, etc.)."""
        functions = []
        
        # For HTML/XML: Extract elements with ids or named elements like functions, classes
        html_patterns = [
            # HTML elements with ID
            r'<\s*(\w+)[^>]*\s+id\s*=\s*[\'"]([^\'"]+)[\'"][^>]*>',
            # HTML elements with class
            r'<\s*(\w+)[^>]*\s+class\s*=\s*[\'"]([^\'"]+)[\'"][^>]*>',
            # HTML elements that are usually important (headers, divs with role)
            r'<\s*(h[1-6]|main|header|footer|nav)[^>]*>(.*?)</\s*\1\s*>',
            # Script or style tags
            r'<\s*(script|style)[^>]*>(.*?)</\s*\1\s*>'
        ]
        
        # For CSS: Extract rules and declarations
        css_patterns = [
            # CSS class or ID selector
            r'([.#][\w-]+)\s*\{([^}]*)\}',
            # CSS element with ID or class
            r'(\w+(?:[.#][\w-]+)+)\s*\{([^}]*)\}'
        ]
        
        # Process HTML/XML patterns
        for pattern in html_patterns:
            try:
                if 'script|style' in pattern:
                    # For script and style tags, we need to use re.DOTALL to match across lines
                    matches = re.finditer(pattern, content, re.DOTALL)
                else:
                    matches = re.finditer(pattern, content)
                
                for match in matches:
                    if len(match.groups()) == 2:
                        # For elements with ID or class attributes
                        element_type = match.group(1)
                        identifier = match.group(2)
                        
                        if 'id=' in match.group(0):
                            name = f"{element_type}#{identifier}"
                        else:
                            name = f"{element_type}.{identifier}"
                            
                        start_pos = match.start()
                        
                        # Find the closing tag
                        close_tag = f"</{element_type}>"
                        end_tag_pos = content.find(close_tag, start_pos)
                        
                        if end_tag_pos != -1:
                            end_pos = end_tag_pos + len(close_tag)
                            segment = content[start_pos:end_pos]
                            functions.append((name, segment))
            except re.error:
                continue
        
        # Process CSS patterns
        for pattern in css_patterns:
            try:
                matches = re.finditer(pattern, content)
                for match in matches:
                    selector = match.group(1)
                    declarations = match.group(2)
                    segment = f"{selector} {{{declarations}}}"
                    functions.append((selector, segment))
            except re.error:
                continue
                
        return functions
    
    def _extract_config_sections(self, content: str, file_ext: str) -> List[Tuple[str, str]]:
        """Extract structured sections from configuration files (JSON, YAML, TOML, etc.)."""
        functions = []
        
        # Different approaches based on file type
        if file_ext in ['.json', '.json5']:
            # For JSON: Extract top-level keys
            try:
                # Simple regex-based approach (not full JSON parsing)
                # Extract top-level keys in the format "key": { ... }
                pattern = r'["\']([\w\-\.]+)["\']\s*:\s*\{'
                matches = re.finditer(pattern, content)
                
                for match in matches:
                    key_name = match.group(1)
                    start_pos = match.start()
                    
                    # Find matching closing brace
                    open_count = 1
                    end_pos = start_pos + match.group(0).find('{') + 1
                    
                    while open_count > 0 and end_pos < len(content):
                        if content[end_pos] == '{':
                            open_count += 1
                        elif content[end_pos] == '}':
                            open_count -= 1
                        end_pos += 1
                        
                    if open_count == 0:
                        func_content = content[start_pos:end_pos]
                        functions.append((key_name, func_content))
            except Exception:
                pass
                
        elif file_ext in ['.yml', '.yaml']:
            # For YAML: Extract top-level entries and their indented blocks
            try:
                # Simple line-based parsing to find top-level sections
                lines = content.split('\n')
                current_section = None
                section_content = []
                
                for i, line in enumerate(lines):
                    if not line.strip() or line.strip().startswith('#'):
                        continue
                        
                    # Top-level entries (no indentation)
                    if not line.startswith(' ') and ':' in line:
                        # Save the previous section if there was one
                        if current_section:
                            section_text = '\n'.join(section_content)
                            functions.append((current_section, section_text))
                            
                        # Start a new section
                        current_section = line.split(':', 1)[0].strip()
                        section_content = [line]
                    elif current_section:
                        # Add line to current section
                        section_content.append(line)
                
                # Don't forget to add the last section
                if current_section and section_content:
                    section_text = '\n'.join(section_content)
                    functions.append((current_section, section_text))
            except Exception:
                pass
                
        elif file_ext in ['.toml']:
            # For TOML: Extract sections marked by [section_name]
            try:
                # Match TOML section headers like [section] or [[array_section]]
                pattern = r'^\s*(\[+)([^\]]+)(\]+)\s*$'
                lines = content.split('\n')
                current_section = None
                section_content = []
                
                for i, line in enumerate(lines):
                    match = re.match(pattern, line)
                    if match:
                        # Save the previous section if there was one
                        if current_section:
                            section_text = '\n'.join(section_content)
                            functions.append((current_section, section_text))
                            
                        # Start a new section
                        current_section = match.group(2).strip()
                        section_content = [line]
                    elif current_section:
                        # Add line to current section
                        section_content.append(line)
                        
                # Don't forget to add the last section
                if current_section and section_content:
                    section_text = '\n'.join(section_content)
                    functions.append((current_section, section_text))
            except Exception:
                pass
                
        elif file_ext in ['.ini', '.conf', '.cfg', '.properties']:
            # For INI/config: Extract sections marked by [section_name]
            try:
                # Match INI section headers like [section]
                pattern = r'^\s*\[([^\]]+)\]\s*$'
                lines = content.split('\n')
                current_section = None
                section_content = []
                
                for i, line in enumerate(lines):
                    match = re.match(pattern, line)
                    if match:
                        # Save the previous section if there was one
                        if current_section:
                            section_text = '\n'.join(section_content)
                            functions.append((current_section, section_text))
                            
                        # Start a new section
                        current_section = match.group(1).strip()
                        section_content = [line]
                    elif current_section:
                        # Add line to current section
                        section_content.append(line)
                        
                # Don't forget to add the last section
                if current_section and section_content:
                    section_text = '\n'.join(section_content)
                    functions.append((current_section, section_text))
            except Exception:
                pass
                
        return functions
    
    def _extract_generic_functions(self, content: str) -> List[Tuple[str, str]]:
        """
        Generic function/section extraction for any other supported file types.
        Uses language-agnostic pattern recognition to identify probable function-like structures.
        """
        functions = []
        
        # Generic patterns that work across many languages
        patterns = [
            # General function pattern with name and parentheses
            r'(?:^|\n)\s*(\w+)\s*\([^\)]*\)\s*[\{\:]',
            # General assignment pattern (name = something)
            r'(?:^|\n)\s*(\w+)\s*=\s*[^\n]+',
            # Section headers/comments that might indicate logical sections
            r'(?:^|\n)\s*(?://|#|;)\s*(?:SECTION|BEGIN|START|MARK):\s*([^\n]+)',
            # Any string that might be a class or type definition
            r'(?:^|\n)\s*(?:class|type|interface|struct|enum)\s+(\w+)',
            # Any line with meaningful indentation followed by a named declaration
            r'(?:^|\n)(?:\t+|\s{2,})(\w+)\s*[:\=]'
        ]
        
        for pattern in patterns:
            try:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    name = match.group(1).strip()
                    if not name or len(name) < 2:  # Skip very short names
                        continue
                        
                    start_pos = match.start()
                    
                    # Determine end position based on structure
                    if '{' in match.group(0):
                        # For brace-based languages
                        open_count = 1
                        brace_pos = match.group(0).find('{')
                        end_pos = start_pos + brace_pos + 1
                        
                        # Find matching closing brace
                        while open_count > 0 and end_pos < len(content):
                            if content[end_pos] == '{':
                                open_count += 1
                            elif content[end_pos] == '}':
                                open_count -= 1
                            end_pos += 1
                    else:
                        # For non-brace languages, look for patterns that might indicate end
                        # 1. Next blank line
                        next_blank = content.find('\n\n', start_pos + 1)
                        # 2. Next similar structure at same indentation
                        indentation = len(match.group(0)) - len(match.group(0).lstrip())
                        indent_pattern = f"\n{' ' * indentation}\\w+"
                        next_same_indent = -1
                        
                        indent_match = re.search(indent_pattern, content[start_pos + 1:])
                        if indent_match:
                            next_same_indent = start_pos + 1 + indent_match.start()
                        
                        # Use appropriate endpoint
                        if next_blank == -1 and next_same_indent == -1:
                            # If no clear endpoints found, use a reasonable chunk size
                            end_pos = min(start_pos + 500, len(content))
                        elif next_blank == -1:
                            end_pos = next_same_indent
                        elif next_same_indent == -1:
                            end_pos = next_blank
                        else:
                            end_pos = min(next_blank, next_same_indent)
                    
                    # Extract the content
                    func_content = content[start_pos:end_pos].strip()
                    
                    # Only add if we have meaningful content and not duplicate names
                    if len(func_content) > 10 and not any(name == fn_name for fn_name, _ in functions):
                        functions.append((name, func_content))
            except re.error:
                continue
                
        # If we didn't find any functions with specific patterns,
        # try dividing the content into logical chunks by blank lines
        if not functions and len(content) > 0:
            chunks = re.split(r'\n{2,}', content)
            for i, chunk in enumerate(chunks):
                chunk = chunk.strip()
                if len(chunk) > 10:
                    # Try to extract a name from the first line
                    first_line = chunk.split('\n')[0].strip()
                    name_match = re.search(r'\b(\w{2,})\b', first_line)
                    name = f"section_{i+1}" if not name_match else name_match.group(1)
                    functions.append((name, chunk))
        
        return functions