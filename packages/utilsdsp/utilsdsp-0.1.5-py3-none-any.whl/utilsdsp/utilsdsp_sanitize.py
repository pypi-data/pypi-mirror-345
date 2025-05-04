"""
Operaciones de saneamiento
    - truncate_filename: Truncar el nombre del archivo o directorio
    - sanitize_filename: Sanear el nombre de un archivo o directorio
"""

import re
from pathlib import Path


def truncate_filename(filename: str, chars_cant: int = 120) -> str:
    """
    Truncar el nombre del archivo o directorio

    Parameters:
    filename (str): Nombre del archivo o directorio
    chars_cant (int): Cantidad de carácteres a dejar en el nombre

    Returns:
    srt: Devuelve el nombre truncado o no, según los carácteres que contenga
    """

    # Retornar el nombre tal y como está,
    # sí tiene menos carácteres de los admitidos
    if len(filename) <= chars_cant:

        return filename

    # Obtener el nombre y la extesión por separados
    name = Path(filename).stem
    ext = Path(filename).suffix

    # Indice donde vamos a truncar el nombre del archivo
    idx_trunc = chars_cant - len(ext)

    # Retornar el nombre truncado y a los ficheros
    # agregarle tres puntos al final
    return f'{name[:idx_trunc - 3]}...{ext}' if ext else name[:idx_trunc]


def sanitize_filename(filename: str, chars_cant: int = 120) -> str:
    """
    Sanear el nombre de un archivo o directorio, eliminando
    los carácteres no adminitidos por Linux y Windows

    Parameters:
    filename (str): Nombre del archivo o directorio
    chars_cant (int): Cantidad de carácteres a dejar en el nombre

    Returns:
    srt: Devuelve el nombre saneado
    """

    # Expresión Regular con los carácteres no admitidos en los nombres
    # [\\/:*?"<>|] --> Carácteres no admitidos que se van a cambiar
    # ^\. --> Cambiar un punto (.) que este al inicio
    # \.+$ --> Cambiar un punto (.) o más que esten al final
    invalid_chars = r'[\\/:*?"<>|]|^\.|\.+$'

    # Reemplazar los carácteres no admitidos
    # filename = re.sub(invalid_chars, '_', filename)
    filename = re.sub(invalid_chars, '', filename)  # Es mejor eliminarlos

    # Reemplazar más de un espacio por uno sencillo
    filename = re.sub(r'\s+', ' ', filename)

    # Retornar el nombre saneado y truncado en caso de ser necesario
    return truncate_filename(filename.strip(), chars_cant)
