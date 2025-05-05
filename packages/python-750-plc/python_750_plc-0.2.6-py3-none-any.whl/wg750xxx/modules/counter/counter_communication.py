"""Counter communication."""

from wg750xxx.modbus.registers import Register, Words
from wg750xxx.modbus.state import AddressDict, ModbusConnection


class CounterControlByte:
    """Counter control byte."""

    def __init__(self, register: Register, modbus_connection: ModbusConnection) -> None:
        """Initialize the CounterControlByte."""
        self.register: Register = register
        self.modbus_connection: ModbusConnection = modbus_connection

    def _set_and_write(self, bit_index: int, value: bool) -> None:
        """Set the bit and write the register to the modbus."""
        self.register.bits()[bit_index] = value
        self.modbus_connection.write_registers(self.register.address, self.register)

    @property
    def set_counter(self) -> bool:
        """Check if the counter is set."""
        return self.register.bits()[5]

    @set_counter.setter
    def set_counter(self, value: bool) -> None:
        """Set the counter."""
        self._set_and_write(5, value)

    @property
    def lock(self) -> bool:
        """Check if the counter is locked."""
        return self.register.bits()[4]

    @lock.setter
    def lock(self, value: bool) -> None:
        """Lock the counter."""
        self._set_and_write(4, value)

    @property
    def set_do2(self) -> bool:
        """Check if the DO2 is set."""
        return self.register.bits()[3]

    @set_do2.setter
    def set_do2(self, value: bool) -> None:
        """Set the DO2."""
        self._set_and_write(3, value)

    @property
    def set_do1(self) -> bool:
        """Check if the DO1 is set in output register."""
        return self.register.bits()[2]

    @set_do1.setter
    def set_do1(self, value: bool) -> None:
        """Set the DO1 in output register."""
        self._set_and_write(2, value)


class CounterStatusByte:
    """Counter status byte."""

    def __init__(self, register: Register, modbus_connection: ModbusConnection) -> None:
        """Initialize the CounterStatusByte."""
        self.register: Register = register
        self.modbus_connection: ModbusConnection = modbus_connection

    def _read(self, bit_index: int) -> bool:
        """Read the bit from the register."""
        value = self.modbus_connection.read_input_registers(self.register.address, 1)
        if hasattr(value, "bits"):
            return bool(value.bits()[bit_index])
        return False

    @property
    def ack_set_counter(self) -> bool:
        """Check if the counter is set."""
        return self._read(5)

    @property
    def locked(self) -> bool:
        """Check if the counter is locked."""
        return self._read(4)

    @property
    def current_level_do2(self) -> bool:
        """Check if the counter is set."""
        return self._read(3)

    @property
    def current_level_do1(self) -> bool:
        """Check if the counter is set."""
        return self._read(2)

    @property
    def current_level_ud(self) -> bool:
        """Check if the counter is set."""
        return self._read(1)

    @property
    def current_level_clock(self) -> bool:
        """Check if the counter is set."""
        return self._read(0)


class CounterCommunicationRegister:
    """Counter communication register."""

    def __init__(
        self, modbus_connection: ModbusConnection, modbus_address: AddressDict
    ) -> None:
        """Initialize the CounterCommunicationRegister."""
        self.modbus_connection = modbus_connection
        self.modbus_address = modbus_address

        # Read the input registers
        input_registers = self.modbus_connection.read_input_registers(
            self.modbus_address["input"], 3, update=True
        )
        self.input_register = Register(
            self.modbus_address["input"], input_registers.value
        )

        # Read the output registers
        holding_registers = self.modbus_connection.read_holding_registers(
            self.modbus_address["holding"], 3, update=True
        )
        self.output_register = Register(
            self.modbus_address["holding"], holding_registers.value
        )

        # Create control and status bytes
        self.control_byte = CounterControlByte(
            Register(self.modbus_address["holding"], [self.output_register.value[0]]),
            modbus_connection,
        )
        self.status_byte = CounterStatusByte(
            Register(self.modbus_address["input"], [self.input_register.value[0]]),
            modbus_connection,
        )

    @property
    def value(self) -> int:
        """Get the value of the counter."""
        register_subset = self.input_register[1:3]
        bytes_instance = register_subset.bytes()
        return bytes_instance.value_to_int()

    @value.setter
    def value(self, value: int) -> None:
        """Set the value of the counter."""
        # Convert value to bytes and create Words object
        value_bytes = value.to_bytes(4, byteorder="little")
        word_values = [
            int.from_bytes(value_bytes[0:2], byteorder="little"),
            int.from_bytes(value_bytes[2:4], byteorder="little"),
        ]
        self.input_register[1:3] = Words(word_values)  # type: ignore[assignment]
        self.control_byte.set_counter = True
        # TODO: we should async wait for the counter to be reset
        if self.status_byte.ack_set_counter:
            self.control_byte.set_counter = False

    def reset(self) -> None:
        """Reset the counter."""
        self.value = 0

    def lock(self) -> None:
        """Lock the counter."""
        self.control_byte.lock = True

    def unlock(self) -> None:
        """Unlock the counter."""
        self.control_byte.lock = False
