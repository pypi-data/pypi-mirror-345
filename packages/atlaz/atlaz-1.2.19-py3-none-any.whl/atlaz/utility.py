import json
import os
from pathlib import Path
import tiktoken
from typing import Optional, List
from atlaz.old_overview.main_overview import gather_repository

def count_tokens(string_inp):
    encc = tiktoken.encoding_for_model("gpt-4")
    encoded_str = encc.encode(string_inp)
    return len(encoded_str)

def build_code_prompt(file_contents: list[dict]):
    output_text = '\n'
    for file in file_contents:
        output_text += f'```{file["name"]}\n{file["content"]}\n```\n\n\n'
    return output_text[:-2]


def manual_overview(
    focus_directories: Optional[List[str]] = None,
    manual_ignore_files: Optional[List[str]] = None,
) -> str:
    if not focus_directories:          # catches both None and []
        focus_directories = [str(Path(__file__).resolve().parent)]

    # Turn None into a list and avoid the mutable-default pit-fall.
    manual_ignore_files = manual_ignore_files or []

    directory_data, directory_structure = gather_repository(
        script_path=Path(__file__).resolve().parent,
        focus_directories=focus_directories,
        manual_ignore_files=manual_ignore_files,
    )

    prompt = directory_structure + "\n\n" + build_code_prompt(directory_data)
    return prompt

from pathlib import Path
import os
from atlaz.old_overview.main_overview import gather_repository

def get_directory_data(focus_directories: list[str], manual_ignore_files: list[str]) -> list[dict]:
    """
    Uses gather_repository to scan the repository and return the file data.
    
    Returns a list of dictionaries, each with 'name' and 'content' keys.
    """
    directory_data, _ = gather_repository(
        script_path=Path(__file__).resolve().parent,
        focus_directories=focus_directories,
        manual_ignore_files=manual_ignore_files
    )
    return directory_data

def analyze_long_files(directory_data: list[dict], min_lines: int = 150) -> list[str]:
    """
    Returns a list of strings for files that are longer than min_lines.
    
    Each string includes the file name and its line count.
    """
    long_files = []
    for file in directory_data:
        line_count = len(file["content"].splitlines())
        if line_count > min_lines:
            long_files.append(f"{file['name']}: {line_count} lines")
    return long_files

def analyze_folders(focus_directories: list[str], ignore_set: set = None, threshold: int = 6) -> list[str]:
    """
    Walks through each focus directory and returns a list of folder summaries.
    
    Only folders with more than `threshold` items (files or subdirectories)
    are included, while ignoring any items in the provided ignore_set.
    """
    if ignore_set is None:
        ignore_set = {"__init__.py", "__pycache__"}
    
    folders_info = []
    
    for focus_dir in focus_directories:
        focus_path = Path(focus_dir)
        # Skip if the focus item is a file.
        if focus_path.is_file():
            continue
        
        # Walk through the directory tree.
        for root, dirs, files in os.walk(focus_path):
            # Filter out ignored directories for traversal.
            dirs[:] = [d for d in dirs if d not in ignore_set]
            if Path(root).name in ignore_set:
                continue
            
            # Combine subdirectories and files, filtering out ignored items.
            items = dirs + files
            filtered_items = [item for item in items if item not in ignore_set]
            if len(filtered_items) > threshold:
                try:
                    rel_path = Path(root).relative_to(focus_path)
                except ValueError:
                    rel_path = Path(root)
                folder_name = str(rel_path) if str(rel_path) != "." else focus_dir
                folders_info.append(f"Folder '{folder_name}': {len(filtered_items)} items")
    
    return folders_info

def build_report(long_files: list[str], folders_info: list[str]) -> str:
    """
    Combines the results from file and folder analyses into a final report.
    """
    report_lines = []
    
    if long_files:
        report_lines.append("Files longer than 150 lines:")
        report_lines.extend(long_files)
    else:
        report_lines.append("No files longer than 150 lines found.")
    
    if folders_info:
        report_lines.append("\nFolders with more than 6 items:")
        report_lines.extend(folders_info)
    else:
        report_lines.append("\nNo folders with more than 6 items found.")
    
    return "\n".join(report_lines)

def analyse_codebase(focus_directories: list[str], manual_ignore_files: list[str]) -> str:
    """
    Scans the repository using the given focus directories and ignore files.
    
    Returns a string report containing:
      1. A list of scripts (files) that are longer than 150 lines with their line counts.
      2. A list of folders that contain more than 6 items (files or subdirectories),
         excluding standard ignored items (e.g. '__init__.py' and '__pycache__').
    """
    directory_data = get_directory_data(focus_directories, manual_ignore_files)
    long_files = analyze_long_files(directory_data, min_lines=150)
    folders_info = analyze_folders(focus_directories, ignore_set={"__init__.py", "__pycache__"}, threshold=6)
    return build_report(long_files, folders_info)