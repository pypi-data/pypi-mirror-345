# rtos_cli/utils/project_paths.py

import os

# Obtener la ruta al archivo de configuración del proyecto
def get_project_config_path():
    """
    Obtiene la ruta al archivo 'project_config.h' en el proyecto.
    """
    # Suponiendo que 'project_config.h' está en el directorio raíz del proyecto
    return os.path.join(os.getcwd(), "project_config.h")

# Obtener la ruta al archivo 'main.cpp' del proyecto
def get_main_cpp_path():
    """
    Obtiene la ruta al archivo 'main.cpp' en el proyecto.
    """
    # Suponiendo que 'main.cpp' está en el directorio 'src'
    return os.path.join(os.getcwd(), "src", "main.cpp")

# Actualizar el archivo README.md con información sobre el temporizador creado
def update_readme(section, content):
    """
    Actualiza el archivo README.md con una nueva sección y contenido.
    """
    readme_path = os.path.join(os.getcwd(), "README.md")
    
    # Agregar nueva sección al final del README.md
    with open(readme_path, 'a') as readme_file:
        readme_file.write(f"\n## {section}\n{content}\n")