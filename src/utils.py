import unicodedata

def normalize_string(s: str) -> str:
    """Elimina acentos y estandariza texto a Mayúsculas iniciales."""
    if not s:
        return ""
    # Eliminar acentos
    s = "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )
    # Estandarizar nombres compuestos (p. ej. CASTELLON / CASTELLO -> CASTELLON)
    if " / " in s:
        s = s.split(" / ")[0]
    
    # Capitalizar cada palabra (Title Case)
    return s.strip().title()

def normalize_province(province: str) -> str:
    """Normalización específica para provincias españolas."""
    mapping = {
        "Alicante / Alacant": "Alicante",
        "Castellon / Castello": "Castellon",
        "Valencia / Valencia": "Valencia",
        "Araba/Alava": "Alava",
        "Gipuzkoa": "Guipuzcoa",
        "Bizkaia": "Vizcaya",
        "Coruna (A)": "A Coruna",
        "Palmas (Las)": "Las Palmas",
        "Rioja (La)": "La Rioja",
    }
    
    clean_p = normalize_string(province)
    return mapping.get(clean_p, clean_p)
