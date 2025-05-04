"""
Organizar directorios:
    - move_to_root: Mover archivos de los sub-directorios hacía el directorio raíz
    - move_files_to_subdir: Mover archivos hacia un sub-directorio dentro de los sub-directorios de nivel 1
    - organize_files_by_type: Organizar los archivos en directorios según su tipo
    - organize_files_by_name: Organizar los archivos en directorios según su nombre
"""

from pathlib import Path
from outputstyles import warning, info, bold, error
from utilsdsp import validate_path, select_dir_content, move_dirs, del_empty_dirs, join_list_to_dict, join_path


def move_files_to_root(path_src: str | Path, file_type: str | None = None, delete_empty: bool = False, overwrite: bool = False, print_msg: bool = True) -> None:
    """
    Mover archivos de los sub-directorios hacía el directorio raíz

    Parameters:
    path_src (str | Path): Ruta del directorio raíz
    file_type (str | None): Tipos de archivos a mover
    delete_empty (bool): Eliminar las carpetas vacias
    overwrite (bool): Sobrescribir el destino sí existe
    print_msg (bool): Imprimir un mensaje satisfactorio

    Returns:
    None
    """

    # Comprobar que exista la ruta
    if not validate_path(path_src):

        return

    # Construir rutas absolutas y un objeto Path
    path_root = Path(path_src).resolve()

    # Seleccionar solo los archivos en los sub-directorios
    file_type = file_type if file_type else "*"

    files = [
        file for file in select_dir_content(path_root, file_type, True) if file.parent != path_root
    ]

    # Comprobar que existan archivos en los sub-directorios
    if not files:

        if file_type != "*":

            msg = f'No hay archivos {file_type.upper()} en los sub-directorios de:'

        else:

            msg = f'No hay archivos en los sub-directorios de:'

        print(warning(msg, "ico"), info(path_root))

        return

    # Mover todos los elementos seleccionados
    move_dirs(
        path_src=files,
        path_dst=path_root,
        print_msg=print_msg,
        overwrite=overwrite,
        file_type=file_type
    )

    # Borrar los sub-directorios vacios
    if delete_empty:

        del_empty_dirs(path_root, print_msg=print_msg)


def move_files_to_subdir(path_src: str | Path, subdir_name: str, file_type: str | None = None, overwrite: bool = False, print_msg: bool = True) -> None:
    """
    Crear un directorio dentro de los sub-directorios del nivel 1
    y mover los archivos seleccionados dentro de él

    Parameters:
    path_src (str | Path): Ruta del directorio raíz
    subdir_name (str): Nombre del nuevo sub-directorio
    file_type (str | None): Tipos de archivos a mover
    overwrite (bool): Sobrescribir el destino sí existe
    print_msg (bool): Imprimir un mensaje satisfactorio

    Returns:
    None
    """

    # Comprobar que exista la ruta
    if not validate_path(path_src):

        return

    # Construir rutas absolutas y un objeto Path
    path_src = Path(path_src).resolve()

    # Obtener todos los sub-directorios del nivel 1
    all_subdirs = [
        item for item in select_dir_content(path_src) if item.is_dir()
    ]

    # Comprobar que hayan subdirectorios en el nivel 1
    if not all_subdirs:

        print(warning(f'No hay sub-directorios en:', "ico"), info(path_src))

        return

    # Mover los archivos hacia el nuevo sub-directorio
    for subdir in all_subdirs:

        # Obtener los archivos del directorio actual
        file_type = file_type if file_type else "*"

        files = [item for item in select_dir_content(subdir, file_type)]

        # Continuamos sí no hay archivos
        if not files:

            print("")

            continue

        # Ruta del nuevo sub-directorio
        path_dst = subdir / subdir_name

        # Mover los archivos
        move_dirs(
            path_src=files,
            path_dst=path_dst,
            print_msg=print_msg,
            overwrite=overwrite,
            file_type=file_type
        )


def organize_files_by_type(path_src: str | Path, files_data: dict | list, path_dst: str | Path | None = None, overwrite: bool = False, print_msg: bool = True) -> None:
    """
    Organizar los archivos en directorios según su tipo

    Parameters:    
    path_src (str | Path): Ruta del directorio raíz a organizar
    files_data (dict | list): Diccionario o lista con los tipos de archivos y carpetas
    path_dst (str | Path | None): Ruta de destino
    overwrite (bool): Sobrescribir el destino sí existe
    print_msg (bool): Imprimir un mensaje satisfactorio

    Ej diccionario:
    - files_data = {
        "txt":"Textos",
        "jpg":"Imagenes"
    }

    Ej lista (Deben tener la misma longitud):
    - files_type = ["txt", "jpg"]
    - files_folder = ["Textos", "Imagenes"]
    - files_data = [files_type, files_folder]

    Returns:
    None
    """

    # Comprobar que exista la ruta
    if not validate_path(path_src):

        return

    # Construir rutas absolutas y objetos Path
    path_root = Path(path_src).resolve()
    path_dst = Path(path_dst).resolve() if path_dst else path_root

    # Preparar los datos (type, foldername) sí es una lista
    if isinstance(files_data, list) and len(files_data) == 2:

        types_and_folders = join_list_to_dict(files_data[0], files_data[1])

        if not types_and_folders:

            return

    # Preparar los datos (type, foldername) sí es un diccionario
    elif isinstance(files_data, dict):

        types_and_folders = files_data

    else:

        print(error('"files_data" no es un diccionario o una lista', "btn_ico"))

        return

    # Organizar los archivos en las carpetas correspondientes
    for ext, folder in types_and_folders.items():

        # Comprobar que que no esten vacios los valores (type, foldername)
        if not (ext and folder):

            print(
                warning("Los valores no deben estar vacios.", "ico"),
                "\n" + bold("Extensión:"),
                ext,
                "\n" + bold("Carpeta:"),
                folder,
                "\n"
            )

            continue

        # Buscar los archivos según la extensión
        files = select_dir_content(path_root, file_type=ext)

        # Continuamos sí no hay archivos
        if not files:

            print("")

            continue

        # Obtener la ruta del directorio de destino final
        path_folder = path_dst / folder

        # Mover los archivos
        move_dirs(
            path_src=files,
            path_dst=path_folder,
            print_msg=print_msg,
            overwrite=overwrite,
            file_type=ext
        )


def organize_files_by_name(path_src: str | Path, path_dst: str | Path | None = None, file_type: str | None = None, secondary: str | None = None, not_include: str | None = None, subdir: str | None = None, overwrite: bool = False, print_msg: bool = True) -> None:
    """
    Organizar los archivos en directorios según su nombre

    Pueden existir archivos principales y secundarios. Ej:
    - Principal: The Boys - Series.com.html
    - Secundario: The Boys Episodio 1 - Series.com.html

    Parameters:    
    path_src (str | Path): Ruta del directorio raiz a organizar
    path_dst (str | Path | None): Ruta del directorio de destino
    file_type (str | None): Tipos de archivos a organizar
    secondary (str | None): Texto único que identifica a los archivos secundarios (Episodio)
    not_include (str | None): Texto a eliminar del nombre de la carpeta ( - Series.com)
    subdir (str | None): Subdirectorio a crear dentro de las carpetas
    overwrite (bool): Sobrescribir el destino sí existe
    print_msg (bool): Imprimir un mensaje satisfactorio

    Returns:
    None
    """

    # Comprobar que exista la ruta
    if not validate_path(path_src):

        return

    # Construir rutas absolutas y objetos Path
    path_root = Path(path_src).resolve()
    path_dst = Path(path_dst).resolve() if path_dst else path_src

    # Obtener los archivos especificados del nivel 1
    file_type = file_type if file_type else "*"

    all_files = select_dir_content(path_root, file_type)

    if not all_files:

        return

    # Seleccionar los archivos principales y secundarios
    files_secondary = [
        item for item in all_files if secondary and secondary in item.name
    ]

    files_main = [item for item in all_files if not item in files_secondary]

    # Mover los archivos hacia sus carpetas correspondientes
    for file in files_main:

        # Obtener el nombre de la carpeta
        not_include = not_include if not_include else ""
        folder_name = file.stem.replace(not_include, "")

        # Ruta de la nueva carpeta
        new_folder = join_path(str(path_dst), folder_name, str(subdir))

        # Seleccionar los secundarios del archivos principal en turno
        files_sec = [
            item for item in files_secondary if item.stem.startswith(folder_name)
        ]

        # Mover el archivo principal y sus secundarios
        move_dirs(
            path_src=[file] + files_sec,
            path_dst=new_folder,
            print_msg=print_msg,
            overwrite=overwrite,
            file_type=file_type
        )
