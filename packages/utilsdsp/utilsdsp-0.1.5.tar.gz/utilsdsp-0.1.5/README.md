# UtilsDSP

Variedades de funciones útiles para trabajar con Python, sin tener que escribrirlas una y otras vez cada vez que se necesitan en algún proyecto.

Orientadas principalmente para ejecutar scripts de Python desde CLI o en cuadernos de Google Colab y Jupyter.

Tabla de contenido

- [UtilsDSP](#utilsdsp)
  - [Install](#install)
  - [Usage/Examples](#usageexamples)
    - [Operaciones con rutas](#operaciones-con-rutas)
    - [Operaciones con directorios](#operaciones-con-directorios)
    - [Operaciones con archivos](#operaciones-con-archivos)
    - [Operaciones de saneamiento](#operaciones-de-saneamiento)
    - [Tamaño de archivos y directorios](#tamaño-de-archivos-y-directorios)
    - [Comprimir archivos y directorios](#comprimir-archivos-y-directorios)
    - [Otras funciones útiles](#otras-funciones-útiles)
    - [Operaciones con listas](#operaciones-con-listas)
    - [Operaciones con Diccionarios](#operaciones-con-diccionarios)
    - [Organizar directorios](#organizar-directorios)
    - [Descargar archivos desde internet](#descargar-archivos-desde-internet)
  - [Documentation](#documentation)
  - [License](#license)
  - [Authors](#authors)

## Install

La instalación vía `pip` es sencilla, solo ejecutar la siguiente línea en la terminal del proyecto de Python.

```bash
  pip install utilsdsp
```

## Usage/Examples

Su uso es bastante simple, una vez instalado solo se debe importar la función o funciones necesarias de la siguiente forma:

```py
from utilsdsp import compress, uncompress
```

### Operaciones con rutas

- `obtain_current_path` - Obtener la ruta donde se está ejecutando el script
- `obtain_absolute_path` - Obtener la ruta absoluta
- `change_current_path` - Cambiar la ruta actual de ejecución del script
- `validate_path` - Válidar sí la ruta existe
- `join_path` - Unir rutas en una sola
- `obtain_default_path` - Obtener la ruta absoluta por defecto _(PC o Google Colab)_
- `obtain_downloads_path` - Obtener la ruta para guardar las descargas
- `rename_exists_file` - Renombrar un archivo sí existe en el destino

### Operaciones con directorios

- `create_dir` - Crear directorio
- `create_downloads_dir` - Crear el directorio de las descargas
- `create_symbolic_link` - Crear enlace simbólico
- `delete_dir` - Eliminar un directorio o archivo
- `del_empty_dirs` - Borrar recursivamente los sub-directorios vacios
- `select_dir_content` - Seleccionar contenido de un directorio
- `move_dirs` - Mover archivo(s) y directorio(s) hacia otro directorio
- `copy_dirs` - Copiar archivo(s) y directorio(s) hacia otro directorio
- `rename_dir` - Renombrar un archivo o directorio

### Operaciones con archivos

- `read_text_file` - Leer un archivo de texto
- `write_text_file` - Guardar texto en un archivo

### Operaciones de saneamiento

- `truncate_filename` - Truncar el nombre del archivo o directorio
- `sanitize_filename` - Sanear el nombre de un archivo o directorio

### Tamaño de archivos y directorios

- `natural_size` - Convertir los bytes a medidas más legibles _(KB, MB, etc)_
- `obtain_size` - Obtener tamaño de un archivo o directorio

### Comprimir archivos y directorios

- `compress` - Comprimir un directorio o archivo
- `uncompress` - Descomprimir un archivo _(zip, tar, gztar, bztar, xztar)_

### Otras funciones útiles

- `obtain_url_from_html` - Obtener la URL desde un archivo HTML
- `create_headers_decorates` - Crear un encabezado decorado
- `clear_output` - Limpiar salida en la Terminal según el SO
- `calc_img_dimensions` - Calcular las dimensiones de una imagen
- `obtain_similar_vars` - Obtener el valor o nombre de variables similares

### Operaciones con listas

- `remove_repeated_elements` - Eliminar elementos repetidos

### Operaciones con Diccionarios

- `join_list_to_dict` - Unir dos listas en un diccionario

### Organizar directorios

- `move_to_root` - Mover archivos de los sub-directorios hacia el directorio raíz
- `move_files_to_subdir` - Mover archivos hacia un sub-directorio dentro de los sub-directorios de nivel 1
- `organize_files_by_type` - Organizar los archivos en directorios según su tipo
- `organize_files_by_name` - Organizar los archivos en directorios según su nombre

### Descargar archivos desde internet

- `validate_and_resquest` - Comprobar sí una URL es válida y accesible
- `download_file` - Descargar un archivo desde internet
- `download_files` - Descargar multiples archivos simultáneos desde internet

## Documentation

En desarrollo

## License

[MIT](LICENSE)

## Authors

- [@dunieskysp](https://github.com/dunieskysp)
