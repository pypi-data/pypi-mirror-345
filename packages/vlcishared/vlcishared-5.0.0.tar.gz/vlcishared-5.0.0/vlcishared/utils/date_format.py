from datetime import datetime


def convertir_string_a_date(fecha, formato):
    """
    Convierte una cadena de texto a un objeto datetime, usando un formato personalizado.
    """
    formato_strftime = _mapear_formato_personalizado(formato)
    return datetime.strptime(fecha, formato_strftime)


def convertir_date_a_string(fecha, formato):
    """
    Convierte un objeto datetime a una cadena de texto, usando un formato personalizado.
    """
    formato_strftime = _mapear_formato_personalizado(formato)
    return fecha.strftime(formato_strftime)


def _mapear_formato_personalizado(formato: str) -> str:
    """
    Convierte un formato personalizado (por ejemplo: 'DD-MM-YYYY') en uno compatible con las funciones estándar de fechas en Python
    strftime/strptime (por ejemplo: '%d-%m-%Y').

    - `strftime` formatea objetos datetime como cadenas de texto.
    - `strptime` parsea cadenas de texto y las convierte en objetos datetime.
    """
    reemplazo_formatos = {
        "YYYY": "%Y",
        "YY": "%y",
        "MMMM": "%B",
        "MMM": "%b",
        "MM": "%m",
        "DD": "%d",
        "WD": "%A",
        "HH24": "%H",
        "HH12": "%I",
        "HH": "%H",
        "AMPM": "%p",
        "MI": "%M",
        "SS": "%S",
    }

    formato = formato.upper()
    for clave, valor in sorted(reemplazo_formatos.items(), key=lambda x: -len(x[0])):
        formato = formato.replace(clave, valor)
    return formato
