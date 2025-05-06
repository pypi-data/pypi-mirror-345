# utils/file_utils.py
"""
@file file_utils.py
@brief Utility functions for file operations in RTOS CLI
@author Efrain Reyes Araujo
@version 1.2.0
@date 2025-05-05
@license MIT
"""
import os

def insert_in_file(filepath, content, anchor):
    """
    @brief Insert content below a specific anchor comment in a file
    @param filepath Path to the target file
    @param content Code/content to insert
    @param anchor Marker line to look for
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()

    new_lines = []
    inserted = False

    for line in lines:
        new_lines.append(line)
        if anchor in line and not inserted:
            new_lines.append(content + '\n')
            inserted = True

    with open(filepath, 'w') as f:
        f.writelines(new_lines)

def append_to_file(filepath, content):
    """
    @brief Append content to end of a file
    @param filepath File path to append to
    @param content Text to append
    """
    with open(filepath, 'a') as f:
        f.write(content + '\n')

def create_file(path, content):
    """
    @brief Create a file with given content, or skip if it exists
    @param path Path to create the file at
    @param content Initial file contents
    """
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(content)
    else:
        print(f"⚠️  File '{path}' already exists. Skipped.")
