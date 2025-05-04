"""
Operaciones con listas:
    - remove_repeated_elements: Eliminar elementos repetidos
"""


def remove_repeated_elements(list_: list) -> list:
    """
    Eliminar los elementos repetidos de una lista

    Parameters:
    list_ (list): Lista de elementos

    Returns:
    list: Devuelve una lista sin elementos repetidos
    """

    # Usar "fromkeys" de los diccionarios para
    # eliminar elementos repetidos
    return list(dict.fromkeys(list_))
