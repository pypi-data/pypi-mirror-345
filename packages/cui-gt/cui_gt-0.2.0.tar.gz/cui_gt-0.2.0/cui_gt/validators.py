"""
cui_gt.validators
~~~~~~~~~~~~~~~~~
Core validation logic for Guatemalan identifiers.
"""

from __future__ import annotations

__all__ = ["InvalidCUI", "validate_cui", "is_valid_cui"]

_munis_per_dept = (
    17, 8, 16, 16, 14, 14, 19, 8, 24, 21, 9,
    30, 32, 21, 8, 17, 14, 5, 11, 11, 7, 17,
)

class InvalidCUI(ValueError):
    """Raised when a CUI fails validation."""

def _checksum(number: str) -> int:
    total = sum(int(n) * (idx + 2) for idx, n in enumerate(number))
    return total % 11

def is_valid_cui(cui: str) -> bool:
    try:
        return validate_cui(cui) is None
    except InvalidCUI:
        return False

def validate_cui(cui: str) -> None:
    """Validate a Guatemalan CUI.

    Parameters
    ----------
    cui : str
        13–character numeric CUI.

    Raises
    ------
    InvalidCUI
        If the CUI is syntactically or mathematically invalid.
    """
    if len(cui) != 13 or not cui.isdigit():
        raise InvalidCUI("CUI must be exactly 13 numeric characters")

    serial, check, dept, muni = cui[:8], int(cui[8]), int(cui[9:11]), int(cui[11:])
    if dept == 0 or muni == 0:
        raise InvalidCUI("Department or municipality cannot be 00")

    if dept > len(_munis_per_dept):
        raise InvalidCUI("Unknown department code")

    if muni > _munis_per_dept[dept - 1]:
        raise InvalidCUI("Unknown municipality code for the given department")

    if _checksum(serial) != check:
        raise InvalidCUI("Checksum mismatch")

# Optional shorthand
def _cli():  # python -m cui_gt <CUI>
    import sys, textwrap
    cui = (sys.argv + [None])[1]
    if not cui:
        print(textwrap.dedent(__doc__))
        sys.exit(1)
    try:
        validate_cui(cui)
        print("VALID")
    except InvalidCUI as exc:
        print("INVALID:", exc)
        sys.exit(2)

if __name__ == "__main__":
    _cli()
