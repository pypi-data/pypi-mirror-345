"""
Comprimir archivos y directorios:
    - compress: Comprimir un directorio o archivo
    - uncompress: Descomprimir un archivo
"""

from pathlib import Path
from shutil import make_archive, unpack_archive
from outputstyles import error, info, warning
from utilsdsp import validate_path, delete_dir


def compress(path_src: str | Path, path_dst: str | Path | None = None, compress_type: str = "zip", base_include: bool = True, overwrite: bool = False, delete_src: bool = False) -> str | None:
    """
    Comprimir un directorio o archivo

    Parameters:
    path_src (str | Path): Ruta del directorio o archivo a comprimir
    path_dst (str | Path | None): Ruta del directorio a guardar el comprimido
    compress_type (str): Tipo de comprimido (zip, tar, gztar, bztar o xztar)
    base_include (bool): Incluir el directorio base en el comprimido
    overwrite (bool): Sobrescribir el archivo comprimido sí existe
    delete_src (bool): Eliminar el archivo o directorio de origen

    Returns:
    str: Ruta absoluta del archivo comprimido
    None: Sí no existe el origen, sí ya existe el destino y
          sí no se pudo comprimir el archivo
    """

    # Comprobar que exista el directorio o archivo de origen
    if not validate_path(path_src):

        return

    # Construir rutas absolutas y objetos Path
    path_src = Path(path_src).resolve()
    path_dst = Path(path_dst).resolve() if path_dst else path_src.parent

    # Obtener el nombre del directorio o archivo sin la extensión
    file_name = path_src.stem

    # Ruta completa del archivo final comprimido
    path_filecompress = path_dst / f'{file_name}.{compress_type}'

    # Comprobar que no exista el archivo comprimido en la ruta de destino
    if path_filecompress.exists() and not overwrite:

        print(warning("Ya existe:", "ico"), info(path_filecompress))

        return

    # Procedemos a crear el archivo comprimido
    try:

        # Comprimir sí es un directorio con la base incluida o un archivo
        if path_src.is_file() or base_include:

            result = make_archive(
                base_name=str(path_dst / file_name),
                format=compress_type,
                root_dir=path_src.parent,
                base_dir=path_src.name
            )

        # Comprimir un directorio sin la base
        else:

            result = make_archive(
                base_name=str(path_dst / file_name),
                format=compress_type,
                root_dir=path_src
            )

        # Eliminar el archivo o directorio de destino
        if delete_src:

            delete_dir(path_src)

        # Retornar la ruta absoluta del archivo comprimido
        return result

    except Exception as err:

        print(
            error("Error al comprimir:", "ico"),
            info(path_src),
            "\n" + str(err)
        )


def uncompress(path_src: str | Path, path_dst: str | Path | None = None, delete_src: bool = False) -> str | None:
    """
    Descomprimir un archivo

    Parameters:
    path_src (str | Path): Ruta del archivo comprimido
    path_dst (str | Path | None): Directorio a descomprimir el archivo
    delete_src (bool): Eliminar el archivo comprimido

    Returns:
    str: Ruta absoluta del archivo o directorio descomprimido
    None: Sí no existe el origen, sí ya existe el destino y
          sí no se pudo descomprimir el archivo
    """

    # Comprobar que exista el archivo comprimido
    if not validate_path(path_src):

        return

    # Construir rutas absolutas y objetos Path
    path_src = Path(path_src).resolve()
    path_dst = Path(path_dst).resolve() if path_dst else path_src.parent

    # Comprobar que sea un archivo admitido
    if not path_src.suffix in [".zip", ".tar", ".gztar", ".bztar", ".xztar"]:

        print(warning("Archivo no admitido:", "ico"), info(path_src))

        return

    # Procedemos a descomprimir el archivo
    try:

        unpack_archive(path_src, path_dst)

        # Eliminar el archivo comprimido de destino
        if delete_src:

            delete_dir(path_src)

        # Retornar la ruta absoluta del archivo comprimido
        return str(path_dst / path_src.stem)

    except Exception as err:

        print(
            error("Error al descomprimir:", "ico"),
            info(path_src),
            "\n" + str(err)
        )
