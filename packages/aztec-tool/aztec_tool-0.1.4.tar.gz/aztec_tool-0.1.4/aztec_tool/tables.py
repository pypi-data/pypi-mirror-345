from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict

from .enums import AztecTableType
from .exceptions import InvalidParameterError, SymbolDecodeError

__all__ = ["TableManager"]


@dataclass
class AztecTableEntry:
    """Single row of the 5 Aztec character tables (index 0-31)."""

    upper: str
    lower: str
    mixed: str
    punct: str
    digit: Optional[str] = None


class TableManager:
    """Lookup helper for the five Aztec shift/latch character tables.

    Aztec codes use **five tables** (UPPER, LOWER, MIXED, PUNCT, DIGIT).
    Each 5-bit value (0-31) maps to a *character* that depends on the
    currently active table (digit are 4-bit value).

    The mapping is stored in :pyattr:`mapping`.  Two convenience class
    methods are provided:

    * :py:meth:`get_char` - return the character for *(index, table)* or
      raise :class:`SymbolDecodeError`.
    * :py:meth:`letter_to_mode` - convert the first letter of a *shift/latch
      token* (``'U'``, ``'L'``, …) into the corresponding
      :class:`AztecTableType`.

    The class never needs instantiation, all helpers are `@classmethod`s.

    Examples
    --------
    >>> TableManager.get_char(2, AztecTableType.UPPER)
    'A'
    >>> TableManager.letter_to_mode('m')
    <AztecTableType.MIXED: 2>
    """

    LETTER2MODE = {
        "U": AztecTableType.UPPER,
        "L": AztecTableType.LOWER,
        "M": AztecTableType.MIXED,
        "P": AztecTableType.PUNCT,
        "D": AztecTableType.DIGIT,
    }

    mapping: Dict[int, AztecTableEntry] = {
        0: AztecTableEntry("P/S", "P/S", "P/S", "FLG(n)", "P/S"),
        1: AztecTableEntry(" ", " ", " ", "\n", " "),
        2: AztecTableEntry("A", "a", chr(1), "\n\r", "0"),
        3: AztecTableEntry("B", "b", chr(2), ". ", "1"),
        4: AztecTableEntry("C", "c", chr(3), ", ", "2"),
        5: AztecTableEntry("D", "d", chr(4), ": ", "3"),
        6: AztecTableEntry("E", "e", chr(5), "!", "4"),
        7: AztecTableEntry("F", "f", chr(6), '"', "5"),
        8: AztecTableEntry("G", "g", chr(7), "#", "6"),
        9: AztecTableEntry("H", "h", chr(8), "$", "7"),
        10: AztecTableEntry("I", "i", chr(9), "%", "8"),
        11: AztecTableEntry("J", "j", chr(10), "&", "9"),
        12: AztecTableEntry("K", "k", chr(11), "'", ","),
        13: AztecTableEntry("L", "l", chr(12), "(", "."),
        14: AztecTableEntry("M", "m", chr(13), ")", "U/L"),
        15: AztecTableEntry("N", "n", chr(27), "*", "U/S"),
        16: AztecTableEntry("O", "o", chr(28), "+"),
        17: AztecTableEntry("P", "p", chr(29), ","),
        18: AztecTableEntry("Q", "q", chr(30), "-"),
        19: AztecTableEntry("R", "r", chr(31), "."),
        20: AztecTableEntry("S", "s", "@", "/"),
        21: AztecTableEntry("T", "t", "\\", ":"),
        22: AztecTableEntry("U", "u", "^", ";"),
        23: AztecTableEntry("V", "v", "_", "<"),
        24: AztecTableEntry("W", "w", "`", "="),
        25: AztecTableEntry("X", "x", "|", ">"),
        26: AztecTableEntry("Y", "y", "~", "?"),
        27: AztecTableEntry("Z", "z", chr(127), "["),
        28: AztecTableEntry("L/L", "U/S", "L/L", "]"),
        29: AztecTableEntry("M/L", "M/L", "U/L", "{"),
        30: AztecTableEntry("D/L", "D/L", "P/L", "}"),
        31: AztecTableEntry("B/S", "B/S", "B/S", "U/L"),
    }

    @classmethod
    def get_char(cls, index: int, mode: AztecTableType) -> str:
        """Return the character for *index* in the selected *mode* table.

        Raises
        ------
        SymbolDecodeError
            *index* outside 0-31 or undefined in the chosen table.
        """
        try:
            entry = cls.mapping[index]
        except KeyError as exc:
            raise SymbolDecodeError(f"symbol index {index} outside 0-31 range") from exc
        char = getattr(entry, mode.name.lower())
        if char is None:
            raise SymbolDecodeError(f"symbol {index} undefined in {mode.name} table")
        return char

    @classmethod
    def letter_to_mode(cls, char: str) -> AztecTableType:
        """Convert a latch/shift letter (``'U'``, ``'L'``, *etc.*) to the enum.

        Raises
        ------
        InvalidParameterError
            The string is empty or the first letter is not U/L/M/P/D.
        """
        if not char:
            raise InvalidParameterError("empty latch letter")
        try:
            return cls.LETTER2MODE[char[0].upper()]
        except KeyError as exc:
            raise InvalidParameterError(f"unknown latch letter '{char}'") from exc
