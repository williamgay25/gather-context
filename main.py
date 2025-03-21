#!/usr/bin/env python3
"""
gather-context: A tool to collect code context from a directory for use with AI chatbots.
It walks through the current directory, collects code files, and copies their content to clipboard.
"""

import os
import fnmatch
import argparse
import pyperclip
import sys
from pathlib import Path

# Default file extensions to include
DEFAULT_EXTENSIONS = [
    '*.py', '*.js', '*.jsx', '*.ts', '*.tsx', 
    '*.html', '*.css', '*.scss', '*.sass',
    '*.java', '*.c', '*.cpp', '*.h', '*.hpp',
    '*.go', '*.rs', '*.rb', '*.php', '*.swift'
]

# Default directories and patterns to exclude
DEFAULT_EXCLUDES = [
    '**/node_modules/**', '**/venv/**', '**/.git/**', 
    '**/build/**', '**/dist/**', '**/__pycache__/**',
    '**/.env', '**/env/**', '**/.vscode/**', '**/.idea/**',
    '**/vendor/**', '**/bin/**', '**/obj/**',
    '**/*.min.js', '**/*.min.css', '**/package-lock.json',
    '**/yarn.lock', '**/Pipfile.lock', '**/poetry.lock'
]

def is_excluded(path, exclude_patterns):
    """Check if a path matches any of the exclusion patterns."""
    path_str = str(path)
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(path_str, pattern):
            return True
    return False

def is_included(path, include_patterns):
    """Check if a path matches any of the inclusion patterns."""
    path_str = str(path)
    for pattern in include_patterns:
        if fnmatch.fnmatch(path_str, pattern):
            return True
    return False

def format_file_content(path, content):
    """Format the file content with a header showing the relative path."""
    return f"\n\n--- {path} ---\n\n{content}"

def gather_context(directory=None, extensions=None, excludes=None, max_size=None, 
                  max_files=None, relative_to=None):
    """
    Gather code files from the specified directory, filtering by extensions and excludes.
    
    Args:
        directory: The directory to scan (default: current directory)
        extensions: List of file patterns to include
        excludes: List of patterns to exclude
        max_size: Maximum total size in KB to collect
        max_files: Maximum number of files to collect
        relative_to: Path to make file paths relative to
    
    Returns:
        A tuple of (collected_content, stats_dict)
    """
    # Set defaults
    directory = directory or os.getcwd()
    extensions = extensions or DEFAULT_EXTENSIONS
    excludes = excludes or DEFAULT_EXCLUDES
    max_size = max_size or float('inf')
    max_files = max_files or float('inf')
    relative_to = relative_to or directory
    
    # Convert to Path objects
    directory_path = Path(directory).resolve()
    relative_to_path = Path(relative_to).resolve()
    
    # Convert max_size to bytes
    max_size_bytes = max_size * 1024
    
    collected = []
    stats = {
        'total_files': 0,
        'included_files': 0,
        'excluded_files': 0,
        'empty_files': 0,
        'total_size_bytes': 0,
        'skipped_size_limit': 0,
        'skipped_file_limit': 0
    }
    
    # Walk through the directory tree
    for root, dirs, files in os.walk(directory_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not is_excluded(Path(root) / d, excludes)]
        
        for file in files:
            file_path = Path(root) / file
            
            # Skip if excluded or not included
            if is_excluded(file_path, excludes) or not is_included(file_path, extensions):
                stats['excluded_files'] += 1
                continue
            
            stats['total_files'] += 1
            
            # Check if we've reached file limit
            if stats['included_files'] >= max_files:
                stats['skipped_file_limit'] += 1
                continue
            
            # Read the file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Skip empty files
                if not content.strip():
                    stats['empty_files'] += 1
                    continue
                
                file_size = len(content.encode('utf-8'))
                
                # Check if we have enough space for this file
                if stats['total_size_bytes'] + file_size > max_size_bytes:
                    stats['skipped_size_limit'] += 1
                    continue
                
                # Calculate relative path
                try:
                    rel_path = file_path.relative_to(relative_to_path)
                except ValueError:
                    rel_path = file_path
                
                # Add the file to collected files
                collected.append((rel_path, content))
                stats['included_files'] += 1
                stats['total_size_bytes'] += file_size
                
            except (UnicodeDecodeError, IOError) as e:
                # Skip files that can't be read as text
                stats['excluded_files'] += 1
                continue
    
    # Format collected content
    if collected:
        formatted_content = ""
        for rel_path, content in collected:
            formatted_content += format_file_content(rel_path, content)
        
        # Add header with summary
        header = (
            f"Code context gathered from {directory_path}\n"
            f"Total files: {stats['included_files']}"
        )
        formatted_content = header + formatted_content
    else:
        formatted_content = f"No code files found in {directory_path}"
    
    return formatted_content, stats

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Gather code files from a directory for context in AI chatbots.'
    )
    parser.add_argument(
        '-d', '--directory', 
        help='Directory to scan (default: current directory)'
    )
    parser.add_argument(
        '-e', '--extensions', 
        help='Comma-separated list of file patterns to include (e.g., "*.py,*.js")'
    )
    parser.add_argument(
        '-x', '--exclude', 
        help='Comma-separated list of patterns to exclude'
    )
    parser.add_argument(
        '-m', '--max-size', 
        type=int, 
        help='Maximum total size in KB to collect'
    )
    parser.add_argument(
        '-f', '--max-files', 
        type=int, 
        help='Maximum number of files to collect'
    )
    parser.add_argument(
        '-r', '--relative-to',
        help='Path to make file paths relative to'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file (default: copy to clipboard)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print verbose statistics'
    )
    
    args = parser.parse_args()
    
    # Process arguments
    extensions = args.extensions.split(',') if args.extensions else None
    excludes = args.exclude.split(',') if args.exclude else None
    
    # Gather context
    content, stats = gather_context(
        directory=args.directory,
        extensions=extensions,
        excludes=excludes,
        max_size=args.max_size,
        max_files=args.max_files,
        relative_to=args.relative_to
    )
    
    # Output results
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Context written to {args.output}")
    else:
        try:
            pyperclip.copy(content)
            print("Context copied to clipboard!")
        except Exception as e:
            print(f"Error copying to clipboard: {e}", file=sys.stderr)
            print("Printing to stdout instead:")
            print(content)
    
    # Print statistics if verbose
    if args.verbose:
        kb_total = stats['total_size_bytes'] / 1024
        print(f"\nStatistics:")
        print(f"  Files included: {stats['included_files']}")
        print(f"  Files excluded: {stats['excluded_files']}")
        print(f"  Empty files skipped: {stats['empty_files']}")
        print(f"  Total size: {kb_total:.2f} KB")
        
        if stats['skipped_size_limit'] > 0:
            print(f"  Files skipped due to size limit: {stats['skipped_size_limit']}")
        if stats['skipped_file_limit'] > 0:
            print(f"  Files skipped due to file count limit: {stats['skipped_file_limit']}")

if __name__ == "__main__":
    main()