# rtos_cli/commands/create_task.py
"""
@file create_task.py
@brief Command to create a new FreeRTOS task with .cpp/.h files and registration in main.cpp and project_config.h
@author Efrain Reyes Araujo
@version 1.2.0
@date 2025-05-05
@license MIT
"""
import os
from rtos_cli.utils import file_utils, readme_updater, doxygen

def run(task_name):
    print(f"\n🔧 Creating task '{task_name}'...")

    src_path = os.path.join("src", f"{task_name}.cpp")
    include_path = os.path.join("include", f"{task_name}.h")

    # Template contents for .cpp and .h
    h_content = f"""{doxygen.generate_header(f"{task_name}.h", f"Header for {task_name} task")}
#ifndef {task_name.upper()}_H
#define {task_name.upper()}_H

void {task_name}_task(void *pvParameters);

#endif  // {task_name.upper()}_H
"""

    cpp_content = f"""{doxygen.generate_header(f"{task_name}.cpp", f"Implementation of {task_name} task")}
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "{task_name}.h"

void {task_name}_task(void *pvParameters) {{
    while (true) {{
        // TODO: Implement task logic
        vTaskDelay(pdMS_TO_TICKS(1000));
    }}
}}
"""

    file_utils.write_file(src_path, cpp_content)
    file_utils.write_file(include_path, h_content)

    # Insert task declaration in project_config.h
    file_utils.insert_in_file("src/project_config.h", f"#include \"{task_name}.h\"", anchor="// -- TASK INCLUDES --")

    # Register task in main.cpp (this is an example, real logic may vary)
    task_registration = f"xTaskCreate({task_name}_task, \"{task_name}\", 4096, NULL, 1, NULL);"
    file_utils.insert_in_file("src/main.cpp", task_registration, anchor="// -- TASK REGISTRATION --")

    # Update README
    readme_updater.append_section("## Tasks\n", f"- {task_name}_task: Created using rtos_cli\n")

    print(f"✅ Task '{task_name}' created and registered.")
