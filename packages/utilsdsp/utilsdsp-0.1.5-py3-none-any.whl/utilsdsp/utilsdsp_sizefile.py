"""
Tamaño de archivos y directorios:
    - natural_size: Convertir los bytes a medidas más legibles
    - obtain_size_dir: Obtener el tamaño de un directorio
    - obtain_size_file: Obtener el tamaño de un archivo
    - obtain_size: Obtener tamaño de un archivo o directorio
"""

import os
from pathlib import Path
from outputstyles import error, info, warning
from utilsdsp import validate_path


def natural_size(size_file: int, unit: str | None = None) -> str:
    """
    Convertir los bytes a medidas más legibles (KB, MB, GB o TB)

    Parameters:
    size_file (int): Tamaño del archivo en bytes
    unit (str | None): Unidad a mostrar el resulado (KB, MB, GB o TB)

    Returns:
    srt: Devuelve el tamaño del archivo en bytes, KB, MB, GB o TB
    """

    # Comprobar que sea válido el tamaño del archivo o directorio.
    if not isinstance(size_file, int):

        return warning("El tamaño debe ser un número y mayor que 0.", "ico")

    # Comprobar que el tamaño sea mayor que 0
    if size_file <= 0:

        return "0 bytes"

    # Unidades y sus valores en que se va a expresar el resultado
    units = {
        "TB": 1024 ** 4,
        "GB": 1024 ** 3,
        "MB": 1024 ** 2,
        "KB": 1024,
        "BYTES": 1
    }

    # Sanear la unidad
    unit = unit.upper() if unit and isinstance(unit, str) else ""

    # Si la unidad introducida es válida
    if unit in units:

        # Convertir el tamaño a esa unidad
        size = size_file / units[unit]

    else:

        # Buscar la medida más acorde según la cantidad de bytes
        for unit, value in units.items():

            if size_file >= value:

                size = size_file / value

                break

    # Retornamos el tamaño obtenido redondeado y con su Unidad
    return f'{round(size, 2)} {unit.lower() if unit == "BYTES" else unit}'


def __obtain_size_dir(path_src: str | Path, unit: str | None = None, file_type: str = "*") -> str | None:
    """
    Obtener el tamaño de un directorio

    Parameters:
    path_src (str | Path): Ruta del directorio para determinar su tamaño
    unit (str | None): Unidad para dar el resulado (KB, MB, GB o TB)
    file_type (str): Tipos de archivos a seleccionar

    Returns:
    str: Suma del tamaño de todos los elementos en el directorio
    None: Sí la ruta no es válida o sí no es directorio
    """

    # Comprobar que exista el directorio
    if not validate_path(path_src):

        return

    # Construir rutas absolutas y un objeto Path
    path = Path(path_src).resolve()

    # Comprobar que sea un directorio
    if not path.is_dir():

        return f'{error("No es un directorio:", "ico")} {info(path)}'

    # Obtener la suma del tamaño de todos los archivos
    total_size = sum(
        [
            file.stat().st_size for file in path.rglob(f'*.{file_type}')
        ]
    )

    # Retornar el tamaño total con su unidad de medida
    return natural_size(total_size, unit) if total_size else "0 bytes"


def __obtain_size_file(path_src: str | Path, unit: str | None = None, method_stat: bool = False, method_getsize: bool = False) -> str | None:
    """
    Obtener el tamaño de un archivo

    Parameters:
    path_src (str | Path): Ruta del archivo a determinar su tamaño
    unit (str | None): Unidad para dar el resulado (KB, MB, GB o TB)
    method_stat (bool): Usar os.stat() para determinar el tamaño
    metod_getsize (bool): Usar os.path.getsize() para determinar el tamaño

    Returns:
    str: Tamaño del archivo con su unidad de medida.
    None: Sí la ruta no es válida o sí no es archivo
    """

    # Comprobar que exista el archivo
    if not validate_path(path_src):

        return

    # Construir rutas absolutas y un objeto Path
    path = Path(path_src).resolve()

    # Comprobar que sea un archivo
    if not path.is_file():

        return f'{error("No es un archivo:", "ico")} {info(path)}'

    # Método 01: os.stat()
    if method_stat:
        return natural_size(os.stat(path).st_size, unit)

    # Método 02: os.path.getsize()
    elif method_getsize:
        return natural_size(os.path.getsize(path), unit)

    # Método 03: Path.stat()
    return natural_size(path.stat().st_size, unit)


def obtain_size(path_src: str | Path, unit: str | None = None, file_type: str = "*") -> str:
    """
    Obtener tamaño de un archivo o directorio

    Parameters:
    path_src (str | Path): Ruta del archivo o directorio a determinar su tamaño
    unit (str | None): Unidad para dar el resulado (KB, MB, GB o TB)
    file_type (str): Tipos de archivos a seleccionar en el directorio

    Returns:
    str: Tamaño del archivo o directorio con su unidad de medida
    """

    # Comprobar que exista el directorio o archivo
    if not validate_path(path_src):

        return

    # Obtener tamaño de un archivo
    if Path(path_src).is_file():

        return __obtain_size_file(path_src, unit)

    # Obtener tamaño de un directorio
    return __obtain_size_dir(path_src, unit, file_type)
