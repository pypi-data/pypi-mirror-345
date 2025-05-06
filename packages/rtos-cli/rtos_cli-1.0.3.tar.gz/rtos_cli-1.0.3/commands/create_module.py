"""
@file create_module.py
@brief Command to create a new C++ module (.h/.cpp) in the project
@version 1.0.0
@date 2025-05-05
@license MIT
@author Efrain Reyes Araujo

@details
This module generates a new C++ module (.h and .cpp files) with the appropriate structure,
including Doxygen headers, and updates the include directory and README accordingly.
"""

import os

INCLUDE_DIR = "include"
SRC_DIR = "src"
README_PATH = "README.md"

H_TEMPLATE = """/**
 * @file {name}.h
 * @brief Header file for {name} module
 * @version 1.0.0
 * @date 2025-05-05
 * @author Auto-Generated
 */

#ifndef {macro}_H
#define {macro}_H

// Function declarations

#endif // {macro}_H
"""

CPP_TEMPLATE = """/**
 * @file {name}.cpp
 * @brief Source file for {name} module
 * @version 1.0.0
 * @date 2025-05-05
 * @author Efrain Reyes Araujo
 */

#include \"{name}.h\"

// Function definitions
"""

def run(module_name):
    macro = module_name.upper()
    header_path = os.path.join(INCLUDE_DIR, f"{module_name}.h")
    source_path = os.path.join(SRC_DIR, f"{module_name}.cpp")

    if os.path.exists(header_path) or os.path.exists(source_path):
        print(f"Module '{module_name}' already exists.")
        return

    os.makedirs(INCLUDE_DIR, exist_ok=True)
    os.makedirs(SRC_DIR, exist_ok=True)

    with open(header_path, "w") as hfile:
        hfile.write(H_TEMPLATE.format(name=module_name, macro=macro))

    with open(source_path, "w") as cppfile:
        cppfile.write(CPP_TEMPLATE.format(name=module_name))

    with open(README_PATH, "a") as readme:
        readme.write(f"\n- Module `{module_name}` created with rtos_cli.\n")

    print(f"Module '{module_name}' created at include/ and src/.")
