from __future__ import annotations
from functools import cached_property
import numpy as np
import reedsolo
from typing import List, Optional

from .tables import TableManager
from .enums import ReadingDirection, AztecTableType, AztecType
from .exceptions import (
    BitReadError,
    BitStuffingError,
    InvalidParameterError,
    ReedSolomonError,
    SymbolDecodeError,
    StreamTerminationError,
)

__all__ = ["CodewordReader"]


class CodewordReader:
    """Read the data spiral, apply Reed-Solomon correction and decode code-words.

    Parameters
    ----------
    matrix : numpy.ndarray
        Square binary matrix (0/1) representing the Aztec symbol.
    layers : int
        Number of data layers (excluding the bull's-eye).
    data_words : int
        Expected count of data code-words (script does *not* include ECC words).
    aztec_type : AztecType
        ``AztecType.COMPACT`` or ``AztecType.FULL`` according to the spec.
    auto_correct : Optional[bool], default ``True``
        If *True*, a Reed-Solomon pass is executed before high-level decoding.

    Attributes
    ----------
    bitmap : numpy.ndarray
        Raw bit-stream extracted from the symbol (before ECC correction).
    corrected_bits : List[int]
        Bit-stream after Reed-Solomon decoding and bit-stuff removal.
    decoded_string : str
        Final user message built with the Aztec shift/latch tables.

    Raises
    ------
    InvalidParameterError
        One of the constructor arguments is incoherent (e.g. *layers* < 1).
    BitReadError
        Data spiral extraction failed (index out of matrix or empty result).
    ReedSolomonError
        The Reed-Solomon decoder could not correct the symbol.
    BitStuffingError
        Stuffed/padding bits do not follow the spec rules.
    SymbolDecodeError
        An index maps to no entry in the current character table.
    StreamTerminationError
        Premature end of bit-stream (e.g. incomplete Byte-shift segment).
    """

    PRIM_POLY = {
        6: 0x43,  # x^6 + x^5 + 1
        8: 0x12D,  # x^8 + x^5 + x^3 + x^2 + 1
        10: 0x409,  # x^10 + x^3 + 1
        12: 0x1069,  # x^12 + x^6 + x^5 + x^3 + 1
    }

    def __init__(
        self,
        matrix: np.ndarray,
        layers: int,
        data_words: int,
        aztec_type: AztecType,
        auto_correct: Optional[bool] = True,
    ) -> None:
        if layers < 1:
            raise InvalidParameterError("layers must be ≥ 1")
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise InvalidParameterError("matrix must be a square 2-D ndarray")
        if matrix.shape[0] % 2 == 0:
            raise InvalidParameterError("Aztec symbol side length must be odd")
        if data_words < 1:
            raise InvalidParameterError("data_words must be ≥ 1")

        self.matrix = matrix
        self.layers = layers
        self.data_words = data_words
        self.aztec_type = aztec_type
        self.auto_correct = auto_correct

    def _is_reference(self, r: int, c: int) -> bool:
        """Check if the given coordinates are part of the reference grid.
        A coordinate is part of the reference grid if it is a multiple of 16
        from the center of the matrix. The center is defined as the middle of the
        matrix (i.e. the middle row and column).

        Parameters
        ----------
        r : int
            Row index of the coordinate.
        c : int
            Column index of the coordinate.

        Returns
        -------
        bool
            True if the coordinate is part of the reference grid, False otherwise.
        """
        centre = self.matrix.shape[0] // 2
        return (r - centre) % 16 == 0 or (c - centre) % 16 == 0

    def _read_bits(self) -> np.ndarray:
        bitmap = []
        square_size = self.matrix.shape[0]
        reading_direction = ReadingDirection.BOTTOM
        start_point = (
            0,
            0,
        )  # We start reading from the top left corner to the bottom left corner
        end_point = (
            square_size
            - 1
            - 2,  # - 2 because the two last lines are readed in a different direction
            1,
        )
        # The number of cells to skip when we are reading layers in the middle of the matrix
        # So, if we are reading the first layer, we skip 0 cells, if we are reading the second layer, we skip 2 cells, etc.
        # It's used to adjust the starting point and the ending point of the reading
        apply_to_borns = 0

        for _ in range(1, self.layers * 4 + 1):
            for i in range(apply_to_borns, square_size - 2 + apply_to_borns):
                try:
                    if reading_direction == ReadingDirection.BOTTOM:
                        if (
                            not self._is_reference(i, start_point[1])
                            or self.aztec_type == AztecType.COMPACT
                        ):
                            bitmap.append(
                                self.matrix[i, start_point[1] : end_point[1] + 1]
                            )
                    elif reading_direction == ReadingDirection.RIGHT:
                        if (
                            not self._is_reference(start_point[0], i)
                            or self.aztec_type == AztecType.COMPACT
                        ):
                            bitmap.append(
                                self.matrix[start_point[0] : end_point[0] - 1 : -1, i]
                            )
                    elif reading_direction == ReadingDirection.TOP:
                        if (
                            not self._is_reference(
                                start_point[0] - i + apply_to_borns, start_point[1]
                            )
                            or self.aztec_type == AztecType.COMPACT
                        ):
                            bitmap.append(
                                self.matrix[
                                    start_point[0] - i + apply_to_borns,
                                    start_point[1] : end_point[1] - 1 : -1,
                                ]
                            )
                    else:  # LEFT
                        if (
                            not self._is_reference(
                                start_point[0], start_point[1] - i + apply_to_borns
                            )
                            or self.aztec_type == AztecType.COMPACT
                        ):
                            bitmap.append(
                                self.matrix[
                                    start_point[0] : end_point[0] + 1,
                                    start_point[1] - i + apply_to_borns,
                                ]
                            )
                except IndexError as exc:
                    raise BitReadError(
                        f"matrix index out of range while reading (layer offset={apply_to_borns})"
                    ) from exc

            if reading_direction == ReadingDirection.BOTTOM:
                start_point = (start_point[0] + square_size - 1, start_point[1])
                end_point = start_point
                end_point = (end_point[0] - 1, end_point[1] + square_size - 1 - 2)
                reading_direction = ReadingDirection.RIGHT
            elif reading_direction == ReadingDirection.RIGHT:
                start_point = (start_point[0], start_point[1] + square_size - 1)
                end_point = start_point
                end_point = (end_point[0] - square_size + 1 + 2, end_point[1] - 1)
                reading_direction = ReadingDirection.TOP
            elif reading_direction == ReadingDirection.TOP:
                start_point = (start_point[0] - square_size + 1, start_point[1])
                end_point = start_point
                end_point = (end_point[0] + 1, end_point[1] - square_size + 1 + 2)
                reading_direction = ReadingDirection.LEFT
            elif reading_direction == ReadingDirection.LEFT:
                # When we are going to the next layer, the square size is reduced by 4
                # because we are skipping the two last lines and the two first lines of the previous layer
                square_size -= 4
                apply_to_borns += 2
                start_point = end_point
                start_point = (start_point[0] + 1, start_point[1])
                # If the start point is a reference, we can skip this "one cell layer"
                if self._is_reference(start_point[0], start_point[1]):
                    start_point = (start_point[0] + 1, start_point[1] + 1)
                    square_size -= 2
                    apply_to_borns += 1
                end_point = start_point
                end_point = (end_point[0] + square_size - 1 - 2, end_point[1] + 1)
                reading_direction = ReadingDirection.BOTTOM

        if not bitmap:
            raise BitReadError(
                "no data modules extracted - check bull's-eye/layer count"
            )

        return np.concatenate(bitmap).astype(int)

    @cached_property
    def bitmap(self) -> np.ndarray:
        return self._read_bits()

    def _correct(self) -> List[int]:
        if self.layers <= 2:
            cw_size = 6
        elif self.layers <= 8:
            cw_size = 8
        elif self.layers <= 22:
            cw_size = 10
        else:
            cw_size = 12

        start_padding = len(self.bitmap) % cw_size
        bits = self.bitmap[
            start_padding:
        ]  # We need to have a multiple of cw_size, so we remove the padding bits

        prim = self.PRIM_POLY[cw_size]
        nsize = (1 << cw_size) - 1
        total_words = len(bits) // cw_size
        ecc_words = total_words - self.data_words
        if ecc_words <= 0:
            raise InvalidParameterError(
                "data_words exceeds total code-words in the symbol"
            )

        # We split the bits into code-words of size cw_size
        symbols = [
            int("".join(str(b) for b in bits[i * cw_size : (i + 1) * cw_size]), 2)
            for i in range(total_words)
        ]

        try:
            rs = reedsolo.RSCodec(
                nsym=ecc_words,
                nsize=nsize,
                fcr=1,
                generator=2,
                c_exp=cw_size,
                prim=prim,
            )
            _, full_codeword, _ = rs.decode(symbols)
        except reedsolo.ReedSolomonError as exc:
            raise ReedSolomonError(str(exc)) from exc

        corrected_bits = []
        for sym in full_codeword:
            for shift in range(cw_size - 1, -1, -1):
                corrected_bits.append((sym >> shift) & 1)

        return corrected_bits

    @cached_property
    def corrected_bits(self) -> List[int]:
        return self._correct()

    @classmethod
    def _bits_to_int(cls, bits: List[int]) -> int:
        return int("".join(str(b) for b in bits), 2)

    @classmethod
    def _bits_to_bytes(cls, bits: List[int]) -> bytes:
        return bytes(cls._bits_to_int(bits[i : i + 8]) for i in range(0, len(bits), 8))

    def _remove_stuff_bits(
        self, bits: List[int], cw_size: int, data_words: int
    ) -> List[int]:
        """Remove the stuffing bits from the bit-stream.
        A stuffed bit is a bit that is added to the bit-stream when there are cw_size-1
        consecutive bits of the same value. The stuffed bit is the opposite of the last bit.
        We need to remove the stuffed bits from the bit-stream before decoding it.
        Remove also the padding bits at the beginning of the stream.

        Parameters
        ----------
        bits : List[int]
            The bit-stream to clean.
        cw_size : int
            The size of the code-words (6, 8, 10 or 12).
        data_words : int
            The number of data code-words in the symbol.

        Returns
        -------
        List[int]
            The cleaned bit-stream without the stuffed bits and the padding bits.
        """
        cleaned = []
        i = 0
        words_seen = 0
        while words_seen < data_words and i < len(bits):
            run = bits[i : i + cw_size]
            if len(run) != cw_size:
                raise BitStuffingError("incomplete code-word at end of stream")
            if all(b == run[0] for b in run[:-1]):
                cleaned.extend(run[:-1])
                i += cw_size
            else:
                cleaned.extend(run)
                i += cw_size
            words_seen += 1
        # If the total number of bits is not a multiple of cw_size, we need to remove the padding bits
        start_padding = len(bits) % cw_size
        return cleaned[start_padding : data_words * cw_size]

    def _decode(self) -> str:
        if self.layers <= 2:
            codeword_size = 6
        elif self.layers <= 8:
            codeword_size = 8
        elif self.layers <= 22:
            codeword_size = 10
        else:
            codeword_size = 12

        if self.auto_correct:
            bits = self._remove_stuff_bits(
                self.corrected_bits, codeword_size, self.data_words
            )
        else:
            bits = self._remove_stuff_bits(self.bitmap, codeword_size, self.data_words)

        i = 0
        chars = []
        current_mode = AztecTableType.UPPER  # Default mode is UPPER
        previous_mode = AztecTableType.UPPER
        single_shift = False
        single_consumed = 0
        while True:
            bits_left = len(bits) - i
            needed = 4 if current_mode == AztecTableType.DIGIT else 5
            if bits_left < needed:
                break

            if single_shift and single_consumed == 1:
                current_mode = previous_mode
                single_shift = False
                single_consumed = 0

            if current_mode == AztecTableType.DIGIT:
                symbol_bits = bits[i : i + 4]
                i += 4  # DIGIT mode uses 4 bits for each symbol
            else:
                symbol_bits = bits[i : i + 5]
                i += 5  # UPPER, LOWER, MIXED and PUNCT modes use 5 bits for each symbol

            val = self._bits_to_int(symbol_bits)
            try:
                char = TableManager.get_char(val, current_mode)
            except KeyError as exc:
                raise SymbolDecodeError(
                    f"value {val} undefined in {current_mode.name} table"
                ) from exc

            if char == "B/S":
                if len(bits) - i < 5:
                    continue
                length = self._bits_to_int(bits[i : i + 5])
                i += 5
                if length == 0:
                    if len(bits) - i < 11:
                        raise StreamTerminationError(
                            "Byte-shift length=0 but 11-bit extension missing"
                        )
                    length = self._bits_to_int(bits[i : i + 11]) + 31
                    i += 11

                byte_bits = bits[i : i + 8 * length]
                if len(byte_bits) != 8 * length:
                    raise StreamTerminationError(
                        "Byte-shift claims more data than available"
                    )
                i += 8 * length
                chars.append(self._bits_to_bytes(byte_bits).decode("latin-1"))
                continue

            elif char.endswith("/S"):
                previous_mode = current_mode
                current_mode = TableManager.letter_to_mode(char[0])
                single_shift = True
                single_consumed = 0
                continue

            elif char.endswith("/L"):
                current_mode = TableManager.letter_to_mode(char[0])
                previous_mode = current_mode
                continue

            if char.startswith("FLG"):
                if len(bits) - i < 3:
                    raise StreamTerminationError(
                        "FLG announced but flag length bits missing"
                    )
                n = self._bits_to_int(bits[i : i + 3])
                i += 3
                if n == 0:
                    chars.append("\x1d")
                elif 1 <= n <= 6:
                    if len(bits) - i < 4 * n:
                        raise StreamTerminationError("ECI digits truncated")
                    digits = ""
                    for _ in range(n):
                        d = self._bits_to_int(bits[i : i + 4])
                        i += 4
                        digits += TableManager.get_char(d, AztecTableType.DIGIT)
                    eci_id = digits.zfill(6)
                    chars.append(f"[ECI:{eci_id}]")
                else:
                    raise SymbolDecodeError("FLG(7) is reserved/illegal")
                continue

            if char in ("U/S", "L/S", "M/S", "P/S", "D/S"):
                continue
            chars.append(char)

            if single_shift:
                single_consumed += 1

        return "".join(chars)

    @cached_property
    def decoded_string(self) -> str:
        return self._decode()
