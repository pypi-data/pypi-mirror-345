import pytest
from cui_gt import validate_cui, InvalidCUI, is_valid_cui

# --- Casos VÁLIDOS (diferentes departamentos y municipios) ---
VALID_CUIS = [
    "1234567890101",  # 01‑Guatemala, muni 01
    "8765432122217",  # 22‑Jutiapa,    muni 17
    "1029384741305",  # 13‑Huehuetenango, muni 05
    "7654321020924",  # 09‑Quetzaltenango, muni 24
]

# --- Casos INVÁLIDOS (checksum, depto, muni, longitud, etc.) ---
INVALID_CUIS = [
    "1234567890000",  # depto/muni 00
    "1234567892301",  # depto 23 no existe
    "1234567890125",  # muni 25 no existe en depto 01
    "123456789010",   # longitud 12 (debe ser 13)
    "5486270650100",  # checksum incorrecto
]

# ---------- Tests ----------

@pytest.mark.parametrize("cui", VALID_CUIS)
def test_valid_cuis(cui):
    assert is_valid_cui(cui)          # Función booleana
    validate_cui(cui)                 # No debe lanzar excepción

@pytest.mark.parametrize("cui", INVALID_CUIS)
def test_invalid_cuis(cui):
    assert not is_valid_cui(cui)
    with pytest.raises(InvalidCUI):
        validate_cui(cui)
