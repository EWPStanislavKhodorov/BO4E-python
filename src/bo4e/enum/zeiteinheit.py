"""
Auflistung möglicher Einheiten zur Verwendung in zeitbezogenen Angaben.
"""

from enum import Enum

Zeiteinheit = Enum(
    "Zeiteinheit",
    {
        "SEKUNDE": "SEKUNDE",  # Sekunde
        "MINUTE": "MINUTE",  # Minute
        "STUNDE": "STUNDE",  # Stunde
        "VIERTEL_STUNDE": "VIERTEL_STUNDE",  # Viertelstunde
        "TAG": "TAG",  # Tag
        "WOCHE": "WOCHE",  # Woche
        "MONAT": "MONAT",  # Monat
        "QUARTAL": "QUARTAL",  # Quartal
        "HALBJAHR": "HALBJAHR",  # Halbjahr
        "JAHR": "JAHR",  # Jahr
    },
)
