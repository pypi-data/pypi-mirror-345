"""
Útiles de @dunieskysp

Operaciones con rutas:
    - obtain_current_path: Obtener la ruta donde se está ejecutando el script
    - obtain_absolute_path: Obtener la ruta absoluta
    - change_current_path: Cambiar la ruta actual de ejecución del script
    - validate_path: Válidar si la ruta existe
    - join_path: Unir rutas en una sola
    - obtain_default_path: Obtener la ruta absoluta por defecto (PC o Google Colab)
    - obtain_downloads_path: Obtener la ruta para guardar las descargas
    - rename_exists_file: Renombrar un archivo sí existe en el destino

Operaciones con directorios:
    - create_dir: Crear directorio
    - create_downloads_dir: Crear el directorio de las descargas
    - create_symbolic_link: Crear enlace simbólico
    - delete_dir: Eliminar un directorio o archivo
    - del_empty_dirs: Borrar recursivamente los sub-directorios vacios
    - select_dir_content: Seleccionar contenido de un directorio
    - move_dirs: Mover archivo(s) y directorio(s) hacia otro directorio
    - copy_dirs: Copiar archivo(s) y directorio(s) hacia otro directorio
    - rename_dir: Renombrar un archivo o directorio

Operaciones con archivos:
    - read_text_file: Leer un archivo de texto
    - write_text_file: Guardar texto en un archivo

Operaciones de saneamiento
    - truncate_filename: Truncar el nombre del archivo o directorio
    - sanitize_filename: Sanear el nombre de un archivo o directorio

Tamaño de archivos y directorios:
    - natural_size: Convertir los bytes a medidas más legibles
    - obtain_size: Obtener tamaño de un archivo o directorio

Comprimir archivos y directorios:
    - compress: Comprimir un directorio o archivo
    - uncompress: Descomprimir un archivo

Otras funciones útiles:
    - obtain_url_from_html: Obtener la URL desde un archivo HTML
    - create_headers_decorates: Crear un encabezado decorado
    - clear_output: Limpiar salida en la Terminal según el SO
    - calc_img_dimensions: Calcular las dimensiones de una imagen
    - obtain_similar_vars: Obtener el valor o nombre de variables similares

Operaciones con listas:
    - remove_repeated_elements: Eliminar elementos repetidos

Operaciones con Diccionarios:
    - join_list_to_dict: Unir dos listas en un diccionario

Organizar directorios:
    - move_to_root: Mover archivos de los sub-directorios hacía el directorio raíz
    - move_files_to_subdir: Mover archivos hacia un sub-directorio dentro de los sub-directorios de nivel 1
    - organize_files_by_type: Organizar los archivos en directorios según su tipo
    - organize_files_by_name: Organizar los archivos en directorios según su nombre

Descargar archivos desde internet:
    - validate_and_resquest: Comprobar sí una URL es válida y accesible
    - obtain_filename: Obtener nombre del archivo que se va a descargar
    - update_download_logs: Actualizar los logs de la descarga
    - download_file: Descargar un archivo desde internet
    - organize_urls_data: Organizar en tuplas los datos de las URLs a descargar
    - update_description_pbar: Actualizar descripción de la barra de progreso principal
    - download_files: Descargar multiples archivos simultaneos desde internet


"""

# Útiles de rutas
from utilsdsp.utilsdsp_paths import obtain_current_path, obtain_absolute_path, change_current_path, validate_path, join_path, obtain_default_path, obtain_downloads_path, rename_exists_file


# Útiles de directorios
from utilsdsp.utilsdsp_dirs import create_dir, create_downloads_dir, create_symbolic_link, delete_dir, del_empty_dirs, select_dir_content, move_dirs, copy_dirs, rename_dir


# Útiles de archivos
from utilsdsp.utilsdsp_files import read_text_file, write_text_file


# Útiles de seneamiento de nombres de archivos
from utilsdsp.utilsdsp_sanitize import truncate_filename, sanitize_filename


# Obtener tamaño de archivos y directorios
from utilsdsp.utilsdsp_sizefile import natural_size, obtain_size


# Comprimir archivos y directorios
from utilsdsp.utilsdsp_compress import compress, uncompress


# Otras funciones útiles
from utilsdsp.utilsdsp_others import obtain_url_from_html, create_headers_decorates, clear_output, calc_img_dimensions, obtain_similar_vars

# Útiles de las Listas
from utilsdsp.utilsdsp_list import remove_repeated_elements


# Útiles de los Diccionarios
from utilsdsp.utilsdsp_dict import join_list_to_dict


# Organizar los directorios
from utilsdsp.utilsdsp_organizedirs import move_files_to_root, move_files_to_subdir, organize_files_by_type, organize_files_by_name


# Descargar archivos desde internet
from utilsdsp.utilsdsp_downloads import validate_and_resquest, obtain_filename, update_download_logs, organize_urls_data, update_description_pbar, download_file, download_files
