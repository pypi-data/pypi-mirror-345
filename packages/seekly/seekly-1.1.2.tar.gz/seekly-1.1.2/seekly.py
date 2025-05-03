#!/usr/bin/env python3
"""
Seekly CLI - Natural language search for files
A semantic code search tool that understands what your code does.
"""

import os
import sys
import time
import click
from pathlib import Path
from seekly.search import SeeklySearch
from seekly.spinner import Spinner


# Create a shared context for commands to access the same searcher instance
class SeeklyContext:
    def __init__(self):
        self.searcher = SeeklySearch(verbose=False)
        self.verbose = False
        self.spinner = Spinner()

pass_seekly_context = click.make_pass_decorator(SeeklyContext, ensure=True)


@click.group(help="Seekly - Semantic code search that understands your codebase")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed debug information")
@click.pass_context
def cli(ctx, verbose):
    """Natural language search for code across files and directories.
    
    Common options available in subcommands:
    
      --dir, -d          Directory to search in (default: current directory)
      
      --top-k, -k        Number of results to display (default: 10)
      
      --similarity, -s   Minimum similarity threshold for results (0-1)
    
    Example usage:
      seekly search "function that sorts an array" --dir ~/projects --top-k 5
    """
    # Initialize the context
    ctx.obj = SeeklyContext()
    ctx.obj.verbose = verbose


@cli.command(help="Search for code using natural language")
@click.argument("query", required=False)
@click.option("--dir", "-d", default=".", show_default=True, type=click.Path(exists=True),
              help="Directory to search in")
@click.option("--top-k", "-k", default=10, show_default=True, type=int,
              help="Maximum number of results to show")
@click.option("--similarity", "-s", default=0.5, show_default=True, type=float,
              help="Minimum similarity score (0-1)")
@click.option("--snippets/--no-snippets", default=True, show_default=True,
              help="Show code snippets in results")
@click.option("--all/--limit", default=True, show_default=True,
              help="Show all matching results vs limiting to top-k")
@pass_seekly_context
def search(ctx, query: str = None, dir: str = ".", top_k: int = 10, 
           similarity: float = 0.4, snippets: bool = True, all: bool = True):
    """
    Find code that matches your description using semantic search.
    
    Examples:
      seekly search "function that sorts an array"
      seekly search "code that validates email addresses" --dir ~/projects
      seekly search "implementation of binary search" --similarity 0.5
    """
    # Interactive mode if no query provided
    if not query:
        click.echo("Seekly Interactive Search")
        click.echo("Enter your query (or 'exit' to quit):")
        query = click.prompt("> ", type=str)
        if query.lower() in ('exit', 'quit'):
            return

    # Normalize and expand directory path
    dir_path = os.path.abspath(os.path.expanduser(dir))
    
    # Validate directory exists
    if not os.path.isdir(dir_path):
        click.echo(f"Error: Directory '{dir}' does not exist", err=True)
        sys.exit(1)
    
    # Set verbose mode based on context
    ctx.searcher.verbose = ctx.verbose
    
    # Automatically load model if needed - use spinner for visual feedback
    if not ctx.searcher.is_model_loaded():
        try:
            # Start spinner for model loading
            ctx.spinner.start("Loading semantic search model")
            
            # Load the model
            success = ctx.searcher.load_model(verbose_override=False)
            
            # Stop spinner with appropriate message
            if success:
                ctx.spinner.stop("Model loaded successfully!")
            else:
                ctx.spinner.stop("Failed to load model")
                click.echo("Error: Could not load semantic search model.")
                sys.exit(1)
        except Exception as e:
            ctx.spinner.stop()
            click.echo(f"Error loading model: {str(e)}")
            click.echo("Please check your internet connection and try again.")
            sys.exit(1)
    
    # Use spinner during search operation
    start_time = time.time()
    click.echo(f"Searching for: '{query}' in {dir_path}")
    
    # Start spinner for search operation
    ctx.spinner.start("Analyzing files and computing semantic matches")
    
    try:
        # Search with minimum similarity score of 0.4 by default
        results = ctx.searcher.search(query, dir_path, max(50, top_k * 2), similarity, force_reindex=False)
        search_time = time.time() - start_time
        
        # Stop spinner with appropriate message
        ctx.spinner.stop()
        
        if not results:
            click.echo(f"\nNo results found with similarity score ≥ {similarity:.2f} in {search_time:.2f} seconds.")
            click.echo(f"Try lowering the similarity score with --similarity option or try a different query.")
            return
        
        # Show all results or just top-k based on user preference
        display_results = results if all else results[:top_k]
        
        click.echo(f"\nFound {len(display_results)} results in {search_time:.2f} seconds:\n")
        
        # Import needed function here to avoid circular imports
        from seekly.file_processor import extract_relevant_code_snippet
        
        for i, (file_path, score) in enumerate(display_results, 1):
            # Format the result line with clear relevance score
            relevance_indicator = "★ " if score > 0.7 else "  "
            result_line = f"{i}. {relevance_indicator}{file_path}: {score:.4f}"
            click.echo(result_line)
            
            # Show code snippets if enabled
            if snippets:
                abs_file_path = os.path.join(dir_path, file_path) if not os.path.isabs(file_path) else file_path
                code_lines = extract_relevant_code_snippet(abs_file_path, query)
                
                if code_lines:
                    click.echo("\n   Relevant code:")
                    for j, line in enumerate(code_lines, 1):
                        click.echo(f"   {j}: {line}")
                    click.echo("")  # Add empty line after snippet
    except Exception as e:
        # Make sure to stop spinner if an error occurs
        ctx.spinner.stop()
        click.echo(f"Error during search: {str(e)}")
        sys.exit(1)


@cli.command(help="Clear cached data to free up disk space")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.option("--all", "-a", is_flag=True, help="Clear both model and embeddings cache")
@click.option("--embeddings", "-e", is_flag=True, help="Clear only embedding cache")
@click.option("--model", "-m", is_flag=True, help="Clear only model cache")
@click.option("--dir", "-d", type=click.Path(exists=True), help="Clear cache for specific directory only")
@pass_seekly_context
def clear(ctx, yes: bool = False, all: bool = False, embeddings: bool = False, model: bool = False, dir: str = None):
    """
    Clear cached data to free up disk space.
    
    Examples:
      seekly clear --all --yes
      seekly clear --embeddings --dir ~/projects
      seekly clear --model
    """
    # Get cache directories
    model_cache_dir = os.path.join(str(Path.home()), ".seekly", "model_cache")
    embeddings_cache_dir = os.path.join(str(Path.home()), ".seekly", "cache")
    
    # Default to clearing all cache if nothing specific is selected
    if not any([all, embeddings, model]):
        all = True
    
    # Determine what to clear
    clear_embeddings = all or embeddings
    clear_model = all or model
    
    # Display what will be cleared
    components = []
    if clear_embeddings:
        components.append("embedding cache")
    if clear_model:
        components.append("model cache")
    
    target = f"for directory '{dir}'" if dir else "for all directories"
    clear_message = f"This will delete {' and '.join(components)} {target}"
    
    # Confirm with user unless --yes is used
    if not yes and not click.confirm(f"{clear_message}. Continue?"):
        click.echo("Operation cancelled.")
        return
    
    try:
        files_cleared = 0
        space_freed = 0
        
        # Clear model cache if requested
        if clear_model and os.path.exists(model_cache_dir):
            if dir:
                click.echo("Note: Model cache is shared across all directories")
                
            for file in os.listdir(model_cache_dir):
                file_path = os.path.join(model_cache_dir, file)
                try:
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        os.unlink(file_path)
                        files_cleared += 1
                        space_freed += size
                except Exception as e:
                    click.echo(f"Error deleting {file_path}: {e}")
        
        # Clear embeddings cache if requested
        if clear_embeddings and os.path.exists(embeddings_cache_dir):
            for file in os.listdir(embeddings_cache_dir):
                # If directory is specified, only clear cache for that directory
                if dir:
                    dir_hash = str(hash(os.path.abspath(os.path.expanduser(dir))))
                    if not file.startswith(f"embeddings_{dir_hash}"):
                        continue
                        
                file_path = os.path.join(embeddings_cache_dir, file)
                try:
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        os.unlink(file_path)
                        files_cleared += 1
                        space_freed += size
                except Exception as e:
                    click.echo(f"Error deleting {file_path}: {e}")
        
        # Report what was cleared
        if files_cleared > 0:
            readable_size = format_size(space_freed)
            click.echo(f"Cache cleared: {files_cleared} files removed ({readable_size} freed)")
        else:
            click.echo("No cache files were found to clear")
        
    except Exception as e:
        click.echo(f"Error clearing cache: {e}")


@cli.command(help="Show information about Seekly status")
@pass_seekly_context
def info(ctx):
    """
    Display information about Seekly status and cached data.
    
    Examples:
      seekly info
    """
    # Get cache directories
    model_cache_dir = os.path.join(str(Path.home()), ".seekly", "model_cache")
    embeddings_cache_dir = os.path.join(str(Path.home()), ".seekly", "cache")
    
    click.echo("Seekly Information")
    click.echo("=================")
    
    # Check if model is loaded, load if necessary for info
    is_model_loaded = ctx.searcher.is_model_loaded()
    if not is_model_loaded:
        try:
            is_model_loaded = ctx.searcher.load_model(verbose_override=False)
        except:
            pass
    
    # Display model info if available
    if is_model_loaded:
        click.echo(f"Model: {ctx.searcher.model_name}")
        click.echo(f"Device: {ctx.searcher.device}")
    else:
        click.echo("Model: Not loaded")
    
    # Calculate cache sizes
    model_size = 0
    model_files = 0
    if os.path.exists(model_cache_dir):
        for file in os.listdir(model_cache_dir):
            file_path = os.path.join(model_cache_dir, file)
            if os.path.isfile(file_path):
                model_size += os.path.getsize(file_path)
                model_files += 1
    
    embeddings_size = 0
    embeddings_files = 0
    indexed_dirs = set()
    if os.path.exists(embeddings_cache_dir):
        for file in os.listdir(embeddings_cache_dir):
            file_path = os.path.join(embeddings_cache_dir, file)
            if os.path.isfile(file_path):
                embeddings_size += os.path.getsize(file_path)
                embeddings_files += 1
                # Extract directory hash from filename
                if file.startswith("embeddings_"):
                    dir_hash = file.split("_")[1].split(".")[0]
                    indexed_dirs.add(dir_hash)
    
    # Display cache information
    click.echo(f"\nCache Status:")
    click.echo(f"  Model cache: {model_files} files ({format_size(model_size)})")
    click.echo(f"  Embeddings: {embeddings_files} files ({format_size(embeddings_size)})")
    click.echo(f"  Indexed directories: {len(indexed_dirs)}")
    
    # Usage hints
    click.echo("\nQuick Tips:")
    click.echo("  • Search:  seekly search \"function that calculates average\" --dir ~/projects --top-k 5")
    click.echo("  • High relevance search:  seekly search \"error handling\" --similarity 0.6")
    click.echo("  • Open file: seekly open \"main config file\" --dir ~/projects")
    click.echo("  • Clear:   seekly clear --all")
    click.echo("  • Help:    seekly --help")


@cli.command(help="Open a file that matches your description")
@click.argument("query", required=True)
@click.option("--dir", "-d", default=".", show_default=True, type=click.Path(exists=True),
              help="Directory to search in")
@click.option("--editor", "-e", help="Editor to use (defaults to system default)")
@pass_seekly_context
def open(ctx, query: str, dir: str, editor: str = None):
    """
    Find and open a file that best matches your description.
    
    Examples:
      seekly open "main configuration file"
      seekly open "utility functions for string manipulation" --dir ~/src
      seekly open "HTTP client implementation" --editor code
    """
    # Normalize and expand directory path
    dir_path = os.path.abspath(os.path.expanduser(dir))
    
    if not os.path.isdir(dir_path):
        click.echo(f"Error: Directory '{dir}' does not exist", err=True)
        sys.exit(1)
    
    # Auto-load the model if needed - use spinner for visual feedback
    if not ctx.searcher.is_model_loaded():
        try:
            # Start spinner for model loading
            ctx.spinner.start("Loading semantic search model")
            
            # Load the model
            success = ctx.searcher.load_model(verbose_override=False)
            
            # Stop spinner
            if success:
                ctx.spinner.stop("Model loaded successfully!")
            else:
                ctx.spinner.stop("Failed to load model")
                click.echo("Error: Failed to load semantic search model.")
                sys.exit(1)
        except Exception as e:
            ctx.spinner.stop()
            click.echo(f"Error loading model: {str(e)}")
            sys.exit(1)
    
    # Search for the best matching file with spinner
    click.echo(f"Finding file that matches: '{query}'")
    
    # Start spinner for search operation
    ctx.spinner.start("Searching for relevant files")
    
    try:
        # Perform the search
        results = ctx.searcher.search(query, dir_path, 1, similarity=0.3)
        
        # Stop spinner
        ctx.spinner.stop()
        
        if not results:
            click.echo("No matching files found.")
            return
        
        # Get the top result
        file_path, score = results[0]
        abs_file_path = os.path.join(dir_path, file_path) if not os.path.isabs(file_path) else file_path
        
        # Show which file we're opening
        click.echo(f"Opening: {file_path} (relevance: {score:.4f})")
        
        try:
            # Determine how to open the file
            if editor:
                os.system(f'{editor} "{abs_file_path}"')
            else:
                # Use platform-specific method to open with default program
                if sys.platform.startswith('darwin'):  # macOS
                    os.system(f'open "{abs_file_path}"')
                elif sys.platform.startswith('win'):   # Windows
                    os.system(f'start "" "{abs_file_path}"')
                else:  # Linux and others
                    os.system(f'xdg-open "{abs_file_path}"')
            
            click.echo(f"File opened successfully.")
        except Exception as e:
            click.echo(f"Error opening file: {str(e)}")
            click.echo(f"File path: {abs_file_path}")
            
    except Exception as e:
        # Make sure to stop spinner if an error occurs
        ctx.spinner.stop()
        click.echo(f"Error during search: {str(e)}")
        sys.exit(1)


@cli.command(name="list", help="List supported file extensions")
@click.option("--group", "-g", is_flag=True, help="Group extensions by language")
@pass_seekly_context
def list_extensions(ctx, group: bool):
    """
    Display all file extensions supported by Seekly search.
    
    Examples:
      seekly list
      seekly list --group
    """
    from seekly import SUPPORTED_EXTENSIONS
    
    # Count total extensions
    total = len(SUPPORTED_EXTENSIONS)
    click.echo(f"Seekly supports {total} file extensions:")
    
    if group:
        # Define extension groups (language families)
        extension_groups = {
            "Python": ['.py', '.ipynb', '.pyi'],
            "JavaScript/TypeScript": ['.js', '.jsx', '.ts', '.tsx'],
            "Web": ['.html', '.htm', '.css', '.scss', '.sass', '.less', '.vue', '.svelte'],
            "C/C++": ['.c', '.cpp', '.cc', '.h', '.hpp'],
            "Java/JVM": ['.java', '.kt', '.scala', '.groovy'],
            "C#/.NET": ['.cs', '.vb', '.fs', '.xaml'],
            "Go": ['.go'],
            "Ruby": ['.rb'],
            "PHP": ['.php'],
            "Rust": ['.rs'],
            "Swift": ['.swift'],
            "Shell": ['.sh', '.bash', '.zsh', '.fish', '.ps1'],
            "Documentation": ['.md', '.markdown', '.rst', '.txt', '.adoc', '.tex'],
            "Config": ['.yml', '.yaml', '.toml', '.ini', '.conf', '.cfg', '.properties', '.json'],
            "Other": []
        }
        
        # Categorize extensions
        categorized = set()
        for group_name, exts in extension_groups.items():
            matching_exts = sorted([ext for ext in SUPPORTED_EXTENSIONS if ext in exts])
            categorized.update(matching_exts)
            if matching_exts:
                click.echo(f"\n{group_name}:")
                # Print in columns
                for i in range(0, len(matching_exts), 6):
                    row = matching_exts[i:i+6]
                    click.echo("  " + "  ".join(f"{ext:<7}" for ext in row))
        
        # Add uncategorized extensions to "Other"
        other_exts = sorted([ext for ext in SUPPORTED_EXTENSIONS if ext not in categorized])
        if other_exts:
            click.echo("\nOther:")
            for i in range(0, len(other_exts), 6):
                row = other_exts[i:i+6]
                click.echo("  " + "  ".join(f"{ext:<7}" for ext in row))
    else:
        # Just list all extensions alphabetically in columns
        sorted_extensions = sorted(SUPPORTED_EXTENSIONS)
        for i in range(0, len(sorted_extensions), 8):
            row = sorted_extensions[i:i+8]
            click.echo("  " + "  ".join(f"{ext:<6}" for ext in row))


@cli.command(help="Show all available command options")
def options():
    """
    Display all available options and parameters for Seekly commands.
    
    Examples:
      seekly options
    """
    click.echo("Seekly Command Options")
    click.echo("====================\n")
    
    # Main search options
    click.echo("Search Options:")
    click.echo("  --dir, -d         Directory to search in (default: current directory)")
    click.echo("  --top-k, -k       Number of results to display (default: 10)")
    click.echo("  --similarity, -s  Minimum similarity threshold for results (0-1)")
    click.echo("  --snippets        Show code snippets in results (default: enabled)")
    click.echo("  --no-snippets     Hide code snippets in results")
    click.echo("  --all             Show all matching results (default)")
    click.echo("  --limit           Limit results to top-k matches")
    
    # Open command options
    click.echo("\nOpen File Options:")
    click.echo("  --dir, -d         Directory to search in (default: current directory)")
    click.echo("  --editor, -e      Editor to use (default: system default)")
    
    # Clear command options
    click.echo("\nCache Clear Options:")
    click.echo("  --all, -a         Clear both model and embeddings cache")
    click.echo("  --embeddings, -e  Clear only embedding cache")
    click.echo("  --model, -m       Clear only model cache")
    click.echo("  --dir, -d         Clear cache for specific directory only")
    click.echo("  --yes, -y         Skip confirmation prompt")
    
    # Other options
    click.echo("\nGeneral Options:")
    click.echo("  --verbose, -v     Show detailed debug information")
    click.echo("  --help            Show help message for a command")
    
    # Advanced usage examples
    click.echo("\nAdvanced Usage Examples:")
    click.echo("  seekly search \"error handling\" --dir ~/projects --top-k 5 --similarity 0.6")
    click.echo("  seekly search \"database connection\" --no-snippets --limit")
    click.echo("  seekly open \"config file\" --editor code")
    click.echo("  seekly clear --embeddings --dir ~/specific-project")


def format_size(size_bytes):
    """Format bytes to human readable format (KB, MB, etc.)"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0 or unit == 'GB':
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0


if __name__ == "__main__":
    cli()