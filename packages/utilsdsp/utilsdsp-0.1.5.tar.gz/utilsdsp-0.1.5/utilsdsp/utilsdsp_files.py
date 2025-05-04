"""
Operaciones con archivos:
    - read_text_file: Leer un archivo de texto
    - write_text_file: Guardar texto en un archivo
"""

from pathlib import Path
from outputstyles import error, info, warning, success
from utilsdsp import create_dir, validate_path


def read_text_file(path_file: str | Path, by_line: bool = True, print_msg: bool = True) -> list | str | None:
    """
    Leer un archivo de texto

    Parameters:
    path_file (str | Path): Ruta del archivo a leer
    by_line (bool): Leer el contenido por líneas
    print_msg (bool): Imprimir un mensaje si no existe el archivo

    Returns:
    list: Contenido según las líneas leidas
    str: Todo el contenido en un string
    None: Si el archivo no existe o no se pudo leer
    """

    # Comprobar que exista el archivo
    if not validate_path(path_file, print_msg=print_msg):

        return

    # Construir rutas absolutas y un objeto Path
    file = Path(path_file).resolve()

    # Comprobar que sea un archivo
    if not file.is_file():

        print(error("No es un archivo:", "ico"), info(file))

        return

    # Leer el contenido del archivo
    try:

        content = file.read_text("utf-8")

        # Retornar una lista según las lineas o todo en un solo string
        return content.split("\n") if by_line else content

    except Exception as err:

        print(
            error("Error al leer el archivo:", "ico"),
            info(file),
            "\n" + str(err)
        )


def write_text_file(path_file: str | Path, content: str | list, replace: bool = False, print_msg: bool = True) -> str | None:
    """
    Guardar texto en un archivo

    Parameters:
    path_file (str | Path): Ruta del archivo a escribir
    content (str | list): Contenido que se va a guardar
    replace (bool): Reemplazar el contenido si existe el archivo
    print_msg (bool): Imprimir mensaje satisfactorio

    Returns:
    str: Ruta del archivo guardado
    None: Sí no hay contenido, sí no es un archivo o sí no se pudo escribir
    """

    # Comprobar que el contenido no este vacio
    if not content:

        print(warning("El contenido no puede estar vacio.", "ico"))

        return

    # Construir rutas absolutas y un objeto Path
    file = Path(path_file).resolve()

    # Comprobar sí existe y no es un archivo
    if file.exists() and not file.is_file():

        print(warning("Ya existe y no es un archivo:", "ico"), info(file))

        return

    # Crear la ruta padre sí no existe
    create_dir(file.parent)

    # Determinar como guardar el contenido, por líneas o un string
    by_line = True if isinstance(content, list) else False

    # Preparar el contenido a guardar, según si existe el achivo
    # y sí se va a reemplazar el contenido existente o no
    if file.exists() and not replace:

        # Leemos el contenido del archivo existente
        old_content = read_text_file(file, by_line=by_line)

        # Agregamos el nuevo contenido al existente
        if by_line:

            # Sí es una lista el contenido
            old_content.extend(content)

            new_content = old_content

        else:

            # Sí es un string el contenido
            new_content = old_content + f'\n{content}'

    # Si no existe o se va a reemplazar el contenido
    else:

        new_content = content

    # Guardar el contenido en el archivo
    try:

        # Guardar una lista
        if by_line:

            # Convertir a string los elementos de la lista
            new_content = [str(item) for item in new_content]

            # Escribimos el contenido en el archivo por líneas
            file.write_text("\n".join(new_content), "utf-8")

        # Guardar un texto
        else:

            # Escribimos el contenido en el archivo como un texto único
            file.write_text(str(new_content), "utf-8")

        # Imprimir mensaje satisfactorio
        if print_msg:

            print(success("Guardado el contenido en:", "ico"), info(file))

        # Retornar la ruta absoluta del archivo
        return str(file)

    except Exception as err:

        print(
            error("Error al escribir en el archivo:", "ico"),
            info(file),
            "\n" + str(err)
        )
