"""
Operaciones con rutas:
    - obtain_current_path: Obtener la ruta donde se está ejecutando el script
    - obtain_absolute_path: Obtener la ruta absoluta
    - change_current_path: Cambiar la ruta actual de ejecución del script
    - validate_path: Válidar si la ruta existe
    - join_path: Unir rutas en una sola
    - obtain_default_path: Obtener la ruta absoluta por defecto (PC o Google Colab)
    - obtain_downloads_path: Obtener la ruta para guardar las descargas
    - rename_exists_file: Renombrar un archivo sí existe en el destino

"""

import os
from pathlib import Path
from outputstyles import error, info, warning


def obtain_current_path(os_method: bool = False) -> str:
    """
    Obtener la ruta donde se está ejecutando el script

    Parameters:
    os_method (bool): Usar el paquete "os" y no "pathlib"

    Returns:
    str: Ruta absoluta actual
    """

    return os.getcwd() if os_method else str(Path().absolute())


def obtain_absolute_path(path_src: str | Path, os_method: bool = False) -> str:
    """
    Obtener la ruta absoluta

    Parameters:
    path_src (str | Path): Ruta relativa (No necesariamente debe existir)
    os_method (bool): Usar el paquete "os" y no "pathlib"

    Returns:
    str: Ruta absoluta
    """

    # Sanear la ruta relativa a un string
    path = str(path_src)

    return os.path.abspath(path) if os_method else str(Path(path).resolve())


def change_current_path(path_dst: str | Path) -> str | None:
    """
    Cambiar la ruta actual de ejecución del script

    Parameters:
    path_dst (str | Path): Destino de la nueva ruta (Debe existir)

    Returns:
    str: Nueva ruta cambiada
    None: Si no se pudo cambiar la ruta actual
    """

    # Construir rutas absolutas para evitar problemas con rutas relativas
    path = obtain_absolute_path(path_dst)

    # Cambiar la ruta actual
    try:

        os.chdir(path)

        return path

    except FileNotFoundError:

        print(error("No existe la ruta:", "ico"), info(path))

    except Exception as err:

        print(
            error("Error al cambiar hacia la ruta:", "ico"),
            info(path),
            "\n" + str(err)
        )


def validate_path(path_src: str | Path, os_method: bool = False, print_msg: bool = True) -> bool:
    """
    Válidar si la ruta existe

    Parameters:
    path (str | Path): Ruta a comprobar su existencia
    os_method (bool): Usar el módulo "os" y no "pathlib"
    print_msg (bool): Imprimir un mensaje si no existe la ruta

    Returns:
    bool: Booleano según la existencia de la ruta
    """

    # Comprobar que no este vacia la ruta
    if not path_src:

        print(warning("Debe insertar una ruta.", "ico"))

        return False

    # Construir rutas absolutas para evitar problemas con rutas relativas
    path = obtain_absolute_path(path_src)

    # Comprobar la existencia de la ruta
    result = os.path.exists(path) if os_method else Path(path).exists()

    # Imprimir un mensaje si no existe
    if not result and print_msg:

        print(error('No existe la ruta:', "ico"), info(path))

    return result


def join_path(*args: str, os_method: bool = False) -> str:
    """
    Unir rutas en una sola (Sí son rutas absolutas, prevalece la última)

    Parameters:
    args (list of str): Rutas a unir en una sola
    os_method (bool): Usar el paquete "os" y no "pathlib"

    Returns:
    str: Ruta unida
    """

    # Seleccionar solo los argumentos de tipo "string"
    args = (arg.strip() for arg in args if isinstance(arg, str))

    return os.path.join(*args) if os_method else str(Path().joinpath(*args))


def obtain_default_path(mount_GDrive: bool = False) -> str:
    """
    Obtener la ruta absoluta por defecto, según si se
    trabaja en la PC o en Google Colab

    Parameters:
    mount_GDrive (bool): Está montado GDriver o no

    Returns:
    str: Ruta por defecto absoluta
    """

    # Comprobar sí se está trabajando en Google Colab
    if os.getenv("COLAB_RELEASE_TAG"):

        # Retornar la ruta por defecto en Google Colab
        return "/content/drive/MyDrive" if mount_GDrive else "/content"

    # Retornar la ruta por defecto en la PC
    current_path = obtain_current_path()

    return join_path(current_path, "MyDrive") if mount_GDrive else current_path


def obtain_downloads_path(input_dir: str | None = None, mount_GDrive: bool = False) -> str:
    """
    Obtener la ruta para guardar las descargas

    Parameters:
    input_dir (str | None): Directorio o ruta para guardar las descargas
    mount_GDrive (bool): Está montado GDriver o no

    Returns:
    str: Ruta absoluta del directorio de descargas
    """

    # Obtener la ruta padre por defecto
    default_path = obtain_default_path(mount_GDrive)

    # Sí no se introdujo ninguna ruta
    if not (input_dir and isinstance(input_dir, str)):

        # Conformar una ruta por defecto para las descargas
        return join_path(default_path, "Downloads")

    # Sí la ruta por defecto, está contenida en la introducida
    if input_dir.startswith(default_path):

        # Usar la misma ruta introducida
        return input_dir

    # Unir la ruta por defecto con la introducida
    return join_path(default_path, input_dir)


def rename_exists_file(path_src: str | Path) -> str:
    """
    Renombrar un archivo sí existe en el destino

    Parameters:
    path_src (str | Path): Ruta del archivo

    Returns:
    str: Ruta del archivo con un nombre diferente
    """

    # Segmentar la ruta original
    path_src = Path(path_src).resolve()

    parent = path_src.parent
    name = path_src.stem
    ext = path_src.suffix

    # Conformar nueva ruta renombrada
    num = 1
    path_new = parent / f'{name}_{str(num)}{ext}'

    # Verificar que no exista la nueva ruta
    while validate_path(str(path_new), print_msg=False):

        # Sí existe, seguimos creando una nueva ruta hasta que no exista
        num += 1
        path_new = parent / f'{name}_{str(num)}{ext}'

    # Retornamos la ruta del archivo renombrado
    return str(path_new)
