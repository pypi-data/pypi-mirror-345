"""
Otras funciones útiles:
    - obtain_url_from_html: Obtener la URL desde un archivo HTML
    - create_headers_decorates: Crear un encabezado decorado
    - clear_output: Limpiar salida en la Terminal según el SO
    - calc_img_dimensions: Calcular las dimensiones de una imagen
    - obtain_similar_vars: Obtener el valor o nombre de variables similares
"""

import os
from pathlib import Path
from utilsdsp import validate_path, read_text_file
from outputstyles import warning, error, info, add_text_styles


def obtain_url_from_html(path_src: str | Path, num_line: int = 3) -> str | None:
    """
    Obtener la URL desde un archivo HTML, guardado
    con SingleFile (Extensión de Firefox)

    Parameters:
    path_src (str | Path): Ruta del archivo HTML
    num_line (int): Número de la linea donde está la URL

    Returns:
    str: URL real del archivo HTML
    None: Si no se obtuvo la URL o no es un archivo HTML
    """

    # Comprobar que exista el archivo HTML
    if not validate_path(path_src):

        return

    # Construir rutas absolutas para evitar problemas con rutas relativas
    path_src = Path(path_src).resolve()

    # Comprobar que sea un archivo HTML
    if path_src.suffix.lower() != ".html":

        print(
            warning("No es un archivo HTML:", "ico"),
            error(path_src, "ico")
        )
        return

    # Leer contenido del archivo HTML por lineas
    content_html = read_text_file(path_src)

    try:

        num_line = num_line if isinstance(num_line, int) else 3

        # Retornar la URL real (Siempre es la 3ra línea)
        # Ej:  url: https://dominio.com/otra/dir/
        # return content_html[num_line - 1].strip().split(" ")[1]
        return content_html[num_line - 1].replace("url:", "").strip()

    except Exception as err:

        print(
            error("No se pudo obtener la URL de:", "ico"),
            info(path_src),
            "\n" + str(err)
        )


def create_headers_decorates(header: str, chars_cant: int = 100, decoration: str = "*", deco_init: int = 2, styles: list | None = None) -> str:
    """
    Crear un encabezado decorado

    Parameters:
    header (str): Texto del encabezado
    chars_cant (int): Cantidad de carácteres del encabezado
    decoration (str): Decorado del encabezado
    deco_init (int): Cantidad de decorado inicial
    styles (list | None): Lista con los estilos a aplicarle al header

    Ej (Los mismos estilos del paquete outputstyles):
        - styles = ["fg_red", "bold"]

    Returns:
    str: Encabezado decorado y con la longitud especificada
    """

    try:

        # Sanear argumentos
        header = str(header)
        chars_cant = int(chars_cant)
        decoration = str(decoration)
        deco_init = int(deco_init)

        # Cantidad de decoración inicial
        deco_init = deco_init if deco_init >= 0 else 1

        # Encabezado inicial decorado y con el texto del header
        header_init = f'{header} ' if deco_init == 0 else f'{decoration * deco_init} {header} '

        # Cantidad de decoración al final del encabezado
        deco_final = chars_cant - len(header_init)

        # Encabezado final decorado
        header_final = decoration * deco_final if deco_final > 0 else decoration * deco_init

        # Verificar que los estilos a aplicar sean válidos
        styles = styles if isinstance(styles, list) and styles else []

        # Retornar el encabezado decorado
        return add_text_styles(header_init + header_final, styles=styles)

    except Exception as err:

        print(error("Error:", "ico"), err)


def clear_output() -> None:
    """
    Limpiar salida en la Terminal según el SO

    Parameters:
    None

    Returns:
    None
    """

    # Si es Windows
    if os.name == "nt":

        os.system("cls")

    # Si es Unix o Linux
    elif os.name == "posix":

        os.system("clear")

    # En otros casos, imprime 120 nuevas líneas
    else:

        print("\n" * 120)


def calc_img_dimensions(img_size: tuple, width_final: int | None = None, height_final: int | None = None) -> tuple:
    """
    Calcular las dimensiones finales (ancho, alto) de
    una imagen según su ancho o altura a modificar

    Parameters:
    img_size (tuple): Tamaño original de la imagen (ancho, alto)
    width_final (int | None): Ancho a modificar
    height_final (int | None): Alto a modificar

    Returns:
    tuple: Devuelve el ancho y alto de la imagen modificada
    """

    # Calcular la altura final si se introdujo un ancho
    if width_final and isinstance(width_final, int):

        # Fórmula: height_final = width_final / width_org * height_org
        height_final = round(width_final / int(img_size[0]) * int(img_size[1]))

    # Calcular el Ancho final si se introdujo una altura
    elif height_final and isinstance(height_final, int):

        # Fórmula: width_final = height_final / height_org * width_org
        width_final = round(height_final / int(img_size[1]) * int(img_size[0]))

    # Retornar el mismo tamaño de la imagen si no son válidos (ancho, alto)
    else:

        width_final, height_final = img_size

    return width_final, height_final


def obtain_similar_vars(var_name: str, var_cant: int, all_vars: dict, value: bool = True) -> list | None:
    """
    Obtener el valor de las variables que tienen el nombre similar,
    solo le cambia un número a cada una
    - Ej: var_1, var_2, ..., var_10

    Parameters:
    var_name (str): Nombre común entre las varibles
    var_cant (int): Cantidad de variables que hay similares
    all_vars (dict): Diccionario con todas las variables [globals() o locals()]
    value (bool): Obtener el valor de las variables o el nombre

    Returns:
    list: Valor o nombre de las variables no nulas
    None: Si ocurrio algún error
    """

    try:

        # Retornar el valor de las variables
        if value:

            return [
                all_vars[f'{var_name}{i}'] for i in range(1, var_cant + 1) if all_vars[f'{var_name}{i}']
            ]

        # Retornar el nombre de las variables
        return [
            f'{var_name}{i}' for i in range(1, var_cant + 1) if all_vars[f'{var_name}{i}']
        ]

    except Exception as err:

        print(error("Error al obtener las variables:", "ico"), err)
