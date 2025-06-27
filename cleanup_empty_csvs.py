#!/usr/bin/env python3
"""
Script to remove empty CSV files (files with only headers) from a directory.
Usage: python cleanup_empty_csvs.py /path/to/directory
"""

import argparse
import os
import sys
import pathlib
import csv
from contextlib import ExitStack


def is_empty_csv(file_path, delimiter=','):
    """
    Check if a CSV file contains only headers and no data rows.
    
    Args:
        file_path: Path to the CSV file to check
        delimiter: Character used as field separator in the CSV file
        
    Returns:
        bool: True if the file has only headers, False otherwise
        
    Raises:
        UnicodeDecodeError: If the file cannot be decoded as text
        csv.Error: If there's an issue parsing the CSV
    """
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=delimiter)
            # Read the header
            next(reader, None)
            # Try to read the first data row
            return next(reader, None) is None
    except (UnicodeDecodeError, csv.Error) as e:
        print(f"Warning: Could not process {file_path}: {str(e)}", file=sys.stderr)
        # If we can't read it as a CSV, we shouldn't delete it
        return False


def cleanup_directory(directory_path, delimiter=',', dry_run=False, verbose=False, recursive=False):
    """
    Remove all empty CSV files from the specified directory.
    
    Args:
        directory_path: Path to the directory to clean
        delimiter: Character used as field separator in the CSV files
        dry_run: If True, only print what would be deleted without actually deleting
        verbose: If True, print detailed information about each file
        recursive: If True, process subdirectories recursively
        
    Returns:
        tuple: (number of files checked, number of files deleted)
    """
    if not os.path.isdir(directory_path):
        raise ValueError(f"The path '{directory_path}' is not a valid directory")
    
    files_checked = 0
    files_deleted = 0
    
    try:
        # Use pathlib to find all CSV files
        pattern = '**/*.csv' if recursive else '*.csv'
        csv_files = list(pathlib.Path(directory_path).glob(pattern))
        
        if verbose:
            print(f"Found {len(csv_files)} CSV files in {directory_path}" + 
                  (" and its subdirectories" if recursive else ""))
        
        # Process each CSV file
        for file_path in csv_files:
            files_checked += 1
            try:
                if is_empty_csv(file_path, delimiter):
                    if dry_run:
                        print(f"Would delete: {file_path}")
                    else:
                        os.remove(file_path)
                        files_deleted += 1
                        if verbose:
                            print(f"Deleted: {file_path}")
                elif verbose:
                    print(f"Keeping: {file_path} (contains data)")
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}", file=sys.stderr)
                
        return files_checked, files_deleted
    
    except Exception as e:
        print(f"Error scanning directory {directory_path}: {str(e)}", file=sys.stderr)
        return files_checked, files_deleted


def main():
    """Main function to parse arguments and execute the cleanup."""
    parser = argparse.ArgumentParser(
        description='Remove empty CSV files (files with only headers) from a directory'
    )
    parser.add_argument(
        'directory', 
        type=str, 
        help='Directory path containing CSV files to check'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true', 
        help='Show what would be deleted without actually deleting'
    )
    parser.add_argument(
        '-v', '--verbose', 
        action='store_true', 
        help='Print detailed information about each file'
    )
    parser.add_argument(
        '-r', '--recursive', 
        action='store_true', 
        help='Process subdirectories recursively'
    )
    parser.add_argument(
        '-d', '--delimiter',
        type=str,
        default=',',
        help='Field delimiter used in CSV files (default: ",", use "pipe" for "|")'
    )
    
    args = parser.parse_args()
    
    # Handle special delimiter values
    if args.delimiter.lower() == 'pipe':
        delimiter = '|'
    elif args.delimiter.lower() == 'tab':
        delimiter = '\t'
    else:
        delimiter = args.delimiter
    
    try:
        # Convert to absolute path for clarity in output
        directory_path = os.path.abspath(args.directory)
        
        if not os.path.exists(directory_path):
            print(f"Error: Directory '{directory_path}' does not exist", file=sys.stderr)
            return 1
            
        if not os.path.isdir(directory_path):
            print(f"Error: '{directory_path}' is not a directory", file=sys.stderr)
            return 1
            
        print(f"Processing directory: {directory_path}")
        print(f"Mode: {'Dry run (no files will be deleted)' if args.dry_run else 'Delete empty files'}")
        print(f"Delimiter: '{delimiter}'")
        print(f"Recursive: {'Yes' if args.recursive else 'No'}")
        
        files_checked, files_deleted = cleanup_directory(
            directory_path, 
            delimiter=delimiter,
            dry_run=args.dry_run, 
            verbose=args.verbose,
            recursive=args.recursive
        )
        
        print(f"\nSummary:")
        print(f"  Files checked: {files_checked}")
        print(f"  Empty files {('would be deleted' if args.dry_run else 'deleted')}: {files_deleted}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())




