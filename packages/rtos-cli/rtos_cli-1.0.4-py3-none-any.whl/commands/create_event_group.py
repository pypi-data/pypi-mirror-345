"""
@file create_event_group.py
@brief Comando CLI para crear un grupo de eventos FreeRTOS en un proyecto basado en ESP32.
@author Efrain Reyes Araujo
@version 1.0
@date 2025-05-05

Este módulo define un grupo de eventos RTOS y lo integra al proyecto, agregándolo a los
archivos necesarios como project_config.h, main.cpp y README.md.
"""

import os
from utils.file_utils import append_to_file, insert_into_file
from utils.project_paths import get_project_config_path, get_main_cpp_path, update_readme


def create_event_group(group_name: str):
    """
    @brief Crea un grupo de eventos FreeRTOS global
    @param group_name Nombre del grupo de eventos
    """
    handle_name = f"xEventGroup_{group_name}"
    project_config = get_project_config_path()
    main_cpp = get_main_cpp_path()

    # 1. Agregar definición global
    definition = f"/// @brief Event Group for {group_name}\nextern EventGroupHandle_t {handle_name};\n"
    append_to_file(project_config, definition)

    # 2. Inicialización en main.cpp
    init_code = f"""
    // Initialize Event Group: {group_name}
    {handle_name} = xEventGroupCreate();
    if ({handle_name} == NULL) {{
        // TODO: Error handling
    }}
    """
    insert_into_file(main_cpp, init_code, marker="// ## INIT_EVENTS_MARKER")

    # 3. Agregar a README
    update_readme("Grupos de Eventos", f"- `{group_name}`")

    print(f"✅ Grupo de eventos '{group_name}' creado correctamente.")
