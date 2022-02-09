from fractions import Fraction
from struct import unpack
from typing import List, Literal, Optional

from async_cog.tags.tag import Tag


class FractionsTag(Tag):
    value: Optional[List[Fraction]]

    class Config:
        arbitrary_types_allowed = True

    def parse_data(self, data: bytes, byte_order_fmt: Literal["<", ">"]) -> None:
        """
        Each fraction in TIFF represented by two LONGs: numerator and denominator.
        Parse them into list of Fractions
        """

        # "I" is for unsigned LONGs and "i" for signed
        type_str = "I" if self.type == 5 else "i"

        # 2 * n values of type (un)signed LONG
        format_str = f"{byte_order_fmt}{self.length * 2}{type_str}"
        values = unpack(format_str, data)

        numerators = values[::2]  # evens
        denominators = values[1::2]  # odds

        self.value = [
            Fraction(numerator, denominator)
            for numerator, denominator in zip(numerators, denominators)
        ]
