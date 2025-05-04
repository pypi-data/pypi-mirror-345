"""
Descargar un archivo desde internet:
    - validate_and_resquest: Comprobar sí una URL es válida y accesible
    - obtain_filename: Obtener nombre del archivo que se va a descargar
    - update_download_logs: Actualizar los logs de la descarga
    - download_file: Descargar un archivo desde internet

Descargar varios archivos desde internet
    - organize_urls_data: Organizar en tuplas los datos de las URLs a descargar
    - update_description_pbar: Actualizar descripción de la barra de progreso principal
    - download_files: Descargar multiples archivos simultaneos desde internet
"""

import os
import requests
import validators
from pathlib import Path
from tqdm.auto import tqdm
from datetime import datetime
from urllib.parse import unquote
from curl_cffi import requests as requests_curl
from concurrent.futures import ThreadPoolExecutor, as_completed
from outputstyles import error, warning, info, success, bold
from utilsdsp import sanitize_filename, create_downloads_dir, natural_size, join_path, validate_path, write_text_file, obtain_downloads_path, rename_exists_file


# COMMENT Funciones para descargar un archivo
def validate_and_resquest(url: str, accessible: bool = True, timeout: int | None = 10, stream: bool = True, headers: dict | None = None, cookies: dict | None = None, auth: dict | None = None, r_curl: bool = False, write_logs: bool = False, logs_path: str | None = None, print_msg: bool = True) -> bool | requests.Response | None:
    """
    Comprobar sí una URL es válida y accesible

    Parameters:
    url (str): Dirección web a comprobar
    accessible (bool): Verificar sí es accesible
    timeout (int | None): Tiempo de espera por la respuesta del servidor
    stream (bool): No descargar la respuesta completa en memoria
    headers (dict | None): Datos del Headers para la petición Get
    cookies (dict | None): Datos de las cookies para la petición Get
    auth (dict | None): Credenciales de autenticación
    r_curl (bool): Usar el metodo requests de curl_cffi

    write_logs (bool): Guardar los logs
    logs_path (str): Ruta del archivo de los logs

    print_msg (bool): Imprimir o no los mensajes (warnings & errors)

    Returns:
    bool: Sí no hay que comprobar la accesibilidad
    requests.Response: Respuesta de la URL
    None: Si no se pudo establecer conexión con la URL
    """

    # Comprobar la estructura de la URL
    if not validators.url(url):

        if print_msg:

            print(error("URL no válida:", "btn_ico"), info(url))

        # Atualizar los logs
        update_download_logs(
            write_logs=write_logs,
            logs_path=logs_path,
            msg_type="url_not_valid",
            url=url
        )

        return False

    # Si no hay que comprobar la accesibilidad de la URL
    if not accessible:

        return True

    # Hacer la petición a la URL
    try:

        # Usar el requests tradicional o el de curl_cffi
        response = (requests_curl if r_curl else requests).get(
            url=url,
            timeout=timeout,
            stream=stream,
            headers=headers,
            cookies=cookies,
            auth=auth
        )

        # Levantar una exception si no se obtuvo una respuesta
        # satisfactoria
        response.raise_for_status()

        # Retornar el contenido
        return response

    except requests.exceptions.RequestException as err:

        if print_msg:

            print(
                error("No se pudo establecer conexión con:", "ico"),
                info(url),
                "\n" + str(err)
            )

        # Atualizar los logs
        update_download_logs(
            write_logs=write_logs,
            logs_path=logs_path,
            msg_type="url_not_accessible",
            url=url,
            err=str(err)
        )

        return


def obtain_filename(response: requests.Response, url: str, missing_name: str | None = None) -> str:
    """
    Obtener el nombre de un archivo que se va a descargar
    desde internet

    Parameters:
    response (requests.Response): Respuesta obtenida de la URL
    url (str): Dirección web del archivo
    missing_name (str): Nombre por defecto si no se obtiene el nombre del archivo

    Returns:
    str: Nombre del archivo
    """

    # Obtener el nombre según su URL
    file = Path(url)
    missing_name = missing_name or "missing name"
    default_name = file.name if file.suffix else f'{missing_name} ({file.name})'

    # Si el servidor brinda el "Content-Disposition", se le asigna a la variable
    if content_disposition := response.headers.get("Content-Disposition"):

        # Retornar nombre del archivo según "filename*"
        # Ej: Content-Disposition: attachment; filename="nombre_del_archivo.ext"; filename*=UTF-8''nombre%20del%20archivo.ext
        # Ej: Content-Disposition: attachment; filename*=UTF-8''4x-UltraSharp.pth; filename="4x-UltraSharp.pth";
        if "filename*" in content_disposition:

            return unquote(content_disposition.split("\'\'")[-1].split(";")[0])

        # Retornar nombre del archivo según "filename"
        # Ej: Content-Disposition: attachment; filename="nombre_del_archivo.ext";
        return content_disposition.split('filename=')[1].split('"')[1]

    # Retornar el nombre según su URL
    return default_name


def update_download_logs(write_logs: bool, logs_path: str | Path, msg_type: str, url: str, filepath: str | None = None, err: str | None = None) -> None:
    """
    Actualizar los logs de la descarga

    Parameters:
    write_logs (bool): Guardar los logs
    logs_path (str | Path): Ruta del archivo de los logs
    msg_type (str): Tipo de mensaje a guardar
    url (str): URL en turno
    filepath (str | None): Ruta del archivo descargado
    err (str | None): Mensaje de error de la excepción

    Returns:
    None
    """

    # Comprobar si no hay que guardar los logs o no hay ruta
    if not (write_logs and logs_path):

        return

    # Mensajes a guardar en los logs
    msg_texts = {
        "url_not_valid": f'ERROR - [Invalid URL]: URL no válida.\n\t\t\tURL: {url}\n',
        "url_not_accessible": f'ERROR - [Not Accessible]: URL no accesible.\n\t\t\tURL: {url}\n',
        "file_empty": f'ERROR - [File Empty]: El archivo no se encuentra o está vacio.\n\t\t\tURL: {url}\n',
        "file_exists": f'WARNING - [File Exists]: Ya existe el archivo a descargar.\n\t\t\tRUTA: {filepath}\n\t\t\tURL: {url}\n',
        "downloaded": f'SUCCESS - [Downloaded File]: Archivo descargado correctamente.\n\t\t\tRUTA: {filepath}\n\t\t\tURL: {url}\n',
        "download_error": f'ERROR - [Download File]: Error al descargar el archivo.\n\t\t\tRUTA: {filepath}\n\t\t\tURL: {url}\n'
    }

    # Obtener fecha y hora actual (Formato: 2024-09-12 09:27:29PM)
    current_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S%p")

    # Guardar el logs sí el mensaje es válido
    if msg_type in msg_texts:

        # Generar el texto a guardar en los logs
        msg = f'{current_time}\t{msg_texts[msg_type]}'

        # Guardar el mensaje de error también, sí existe
        if err:

            msg += f'\t\t\t{err}\n'

        # Escribir los logs en un archivo.
        try:

            write_text_file(logs_path, content=msg, print_msg=False)

        except Exception as err:

            print(error("Error al actualizar los logs", "ico"), "\n" + str(err))


def download_file(url: str, filename: str | None = None, path_dst: str | None = None, overwrite: bool = False, rename: bool = False, missing_name: str | None = None, write_logs: bool = True, logs_path: str | None = None, timeout: int = 10, chunk_size: int | None = None, headers: dict | None = None, cookies: dict | None = None, auth: dict | None = None, r_curl: bool = False, show_pbar: bool = True, disable_pbar: bool = False, leave: bool = True, ncols: int | None = None, colour: str | None = None, position: int | None = None, desc_len: int | None = None, print_msg: bool = True) -> str | bool | None:
    """
    Descargar un archivo desde internet

    Parameters:
    url (str): URL del archivo a descargar
    filename (str): Nombre del archivo
    path_dst (str): Directorio para guardar el archivo

    overwrite (bool): Sobrescribir el archivo sí existe
    rename (bool): Renombrar el archivo sí existe
    missing_name (str): Nombre por defecto si no se obtiene el nombre del archivo

    write_logs (bool): Guardar los logs
    logs_path (str): Ruta del archivo de los logs

    timeout (int): Tiempo de espera por una respuesta del servidor
    chunk_size (int | None): Tamaño del bloque a descargar desde el servidor
    headers (dict | None): Datos del Headers de la petición Get
    cookies (dict | None): Datos de las cookies de la petición Get
    auth (dict | None): Credenciales de autenticación
    r_curl (bool): Usar el metodo requests de curl_cffi

    show_pbar (bool): Mostrar la barra de progreso
    disable_pbar (bool): Deshabilitar la barra de progreso
    leave (bool): Dejar la barra de progreso al completar
    ncols (int): Número de columnas de la barra de progreso
    colour (str): Color de la barra de progreso
    position (int): Posición de la barra de progreso
    desc_len (int): Longitud de la descripción

    print_msg (bool): Imprimir o no los mensajes (warnings & errors)

    Returns:
    str: Ruta del archivo descargado
    False: Si ocurrió alguna adevertencia al descargar
    None: Si ocurrió algún error al descargar
    """

    # Obtener la ruta para guardar la descarga
    path_dst = create_downloads_dir(path_dst)

    # Obtener la ruta del archivo de los logs
    logs_path = logs_path or join_path(path_dst, "logs.txt")

    # Hacer la petición a la URL
    response = validate_and_resquest(
        url=url,
        timeout=timeout,
        headers=headers,
        cookies=cookies,
        auth=auth,
        r_curl=r_curl,
        write_logs=write_logs,
        logs_path=logs_path,
        print_msg=print_msg
    )

    # Comprobar sí hubo respuesta a la petición
    if not response:

        return  # Retornar un error

    # Obtener el tamaño del archivo
    filesize = int(response.headers.get("Content-Length", 0))

    if filesize == 0:

        if print_msg:

            print(error("El archivo no se encuentra o está vacio:", "ico"), info(url))

        # Atualizar los logs
        update_download_logs(
            write_logs=write_logs,
            logs_path=logs_path,
            msg_type="file_empty",
            url=url
        )

        return  # Retornar un error

    # Obtener el nombre del archivo
    if filename and isinstance(filename, str):

        filename = sanitize_filename(filename)

    else:

        filename = obtain_filename(response, url, missing_name)

    # Obtener la ruta del archivo
    filepath = join_path(path_dst, filename)

    # Comprobar si existe el archivo a descargar
    if validate_path(filepath, print_msg=False):

        # Comprobar si no se va a sobreescribir o renombrar
        if not (overwrite or rename):

            if print_msg:

                print(
                    warning("Ya existe:", "ico"),
                    info(filepath),
                    "\n" + bold("  URL:"),
                    info(url)
                )

            # Atualizar los logs.
            update_download_logs(
                write_logs=write_logs,
                logs_path=logs_path,
                msg_type="file_exists",
                url=url,
                filepath=filepath
            )

            return False  # Retornar una advertencia

        # Comprobar sí se va a renombrar
        if rename:

            filepath = rename_exists_file(filepath)
            filename = Path(filepath).name

    # Conformar el formato de la barra de progreso
    bar_format = '{l_bar}{bar}{r_bar}' if show_pbar else '{l_bar}{r_bar}'

    # Conformar la descripción de la barra de progreso según
    # el nombre del archivo
    if isinstance(desc_len, int) and len(filename) > desc_len:

        name = Path(filename).stem
        ext = Path(filename).suffix

        # Cortar el nombre del archivo si es muy largo
        description = f'{name[:desc_len - 3 - len(ext)]}{info("...")}{ext}'

    else:

        description = filename

    # Definir la barra de progreso
    pbar = tqdm(
        total=filesize,
        desc=description,
        unit="B",
        unit_scale=True,
        bar_format=bar_format,
        disable=disable_pbar,
        ncols=ncols,
        colour=colour,
        leave=leave,
        position=position
    )

    # Definir el chunk_size
    if chunk_size and isinstance(chunk_size, int):

        chunk_size = chunk_size

    else:

        # El chunk_size va a ser de 64KB por defecto
        chunk_size = 1024 * 64

    # Descargar el archivo
    try:

        with open(filepath, "wb") as file:

            if disable_pbar:

                print(bold("Descargando:"), info(filepath))

            # Escribir el archivo y actualizar la barra de progreso
            for data in response.iter_content(chunk_size=chunk_size):

                size = file.write(data)
                pbar.update(size)

            pbar.close()

            # Atualizar los logs
            update_download_logs(
                write_logs=write_logs,
                logs_path=logs_path,
                msg_type="downloaded",
                url=url,
                filepath=filepath
            )

            return filepath

    except Exception as err:

        if print_msg:

            print(
                error("Error al descargar:", "ico"),
                info(filename),
                "\n" + bold("  URL:"),
                info(url)
            )

        # Atualizar los logs
        update_download_logs(
            write_logs=write_logs,
            logs_path=logs_path,
            msg_type="download_error",
            url=url,
            filepath=filepath,
            err=err
        )

        return  # Retornar un error


# COMMENT Funciones para descargar varios archivos simultaneos
def organize_urls_data(urls_data: list, path_dst: str, char_separation: str = ",") -> list:
    """
    Organizar en tuplas los datos de las URLs a descargar

    Ejemplo:
    urls_data = [
        "https://dominio.com/imagen.jpg, Foto1.jpg, Carpeta de imagenes",
        "https://dominio.com/archivo.txt, , Carpeta de textos",
        "https://solo_la_url.com/imagen2.jpg",
        "https://url_y_nombre.com/imagen3.jpg, Foto 10.jpg"
    ]

    Parameters:
    urls_data (list): Datos de las URLs (URL, Filename, Path_Folder)
    path_dst (str): Directorio para guardar las descargas
    char_separation (str): Caracter que separa los datos de "urls_data"

    Returns:
    list: Lista de tuplas con los datos de cada archivo a descargar (URL, 
          Filename, Path_Folder)
    """

    # Lista resultante para guardar las tuplas
    result = []

    # Organizar por tuplas con los datos de las URLs
    for data in urls_data:

        # Segmentar los datos
        data_segments = data.split(char_separation)

        # Comprobar que tenga URL y solo 3 datos
        if not (data_segments[0] and len(data_segments) <= 3):
            continue

        # Obtener los datos (URL, Filename, Folder)
        url = data_segments[0]
        name = data_segments[1] if len(data_segments) >= 2 else ""
        folder = data_segments[2] if len(data_segments) == 3 else ""

        # Agregar los datos a la lista resultante
        result.append((
            url.strip(),
            name.strip(),
            join_path(path_dst, folder)
        ))

    # Devolver la lista con las tuplas de los datos
    return result


def update_description_pbar(result: str | bool | None, downloads_status: dict) -> tuple:
    """
    Actualizar la descripción de la barra de progreso principal
    cuando se descarga varios archivos

    Parameters:
    result (str | bool | None): Resultado al descargar un archivo
    downloads_status (dict): Estadísticas de las descargas

    Returns:
    tuple (srt, dict): Descripción actualizada y diccionario con las estadísticas
    """

    # Actualizar el estado y tamaño de los archivos descargados,
    # sí se descargó correctamente el archivo en turno
    if result:

        # Incrementar los archivos descargados y el tamaño total
        downloads_status["downloaded"] += 1
        downloads_status["size"] += Path(result).stat().st_size

    # Actualizar las advertencias y errores
    if result == False:
        downloads_status["warnings"] += 1

    if result == None:
        downloads_status["errors"] += 1

    # Conformar la descripción con las estadísticas actualizadas
    file = "archivos" if downloads_status["downloaded"] > 1 else "archivo"

    stat_downloaded = f'Descargado: {downloads_status["downloaded"]} {file} ({natural_size(downloads_status["size"])})'
    stat_warnings = f'  Warnings: {downloads_status["warnings"]}'
    stat_errors = f'  Errors: {downloads_status["errors"]}'

    # Conformar descripción si se está trabajando en Google Colab
    if os.getenv("COLAB_RELEASE_TAG"):

        desc = stat_downloaded

        desc += stat_warnings

        desc += stat_errors

    else:

        desc = success(stat_downloaded)

        desc += warning(stat_warnings)

        desc += error(stat_errors)

    return desc, downloads_status


def download_files(urls_data: list, path_dst: str | None = None, max_workers: int = 1, char_separation: str = ",", overwrite: bool = False, rename: bool = False, missing_name: str | None = None, write_logs: bool = True, logs_path: str | None = None, timeout: int = 10, chunk_size: int | None = None, headers: dict | None = None, cookies: dict | None = None, auth: dict | None = None, r_curl: bool = False, show_pbar: bool = True, disable_pbar: bool = False, leave: bool = True, ncols: int | None = None, colour_main: str | None = None, colour: str | None = None, desc_len: int | None = None, print_msg: bool = False) -> str | None:
    """
    Descargar multiples archivos simultaneos desde internet

    Ejemplos (URL, Filename, Path_Folder separados por comas u otro carácter):
    urls_data1 = [
        "https://dominio.com/imagen.jpg, Foto1.jpg, Carpeta de imagenes",
        "https://dominio.com/archivo.txt, , Carpeta de textos",
        "https://solo_la_url.com/imagen2.jpg",
        "https://url_y_nombre.com/imagen3.jpg, Foto 10.jpg"
    ]

    urls_data2 = [
        "https://dominio.com/imagen.jpg\tFoto1.jpg\tCarpeta de imagenes",
        "https://solo_la_url.com/imagen2.jpg",
    ]

    Parameters:
    urls_data (list): Datos de las URLs (URL, Filename, Path_Folder)
    path_dst (str): Directorio para guardar las descargas
    max_workers (int): Cantidad de descargas simultaneas
    char_separation (str): Caracter que separa los datos de "urls_data"

    overwrite (bool): Sobrescribir el archivo sí existe
    rename (bool): Renombrar el archivo sí existe
    missing_name (str): Nombre por defecto si no se obtiene el nombre del archivo

    write_logs (bool): Guardar los logs
    logs_path (str): Ruta del archivo de los logs

    timeout (int): Tiempo de espera por una respuesta del servidor
    chunk_size (int | None): Tamaño del bloque a descargar desde el servidor
    headers (dict | None): Datos del Headers de la petición Get
    cookies (dict | None): Datos de las cookies de la petición Get
    auth (dict | None): Credenciales de autenticación
    r_curl (bool | None): Usar el metodo requests de curl_cffi

    show_pbar (bool): Mostrar la barra de progreso
    disable_pbar (bool): Deshabilitar la barra de progreso
    leave (bool): Dejar la barra de progreso al completar
    ncols (int): Número de columnas de la barra de progreso
    colour_main (str): Color de la barra de progreso principal
    colour (str): Color de las barras de progreso secundarias
    desc_len (int): Longitud de la descripción

    print_msg (bool): Imprimir los mensajes (warnings & errors)

    Returns:
    str: Ruta del directorio donde se descargaron los archivos
    None: En caso de no realizar la descarga
    """

    # Ruta para guardar las descargas
    path_dst = obtain_downloads_path(path_dst)

    # Organizar en tuplas los datos de las URLs
    data_organized = organize_urls_data(urls_data, path_dst, char_separation)

    # Definir el color de la barra de progreso principal
    if not (os.getenv("COLAB_RELEASE_TAG") or colour_main):

        colour_main = "green"

    # Definir la barra de progreso principal
    progress_bar = tqdm(
        total=len(data_organized),
        desc=bold("Descargando archivos..."),
        ncols=ncols,
        colour=colour_main,
        leave=True,
        position=0,
        unit="File"
    )

    # Comenzar la descarga de los archivos
    try:

        # Crear un ThreadPoolExecutor para multitareas
        with ThreadPoolExecutor(max_workers=max_workers) as executor:

            # Crear una barra de progreso con tqdm
            with progress_bar as pbar:

                # Enviar tareas de descarga al executor y obtener su
                # resultado en "futures" al finalizar
                futures = {
                    executor.submit(
                        download_file,
                        url=url,
                        filename=filename,
                        path_dst=path_dst_folder,

                        overwrite=overwrite,
                        rename=rename,
                        missing_name=missing_name,

                        write_logs=write_logs,
                        logs_path=logs_path,

                        timeout=timeout,
                        chunk_size=chunk_size,
                        headers=headers,
                        cookies=cookies,
                        auth=auth,
                        r_curl=r_curl,

                        show_pbar=show_pbar,
                        disable_pbar=disable_pbar,
                        leave=leave,
                        ncols=ncols,
                        colour=colour,
                        position=1,
                        desc_len=desc_len,

                        print_msg=print_msg
                    ): (url, filename, path_dst_folder) for url, filename, path_dst_folder in data_organized
                }

                # Estado de las estadísticas de las descargas
                downloads_status = {
                    "downloaded": 0,
                    "size": 0,
                    "warnings": 0,
                    "errors": 0
                }

                # Itera sobre las tareas de descarga a medida que se completan
                for future in as_completed(futures):

                    # Actualizar el porciento de la barra de progreso principal
                    pbar.update(1)

                    # Obtener el resultado de la descarga finalizada en turno
                    result = future.result()

                    # Actualizar la descripción de la barra de progreso
                    desc, downloads_status = update_description_pbar(
                        result, downloads_status)

                    pbar.set_description(desc)

        # Devolver la ruta de las descargas, sí todo salió bien
        return path_dst

    except Exception as err:
        print(error("Error en la descarga simultanea de archivos.", "ico"))
        print(err)
