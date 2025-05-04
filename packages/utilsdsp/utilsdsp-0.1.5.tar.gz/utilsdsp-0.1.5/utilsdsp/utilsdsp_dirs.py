"""
Operaciones con directorios:
    - create_dir: Crear directorio
    - create_downloads_dir: Crear el directorio de las descargas
    - create_symbolic_link: Crear enlace simbólico

    - delete_dir: Eliminar un directorio o archivo
    - del_empty_dirs: Borrar recursivamente los sub-directorios vacios

    - select_dir_content: Seleccionar contenido de un directorio
    
    - __prepare_paths: Preparar las rutas para mover, copiar y renombrar directorios
    - move_dirs: Mover archivo(s) y directorio(s) hacia otro directorio
    - copy_dirs: Copiar archivo(s) y directorio(s) hacia otro directorio
    - rename_dir: Renombrar un archivo o directorio
"""

import os
from pathlib import Path
from shutil import rmtree, move, copyfile, copytree
from outputstyles import error, success, warning, info, bold
from utilsdsp import obtain_default_path, obtain_downloads_path, validate_path


# NOTE: Crear directorios.
def create_dir(path_src: str | Path, parents: bool = True, print_msg: bool = False) -> str | None:
    """
    Crear directorio (Crea o no el directorio padre si no existe)

    Parameters:
    path_src (str | Path): Ruta del directorio a crear
    parents (bool): Crear o no el directorio padre si no existe
    print_msg (bool): Imprimir mensaje satisfactorio o de advertencia

    Returns:
    str: Ruta absoluta del directorio creado
    None: Sí no se pudo crear el directorio
    """

    # Comprobar que no este vacia la ruta
    if not path_src:

        print(warning("Debe insertar una ruta.", "ico"))

        return

    # Construir rutas absolutas y un objeto Path
    path = Path(path_src).resolve()

    try:

        # Crear el nuevo directorio recursivamente o no
        path.mkdir(parents=parents)

        # Imprimir mensaje satisfatorio
        if print_msg:
            print(success("Creado:", "ico"), info(path))

        return str(path)

    # Si el directorio ya existía
    except FileExistsError:

        # Imprimir mensaje de advertencia
        if print_msg:
            print(warning("Ya existe:", "ico"), info(path))

        return str(path)

    # Si los directorios padres no existen
    except FileNotFoundError as err:

        # Imprimir mensaje de error
        print(
            error("No existe el directorio padre de:", "ico"),
            info(path),
            "\n" + str(err)
        )

    # Sí no se pudo crear el directorio
    except OSError as err:

        # Imprimir mensaje de error
        print(
            error("Error al crear:", "btn_ico"),
            info(path),
            "\n" + str(err)
        )


def create_downloads_dir(input_dir: str | None = None, mount_GDrive: bool = False, print_msg: bool = False) -> str:
    """
    Crear el directorio de las descargas

    Parameters:
    input_dir (str | None): Directorio para guardar las descargas
    mount_GDrive (bool): Está montado GDriver o no
    print_msg (bool): Imprimir mensaje al crear el directorio

    Returns:
    str: Ruta absoluta del directorio de descargas
    """

    # Obtener la ruta padre por defecto
    default_path = obtain_default_path(mount_GDrive)

    # Obtener la ruta para guardar las descargas
    downloads_path = obtain_downloads_path(input_dir, mount_GDrive)

    # Crear el directorio de descargas
    downloads_dir = create_dir(downloads_path, print_msg=print_msg)

    # En caso de que haya ocurrido algún error al crear el directorio
    if not downloads_dir:

        # Advertir que se va a usar la ruta por defecto
        print(
            warning("Se va a usar:", "ico"),
            info(default_path)
        )

        # Retornar la ruta padre por defecto
        return default_path

    # Retornar la ruta del directorio creado
    return downloads_dir


def create_symbolic_link(path_src: str | Path, path_dst: str | Path, delete_dst: bool = False) -> str | None:
    """
    Crear enlace simbólico

    Parameters:
    path_src (str | Path): Ruta del directorio o archivo original
    path_dst (str | Path): Ruta del directorio padre de destino
    delete_dst (bool): Borrar el destino sí existe

    Returns:
    str: Ruta absoluta del enlace simbólico
    None: Sí no se creó el enlace simbólico
    """

    # Comprobar que existan las rutas de origen y destino
    if not (validate_path(path_src) and validate_path(path_dst)):
        return

    # Construir rutas absolutas y un objeto Path
    path_src = Path(path_src).resolve()
    path_dst = Path(path_dst).resolve()

    # Ruta absoluta del enlace simbólico
    symbolic_link = path_dst / path_src.name

    # Comprobar sí existe el destino
    if symbolic_link.exists():

        # Sí no se debe borrar
        if not delete_dst:

            print(warning("Ya existe:", "ico"), info(symbolic_link))

            return

        # Eliminar el destino
        if symbolic_link.is_symlink():

            symbolic_link.unlink()

        else:

            delete_dir(symbolic_link)

    # Crear el enlace simbólico
    try:

        symbolic_link.symlink_to(path_src)

        return str(symbolic_link)

    except Exception as err:

        print(
            error("Error al crear el enlace simbólico en:", "ico"),
            info(symbolic_link),
            "\n" + str(err)
        )


# NOTE: Eliminar directorios.
def delete_dir(path_src: str | Path, print_msg: bool = True) -> bool:
    """
    Eliminar un directorio o archivo

    Parameters:
    path_src (str | Path): Ruta del directorio o archivo a eliminar
    print_msg (bool): Imprimir mensaje de error

    Returns:
    bool: Booleano según si se pudo eliminar o no
    """

    # Comprobar que exista el directorio o archivo
    if not validate_path(path_src):

        return False

    # Construir rutas absolutas y un objeto Path
    path = Path(path_src).resolve()

    try:

        # Eliminar un archivo
        if path.is_file():

            os.remove(path)

            return True

        # Eliminar un directorio
        else:

            rmtree(path)

            return True

    except Exception as err:

        # Imprimir mensaje de error si no se pudo eliminar
        if print_msg:
            print(
                error("Error al eliminar:", "btn_ico"),
                info(path),
                "\n" + str(err)
            )

        return False


def del_empty_dirs(path_src: str | Path, print_msg: bool = True) -> None:
    """
    Borrar recursivamente los sub-directorios vacios

    Parameters:
    path_src (str | Path): Ruta del directorio raíz
    print_msg (bool): Imprimir mensaje satisfactorio

    Returns:
    None
    """

    # Comprobar que exista el directorio raíz
    if not validate_path(path_src):
        return

    # Construir rutas absolutas y un objeto Path
    path = Path(path_src).resolve()

    # Comprobar que sea un directorio
    if not path.is_dir():

        print(warning("No es un directorio:", "ico"), info(path))
        return

    # Obtener todos los subdirectorios
    all_subdirs = [item for item in path.rglob("*") if item.is_dir()]

    # Ordenar reversamente la lista
    all_subdirs.sort(reverse=True)

    # Elementos borrados
    deleted = 0

    # Borrar todos los subdirectorios vacios
    for subdir in all_subdirs:

        # Verificar que este vacio el directorio
        if not any(subdir.glob("*")):

            try:

                # Borrar sub-directorio actual
                subdir.rmdir()

                if print_msg:
                    print(success("Borrado:", "ico"), info(subdir))

                deleted += 1

            except Exception as err:

                print(
                    error("No se pudo borrar:", "ico"),
                    info(subdir),
                    "\n" + str(err)
                )

    # Mostrar las estadisticas del borrado
    if deleted == 0:

        print(bold("No hay subdirectorios vacios en:"), info(path))

    elif deleted == 1:

        print(
            success(f"Eliminado 1 directorio vacio de:", "ico"),
            info(path)
        )

    else:

        print(
            success(f"Eliminados {deleted} directorios vacios de:", "ico"),
            info(path)
        )


# NOTE: Seleccionar archivos y subdirectorios dentro de un directorio.
def select_dir_content(path_src: str | Path, file_type: str | None = None, recursive: bool = False, print_msg: bool = True) -> list | None:
    """
    Seleccionar contenido de un directorio

    Parameters:
    path_src (str | Path): Ruta del directorio raíz
    file_type (str | None): Tipos de archivos a seleccionar
    recursive (bool): Buscar en los sub-directorios también
    print_msg (bool): Imprimir mensaje sí no hay archivos

    Returns:
    list: Lista de rutas (Path object) del contenido encontrado
    None: Si no existe o no es un directorio la ruta de origen
    """

    # Comprobar que exista el directorio raíz
    if not validate_path(path_src):
        return

    # Construir rutas absolutas y un objeto Path
    path = Path(path_src).resolve()

    # Comprobar que sea un directorio
    if not path.is_dir():

        print(warning("No es un directorio:", "ico"), info(path))
        return

    # Definir el tipo de contenido a buscar
    file_type = f'*.{file_type}' if file_type else '*'

    # Buscar en el directorio raíz y en sus sub-directorios
    if recursive:

        result = [item for item in path.rglob(file_type)]

    # Buscar solo en el directorio raíz
    else:

        result = [item for item in path.glob(file_type)]

    # Comprobar que se haya encontrado contenido
    if not result and print_msg:

        if file_type in ["*", "*.*"]:

            msg = 'No hay contenido en:'

        else:

            msg = f'No hay archivos {file_type.upper().replace("*.","")} en:'

        print(warning(msg, "ico"), info(path))

    return result


# NOTE: Mover, copiar y renombrar.
def __prepare_paths(path_src: str | Path, path_dst: str | Path | None = None, overwrite: bool = False, rename: bool = False, new_name: str | None = None) -> tuple | None:
    """
    Preparar las rutas para mover, copiar y renombrar directorios

    Parameters:
    path_src (str | Path): Ruta del archivo o directorio de origen
    path_dst (str | Path | None): Ruta del directorio de destino
    overwrite (bool): Sobrescribir el destino sí existe
    rename (bool): Peparar datos para la función renombrar
    new_name (str | None): Nuevo nombre sí es para la función renombrar

    Returns:
    tuple: object Path - Ruta de origen (path_src),
           object Path - Ruta del directorio de destino (path_dst),
           object Path - Ruta absoluta final (path_final),
           mensaje pre-elaborado (msg)
    None: Sí no existe el origen, sí ya existe el destino final
          y no está "overwrite" activado y sí falló la creación
          del directorio de destino
    """

    # Comprobar que exista el archivo o directorio de origen
    if not validate_path(path_src):
        return

    # Construir rutas absolutas y un objeto Path
    path_src = Path(path_src).resolve()
    path_dst = Path(path_dst).resolve() if path_dst else path_src.parent

    # Ruta de destino final
    path_final = path_dst / new_name if rename else path_dst / path_src.name

    # Comprobar que no exista el destino final
    if path_final.exists():

        # Eliminamos el destino sí está "overwrite" activo
        if overwrite:

            delete_dir(path_final)

        else:

            print(warning("Ya existe:", "ico"), info(path_final))

            return

    # Crear el directorio de destino sí no existe
    if not create_dir(path_dst):

        return

    # Mensaje pre-elaborado
    msg = f'{info(path_src)}\n  '

    if rename:

        msg += f'{bold("a:")} {info(path_final)}'

    else:

        msg += f'{bold("hacia:")} {info(path_dst)}'

    # Retornar (Ruta de origen, directorio de destino, ruta final absoluta y msg)
    return path_src, path_dst, path_final, msg


def move_dirs(path_src: str | Path | list, path_dst: str | Path, print_msg: bool = True, overwrite: bool = False, file_type: str | None = None) -> str | None:
    """
    Mover archivo(s) y directorio(s) hacia otro directorio

    Parameters:
    path_src (str | Path | list): Ruta o lista de rutas de elemento(s) a mover
    path_dst (str | Path): Ruta del directorio al que se van a mover
    print_msg (bool): Imprimir un mensaje satisfactorio
    overwrite (bool): Sobrescribir el destino sí existe
    file_type (srt): Tipo de archivos a mover

    Returns:
    str: Ruta del elemento movido sí no es una lista "path_src"
    None: Sí no se pudo mover el elemento o es una lista "path_src"
    """

    # Procesar una lista de elementos a mover
    if isinstance(path_src, list):

        # Preparar el mensaje a imprimir
        if file_type and file_type != "*":

            file_type = file_type.upper()

            msg = bold(f'Moviendo archivos {file_type} hacia: ')

        else:

            msg = bold(f'Moviendo elementos hacia: ')

        print(msg + info(path_dst), "\n") if print_msg else None

        # Llamar a la función recursivamente
        _ = [
            move_dirs(path, path_dst, print_msg, overwrite) for path in path_src
        ]

        # Romper la ejecución de la función
        return

    # Preparar las rutas para mover un solo elemento
    paths = __prepare_paths(path_src, path_dst, overwrite)

    if not paths:

        print("")

        return

    # Desempaquetar las variables necesarias
    path_src, path_dst, path_final, msg = paths

    # Mover el archivo o directorio
    try:

        move(path_src, path_dst)

        # Imprimir mensaje satisfactorio
        if print_msg:

            print(success("Movido:", "ico"), msg, "\n")

        return str(path_final)

    except Exception as err:

        print(error("Error al mover:", "ico"), msg, "\n" + str(err), "\n")


def copy_dirs(path_src: str | Path | list, path_dst: str | Path, print_msg: bool = True, overwrite: bool = False, file_type: str | None = None) -> str | None:
    """
    Copiar archivo(s) y directorio(s) hacia otro directorio

    Parameters:
    path_src (str | Path | list): Ruta o lista de rutas de elemento(s) a copiar
    path_dst (str | Path): Ruta del directorio al que se van a copiar
    print_msg (bool): Imprimir un mensaje satisfactorio
    overwrite (bool): Sobrescribir el destino sí existe

    Returns:
    str: Ruta del elemento copiado sí no es una lista "path_src"
    None: Sí no se pudo copiar el elemento o es una lista "path_src"
    """

    # Procesar una lista de elementos a copiar
    if isinstance(path_src, list):

        # Preparar el mensaje a imprimir
        if file_type:

            file_type = file_type.upper()

            msg = bold(f'Copiando archivos {file_type} hacia: ')

        else:

            msg = bold(f'Copiando elementos hacia: ')

        print(msg + info(path_dst), "\n") if print_msg else None

        # Llamar a la función recursivamente
        _ = [
            copy_dirs(path, path_dst, print_msg, overwrite) for path in path_src
        ]

        # Romper la ejecución de la función
        return

    # Preparar las rutas para copiar un solo elemento
    paths = __prepare_paths(path_src, path_dst, overwrite)

    if not paths:

        print("")

        return

    # Desempaquetar las variables necesarias
    path_src, path_dst, path_final, msg = paths

    # Copiar el archivo o directorio hacia su nuevo destino
    try:

        # Copiar un directorio
        if path_src.is_dir():

            copytree(path_src, path_final, dirs_exist_ok=True)

        # Copiar un archivo u otro
        else:

            copyfile(path_src, path_final)

        # Imprimir mensaje satisfactorio
        if print_msg:

            print(success("Copiado:", "ico"), msg, "\n")

        return str(path_final)

    except Exception as err:

        print(error("Error al copiar:", "ico"), msg, "\n" + str(err), "\n")


def rename_dir(path_src: str | Path, new_name: str, path_dst: str | Path | None = None,  print_msg: bool = True, overwrite: bool = False) -> str | None:
    """
    Renombrar un archivo o directorio
        - Se puede usar para mover archivos o directorios

    Parameters:
    path_src (str | Path): Ruta del archivo o directorio a renombrar
    new_name (str): Nuevo nombre del archivo o directorio a renombrar
    path_dst (str | Path | None): Ruta de destino
    print_msg (bool): Imprimir un mensaje satisfactorio
    overwrite (bool): Sobrescribir el destino sí existe

    Returns:
    str: Ruta absoluta del archivo o directorio renombrado
    None: Sí no se pudo renombrar el archivo o directorio
    """

    # Comprobar que el nuevo nombre no este vacio y sea un string
    if not (new_name and isinstance(new_name, str)):

        print(warning("El nuevo nombre no debe estar vacio y ser un texto.", "ico"))

        return

    # Preparar las rutas
    paths = __prepare_paths(
        path_src=path_src,
        path_dst=path_dst,
        overwrite=overwrite,
        rename=True,
        new_name=new_name
    )

    if not paths:

        return

    # Desempaquetar las variables necesarias
    path_src, path_dst, path_final, msg = paths

    # Renombrar el archivo o directorio
    try:

        path_src.rename(path_final)

        if print_msg:

            print(success("Renombrado", "ico"), msg, "\n")

        return str(path_final)

    except Exception as err:

        print(error("Error al renombrar:", "ico"), msg, "\n" + str(err), "\n")
