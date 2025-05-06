# utils/readme_updater.py
"""
@file readme_updater.py
@brief Handles automatic updates to the project's README.md with new tasks, variables, and queues
@version 1.2.0
@date 2025-05-05
@license MIT
@author Efrain Reyes Araujo
"""
import os

def append_section(header, content):
    """
    @brief Appends content to a section in README.md, creating it if it doesn't exist.
    @param header The section header (e.g., '## Tasks')
    @param content The line(s) to append under the section
    """
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        with open(readme_path, 'w') as f:
            f.write("# Proyecto FreeRTOS ESP32\n\n")

    with open(readme_path, 'r') as f:
        lines = f.readlines()

    section_index = None
    for i, line in enumerate(lines):
        if line.strip() == header.strip():
            section_index = i
            break

    if section_index is not None:
        insert_index = section_index + 1
        while insert_index < len(lines) and lines[insert_index].strip().startswith("-"):
            insert_index += 1
        lines.insert(insert_index, content)
    else:
        lines.append(f"\n{header}\n{content}")

    with open(readme_path, 'w') as f:
        f.writelines(lines)
