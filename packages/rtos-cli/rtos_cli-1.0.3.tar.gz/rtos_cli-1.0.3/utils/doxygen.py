# utils/doxygen.py
"""
@file doxygen.py
@brief Utility to generate Doxygen-compatible documentation blocks
@version 1.0.0
@date 2025-05-05
@license MIT
@author Efrain Reyes Araujo
"""

def generate_task_doc(task_name):
    """
    @brief Generate a Doxygen block for a FreeRTOS task
    @param task_name Name of the task
    @return str - Doxygen formatted string
    """
    return f"""/**
 * @brief Task {task_name}
 * @details FreeRTOS task created by RTOS CLI.
 *
 * @return void
 */"""

def generate_variable_doc(var_name, var_type):
    """
    @brief Generate a Doxygen comment for a global variable
    @param var_name Variable name
    @param var_type Type of the variable
    @return str - Doxygen formatted comment
    """
    return f"""/**
 * @brief Global variable '{var_name}' of type '{var_type}'
 */"""

def generate_queue_doc(queue_name, item_type, length):
    """
    @brief Generate a Doxygen comment for a FreeRTOS queue
    @param queue_name Queue name
    @param item_type Type of items in the queue
    @param length Queue length
    @return str - Doxygen comment block
    """
    return f"""/**
 * @brief Queue '{queue_name}'
 * @details Queue of type {item_type} with length {length}.
 */"""
