"""Registers module contains the classes for the words and bits of the Modbus registers."""

from collections.abc import Iterator
from types import EllipsisType
from typing import Literal, Self, overload

import numpy as np


class Bits:
    """A class to represent a Modbus one bit register of any length."""

    def __init__(
        self,
        bits: list[bool]
        | bool
        | Self
        | int
        | np.ndarray[tuple[int, ...], np.dtype[np.bool_]]
        | None = None,
        size: int = 0,
    ) -> None:
        """Initialize the Bits class."""
        if bits is None:
            self._bits = np.array([], dtype=bool)
        elif isinstance(bits, np.ndarray):
            self._bits = bits
        elif isinstance(bits, Bits):
            self._bits = bits.value
        elif isinstance(bits, int):
            self._bits = self._from_int(bits).value
        else:
            self._bits = np.array(bits, dtype=bool)
        if size == 0:
            size = self._bits.size
        # padding with zeros if width is greater than the number of bits given
        if size > len(self._bits):
            self._bits = np.pad(
                self._bits,
                (0, size - len(self._bits)),
                mode="constant",
                constant_values=False,
            )
        elif size < len(self._bits):
            self._bits = self._bits[:size]
        self.width: int = len(self._bits)

    def copy(self) -> Self:
        """Copy the bit register."""
        return self.__class__(self._bits.copy())

    def __str__(self) -> str:
        """Get the string representation of the bit register."""
        return "".join([f"{b}" for b in self._bits])

    def __repr__(self) -> str:
        """Get the string representation of the bit register."""
        return f"{self._bits}"

    def __int__(self) -> int:
        """Get the bit register content as integer representation."""
        return self.value_to_int()

    def _from_int(self, value: int) -> Self:
        """Convert an integer to a bit register."""
        return self.__class__(
            np.array(
                [int(b) for b in bin(value)[2:].zfill(len(self._bits))], dtype=bool
            )
        )

    @property
    def value(self) -> np.ndarray[tuple[int, ...], np.dtype[np.bool_]]:
        """Get the content of the bit register."""
        return self._bits

    @value.setter
    def value(
        self,
        bits: list[bool]
        | bool
        | Self
        | int
        | np.ndarray[tuple[int, ...], np.dtype[np.bool_]]
        | None,
    ) -> None:
        """Set the content of the bit register."""
        if bits is None:
            self._bits = np.array([], dtype=bool)
        elif isinstance(bits, bool):
            self._bits = np.array([bits], dtype=bool)
        elif isinstance(bits, int):
            self._bits = self._from_int(bits).value
        elif isinstance(bits, np.ndarray):
            self._bits = bits
        elif isinstance(bits, Bits):
            self._bits = bits.value
        else:
            self._bits = np.array(bits, dtype=bool)

    def value_to_hex(self) -> str:
        """Get the bit register content as hexadecimal string representation."""
        return "".join([f"{b:04X}" for b in self._bits])

    def value_to_bin(self) -> str:
        """Get the bit register content as binary string representation."""
        return "".join([f"{b:016b}" for b in self._bits])

    def value_to_int(self, byteorder: Literal["big", "little"] = "big") -> int:
        """Get the bit register content as integer representation."""
        bytes_instance = self.value_to_bytes()
        return int.from_bytes(bytes_instance.value, byteorder=byteorder)

    def value_to_bytes(self, byteorder: Literal["big", "little"] = "big") -> "Bytes":
        """Get the bit register content as byte register."""
        ## Pad the bit register to the nearest byte
        padding = (8 - len(self._bits) % 8) % 8
        padded_bits = np.pad(
            self._bits, (0, padding), mode="constant", constant_values=0
        )
        bytes_list = []
        for i in range(0, len(padded_bits), 8):
            byte = padded_bits[i : i + 8]
            bytes_list.append(sum(b << (i) for i, b in enumerate(byte)))
        if byteorder == "big":
            bytes_list.reverse()
        return Bytes(bytes_list)

    def value_to_words(self, wordorder: Literal["big", "little"] = "big") -> "Words":
        """Get the bit register content as word register."""
        padding = (16 - len(self._bits) % 16) % 16
        padded_bits = np.pad(
            self._bits, (0, padding), mode="constant", constant_values=0
        )
        words_list = []
        for i in range(0, len(padded_bits), 16):
            word = padded_bits[i : i + 16]
            words_list.append(sum(b << (i) for i, b in enumerate(word)))
        if wordorder == "big":
            words_list.reverse()
        return Words(words_list)

    def value_to_string(self) -> str:
        """Get the bit register content as string representation."""
        return "".join(
            [f"{chr(b & 0x00FF)}{chr(b >> 8)}" for b in self._bits if b != 0]
        ).rstrip("\x00")

    @overload
    def __getitem__(self, index: int) -> bool: ...

    @overload
    def __getitem__(self, index: slice) -> Self: ...

    def __getitem__(self, index: int | slice) -> bool | Self:
        """Get the bit register content at a specific index or slice."""
        if isinstance(index, slice):
            return self.__class__(self._bits[index])
        return self._bits[index]

    def __setitem__(
        self, index: int | slice | EllipsisType, value: bool | list[bool] | Self
    ) -> None:
        """Set the bit register content at a specific index or slice."""
        if isinstance(index, EllipsisType):
            if isinstance(value, Bits):
                self._bits[...] = value.value
            else:
                self._bits[...] = np.array(value, dtype=bool)
        elif isinstance(value, Bits):
            self._bits[index] = value.value
        else:
            self._bits[index] = value

    def __len__(self) -> int:
        """Get the length of the bit register."""
        return len(self._bits)

    def __iter__(self) -> Iterator[np.bool_]:
        """Get the iterator of the bit register."""
        return iter(self._bits)

    def __next__(self):
        """Get the next bit in the bit register."""
        return next(self._bits)

    def __missing__(self, index: int):
        """Get the bit at a specific index."""
        return self._bits[index]

    def __contains__(self, item) -> bool:
        """Check if the bit register contains a specific item."""
        if isinstance(item, Words):
            return np.array_equal(item.value, self.value)
        return False

    def __eq__(self, other) -> bool:
        """Check if the bit register is equal to another bit register."""
        if not isinstance(other, Words):
            return False
        if self.width != other.width:
            return False
        return np.array_equal(self._bits, other.value)

    def __ne__(self, other) -> bool:
        """Check if the bit register is not equal to another bit register."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Get the hash of the bit register."""
        return hash(self._bits)


class Bytes:
    """A class to represent a Modbus byte (8-bit) register of any length.

    Args:
        value:  The value to initialize the byte register with. Can be a
                list of integers, a numpy array of integers, an integer or None.
                Integer values higher than 255 will be split into multiple bytes.
                If the value is None, the byte register will be initialized to an
                empty array with the size provided.
        size:   The size of the byte register. If not provided, the size will be
                the size of the value. If the size is greater than the size of the
                value, the byte register will be padded with zeros. If the size is
                less than the size of the value, the byte register will be truncated.

    """

    def __init__(
        self,
        value: list[int]
        | Self
        | np.ndarray[tuple[int, ...], np.dtype[np.uint8]]
        | int
        | None = None,
        size: int = 0,
    ) -> None:
        """Initialize the Bytes class."""
        self._bytes: np.ndarray[tuple[int, ...], np.dtype[np.uint8]]
        if value is None:
            self._bytes = np.array([], dtype=np.uint8)
        elif isinstance(value, np.ndarray):
            self._bytes = value
        elif isinstance(value, Bytes):
            self._bytes = value.value
        elif isinstance(value, int):
            self._bytes = self.from_int(value).value
        else:
            self._bytes = np.array(value, dtype=np.uint8)
        if size == 0:
            size = self._bytes.size
        # padding with zeros if width is greater than the number of bytes given
        if size > self._bytes.size:
            self._bytes = np.pad(
                self._bytes,
                (0, size - self._bytes.size),
                mode="constant",
                constant_values=0,
            )
        elif size < self._bytes.size:
            self._bytes = self._bytes[:size]
        self.width: int = self._bytes.size

    @staticmethod
    def from_int(value: int, byteorder: str = "little") -> "Bytes":
        """Convert an integer to a byte register."""
        if value < 256:
            return Bytes(np.array([value], dtype=np.uint8))
        # split the integer into bytes
        values = np.array([], dtype=np.uint8)
        if byteorder == "big":
            while value > 0:
                values = np.insert(values, 0, value & 0xFF)
                value >>= 8
        else:
            while value > 0:
                values = np.append(values, value & 0xFF)
                value >>= 8
        return Bytes(values)

    def __len__(self) -> int:
        """Get the length of the byte register."""
        return self._bytes.size

    @property
    def value(self) -> np.ndarray[tuple[int, ...], np.dtype[np.uint8]]:
        """Get the content of the byte register."""
        return self._bytes

    @value.setter
    def value(
        self,
        value: list[int]
        | np.ndarray[tuple[int, ...], np.dtype[np.uint8]]
        | Self
        | int
        | None,
    ) -> None:
        """Set the content of the byte register."""
        # if isinstance(value, (list, np.ndarray, Bytes)):
        #     if len(value) != self._bytes.size:
        #         raise ValueError(
        #             f"Invalid value length, register has {self._bytes.size} bytes, got {len(value)}"
        #         )
        if value is None:
            self._bytes = np.array([], dtype=np.uint8)
        elif isinstance(value, np.ndarray):
            self._bytes[...] = value
        elif isinstance(value, Bytes):
            self._bytes[...] = value.value
        elif isinstance(value, int):
            bytes_obj = self.from_int(value)
            self._bytes[...] = bytes_obj.value
        else:
            self._bytes[...] = np.array(value, dtype=np.uint8)

    def __str__(self) -> str:
        """Get the string representation of the byte register."""
        return self.value_to_hex()

    def __repr__(self) -> str:
        """Get the string representation of the byte register."""
        return f"{self._bytes}"

    def copy(self) -> Self:
        """Copy the byte register."""
        return self.__class__(self._bytes.copy())

    def value_to_hex(self) -> str:
        """Get the byte register content as hexadecimal string representation."""
        return "".join([f"{b:02X}" for b in self._bytes])

    def value_to_bin(self) -> str:
        """Get the byte register content as binary string representation."""
        return "".join([f"{b:08b}" for b in self._bytes])

    def value_to_int(self, byteorder: Literal["little", "big"] = "little") -> int:
        """Get the byte register content as integer representation."""
        return int.from_bytes(bytes(self._bytes.tolist()), byteorder=byteorder)

    def bits(self) -> Bits:
        """Get the byte register content as bit register."""
        bit_list: list[bool] = []
        for byte in self._bytes:
            bit_list.extend(bool((byte >> i) & 1) for i in range(7, -1, -1))
        return Bits(bit_list)

    def __int__(self) -> int:
        """Get the byte register content as integer representation."""
        return self.value_to_int()

    def value_to_float(self) -> float:
        """Get the byte register content as float representation."""
        return float(self.value_to_int())

    def value_to_string(self) -> str:
        """Get the byte register content as string representation."""
        return "".join(
            [f"{chr(b & 0x00FF)}{chr(b >> 8)}" for b in self._bytes if b != 0]
        ).rstrip("\x00")

    @overload
    def __getitem__(self, index: slice) -> Self: ...

    @overload
    def __getitem__(self, index: int) -> bool: ...

    def __getitem__(self, index: int | slice) -> bool | Self:
        """Get the byte register content at a specific index or slice."""
        if isinstance(index, slice):
            return self.__class__(self._bytes[index])
        if isinstance(index, int):
            return self.__class__(np.array([self._bytes[index]], dtype=np.uint8))
        raise TypeError(f"Invalid index type: {type(index)}")

    def __setitem__(
        self, index: int | slice | EllipsisType, value: int | list[int] | Self
    ) -> None:
        """Set the byte register content at a specific index or slice."""
        if isinstance(index, EllipsisType):
            if isinstance(value, Bytes):
                self._bytes[...] = value.value
            else:
                self._bytes[...] = np.array(value, dtype=np.uint8)
        elif isinstance(value, Bytes):
            self._bytes[index] = value.value
        else:
            self._bytes[index] = value

    def __eq__(self, other) -> bool:
        """Check if the byte register is equal to another byte register."""
        if not isinstance(other, Bytes):
            return False
        if self.width != other.width:
            return False
        return np.array_equal(self._bytes, other.value)

    def __ne__(self, other) -> bool:
        """Check if the byte register is not equal to another byte register."""
        return not self.__eq__(other)

    def __iter__(self) -> Iterator[int]:
        """Get the iterator of the byte register."""
        return iter(self._bytes)

    def __next__(self) -> int:
        """Get the next byte in the byte register."""
        return int(next(iter(self._bytes)))


class Words:
    """A class to represent a Modbus word (16-bit) register of any length.

    Args:
        value:  The value to initialize the word register with. Can be a
                list of integers, a numpy array of integers, an integer or None.
                Integer values higher than 65535 will be split into multiple words.
                If the value is None, the word register will be initialized to an
                empty array with the size provided.
        size:   The size of the word register. If not provided, the size will be
                the size of the value. If the size is greater than the size of the
                value, the word register will be padded with zeros. If the size is
                less than the size of the value, the word register will be truncated.

    """

    def __init__(
        self,
        value: list[int]
        | np.ndarray[tuple[int, ...], np.dtype[np.uint16]]
        | Self
        | int
        | None = None,
        size: int = 0,
    ) -> None:
        """Initialize the Words class."""
        if value is None:
            self._words = np.array([], dtype=np.uint16)
        elif isinstance(value, np.ndarray):
            self._words = value
        elif isinstance(value, Words):
            self._words = value.value
        elif isinstance(value, int):
            self._words = self.from_int(value)
        else:
            self._words = np.array(value, dtype=np.uint16)
        if size == 0:
            size = self._words.size
        # padding with zeros if width is greater than the number of words given
        if size > len(self._words):
            self._words = np.pad(
                self._words,
                (0, size - len(self._words)),
                mode="constant",
                constant_values=0,
            )
        elif size < len(self._words):
            self._words = self._words[:size]
        self.width: int = len(self._words)

    @staticmethod
    def from_int(
        value: int, byteorder: str = "big"
    ) -> np.ndarray[tuple[int, ...], np.dtype[np.uint16]]:
        """Convert an integer to a word register."""
        if value < 65536:
            return np.array([value], dtype=np.uint16)
        # split the integer into bytes
        values = np.array([], dtype=np.uint16)
        if byteorder == "big":
            while value > 0:
                values = np.insert(values, 0, value & 0xFFFF)
                value >>= 16
        else:
            while value > 0:
                values = np.append(values, value & 0xFFFF)
                value >>= 16
        return values

    def copy(self) -> Self:
        """Copy the word register."""
        return self.__class__(self._words.copy())

    def __str__(self) -> str:
        """Get the string representation of the word register."""
        return self.value_to_hex()

    def __repr__(self) -> str:
        """Get the string representation of the word register."""
        return f"{self._words}"

    @property
    def value(self) -> np.ndarray[tuple[int, ...], np.dtype[np.uint16]]:
        """Get the content of the word register."""
        return self._words

    @value.setter
    def value(
        self,
        value: list[int]
        | np.ndarray[tuple[int, ...], np.dtype[np.uint16]]
        | Self
        | int
        | None,
    ) -> None:
        """Set the content of the word register."""
        # if isinstance(value, (list, np.ndarray, Words)):
        #     if len(value) != self._words.size:
        #         raise ValueError(
        #             f"Invalid value length, register has {self._words.size} words, got {len(value)}"
        #         )
        if value is None:
            self._words = np.array([], dtype=np.uint16)
        elif isinstance(value, np.ndarray):
            self._words[...] = value
        elif isinstance(value, Words):
            self._words[...] = value.value
        elif isinstance(value, int):
            self._words[...] = self.from_int(value)
        else:
            self._words[...] = np.array(value, dtype=np.uint16)

    def value_to_hex(self) -> str:
        """Get the word register content as hexadecimal string representation."""
        return "".join([f"{w:04X}" for w in self._words])

    def value_to_bin(self) -> str:
        """Get the word register content as binary string representation."""
        return "".join([f"{b:016b}" for b in self._words])

    def value_to_int(self, byteorder: Literal["little", "big"] = "big") -> int:
        """Get the word register content as integer representation."""
        return self.bytes(byteorder).value_to_int()

    def bits(self) -> Bits:
        """Get the word register content as bit register."""
        bit_list: list[bool] = []
        for word in self._words:
            bit_list.extend(bool((word >> i) & 1) for i in range(15, -1, -1))
        return Bits(bit_list)

    def bytes(self, byteorder: str = "little") -> Bytes:
        """Convert the word register to a byte register."""
        byte_list = []
        if byteorder == "big":
            words = np.flip(self._words)
        else:
            words = self._words
        for word in words:
            high_byte = (word >> 8) & 0xFF
            low_byte = word & 0xFF
            if byteorder == "big":
                byte_list.append(low_byte)
                byte_list.append(high_byte)
            else:
                byte_list.append(high_byte)
                byte_list.append(low_byte)
        return Bytes(byte_list)

    def __int__(self) -> int:
        """Get the word register content as integer representation."""
        return self.value_to_int()

    def value_to_string(self) -> str:
        """Get the word register content as string representation."""
        return "".join(
            [f"{chr(b & 0x00FF)}{chr(b >> 8)}" for b in self._words if b != 0]
        ).rstrip("\x00")

    def __getitem__(self, index: slice | int) -> Self:
        """Get the word register content at a specific index or slice."""
        if isinstance(index, slice):
            return self.__class__(self._words[index])
        if isinstance(index, int):
            return self.__class__(np.array([self._words[index]], dtype=np.uint16))
        raise TypeError(f"Invalid index type: {type(index)}")

    def __setitem__(
        self, index: int | slice | EllipsisType, value: int | list[int] | Self
    ) -> None:
        """Set the word register content at a specific index or slice."""
        if isinstance(index, EllipsisType):
            if isinstance(value, Words):
                self._words[...] = value.value
            else:
                self._words[...] = np.array(value, dtype=np.uint16)
        elif isinstance(value, Words):
            self._words[index] = value.value
        else:
            self._words[index] = value

    def __len__(self) -> int:
        """Get the length of the word register."""
        return len(self._words)

    def __iter__(self) -> Iterator[int]:
        """Get the iterator of the word register."""
        return iter(self._words)

    def __next__(self) -> int:
        """Get the next word in the word register."""
        return int(next(iter(self._words)))

    def __missing__(self, index: int) -> int:
        """Get the word at a specific index."""
        return self._words[index]

    def __contains__(self, item) -> bool:
        """Check if the word register contains a specific item."""
        if isinstance(item, Words):
            return np.array_equal(item.value, self.value)
        return False

    def __eq__(self, other) -> bool:
        """Check if the word register is equal to another word register."""
        if not isinstance(other, Words):
            return False
        if self.width != other.width:
            return False
        return np.array_equal(self._words, other.value)

    def __ne__(self, other) -> bool:
        """Check if the word register is not equal to another word register."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Get the hash of the word register."""
        return hash(self._words)


class Register(Words):
    """A class to represent a Modbus register with an address."""

    def __init__(self, address: int, *args, **kwargs) -> None:
        """Initialize the Register class."""
        self.address: int = address
        super().__init__(*args, **kwargs)

    def __getitem__(self, index: slice | int) -> Self:
        """Get the word register content at a specific index or slice."""
        if isinstance(index, slice):
            address = self.address + index.start
            return self.__class__(address, self._words[index])
        if isinstance(index, int):
            address = self.address + index
            return self.__class__(
                address, np.array([self._words[index]], dtype=np.uint16)
            )
        raise TypeError(f"Invalid index type: {type(index)}")

    def __str__(self) -> str:
        """Get the string representation of the register."""
        if self.width > 0:
            return f"Address: 0x{self.address:04X}, Value: 0x{self.value_to_hex()}"
        return f"Address: 0x{self.address:04X}, Value: N/A"

    def __repr__(self) -> str:
        """Get the string representation of the register."""
        return f"0x{self.address:04X}:{self.value_to_hex()}"

    def __eq__(self, other) -> bool:
        """Check if the register is equal to another register."""
        return self.address == other.address and self._words == other.value

    def __ne__(self, other) -> bool:
        """Check if the register is not equal to another register."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Get the hash of the register."""
        return hash(self.address) ^ hash(self._words)


test_constants = [
    Register(0x2000, [0x0000]),
    Register(0x2001, [0xFFFF]),
    Register(0x2002, [0x1234]),
    Register(0x2003, [0xAAAA]),  # Maske 1, GP_AAAA
    Register(0x2004, [0x5555]),  # Maske 1, GP_5555
    Register(0x2005, [0x7FFF]),  # GP_MIN_POS
    Register(0x2006, [0x8000]),  # GP_MAX_NEG
    Register(0x2007, [0x3FFF]),  # GP_HALF_POS
    Register(0x2008, [0x4000]),  # GP_HALF_NEG
]
