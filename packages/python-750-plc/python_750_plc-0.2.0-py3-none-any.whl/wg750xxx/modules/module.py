"""Prototype module."""

from abc import abstractmethod
from collections.abc import Iterator
import logging
from typing import ClassVar, Self, overload

from wg750xxx.const import DEFAULT_SCAN_INTERVAL
from wg750xxx.modbus.state import (
    AddressDict,
    ModbusChannel,
    ModbusChannelType,
    ModbusConnection,
)
from wg750xxx.settings import ChannelConfig, ModuleConfig

from .channel import WagoChannel
from .exceptions import WagoModuleError
from .identifier import ModuleIdentifier
from .spec import ModuleSpec

log = logging.getLogger(__name__)


class WagoModule:
    """Base class for all Wago modules.

    This class is used to create a new WagoModule. It is not meant to be used directly. Create a subclass for each module type.

    Class variables (must be set in subclass):
    - spec: ModuleSpec: The specification of the module.
    - display_name: str: The display name of the module.
    - aliases: list[str]: A list of aliases for the module.
    - description: str: The description of the module.

    Instance properties:
    - modbus_connection: ModbusConnection: The modbus connection of the module.
    - modbus_address: AddressDict: The modbus address of the module. AddressDict is a dictionary the addresses of each type of modbus channel of the module.
    - modbus_channels: dict[ChannelType,list[ModbusChannelPrototype]]: The modbus channels of the module.
    - channels: Optional[WagoChannels]: The logical channels of the module. Can be None if the module does not have any logical channels.
    """

    spec: ModuleSpec = ModuleSpec()
    display_name: ClassVar[str] = "Undefined"
    aliases: ClassVar[list[str]] = []
    description: str = ""

    @classmethod
    def module_factory(
        cls,
        index: int,
        module_identifier: ModuleIdentifier,
        modbus_address: AddressDict,
        modbus_connection: ModbusConnection,
        update_interval: int | None = None,
        config: ModuleConfig | None = None,
    ) -> Self:
        """Create a new WagoModule using the factory pattern.

        This method will iterate over all subclasses of WagoModule and return the first one that matches the module_identifier.
        If no subclass is found, it will raise a NotImplementedError.

        Args:
            index: int: The index of the module.
            modbus_connection: ModbusConnection: The modbus connection of the module.
            module_identifier: ModuleIdentifier: The identifier of the module.
            modbus_address: AddressDict: The modbus address of the module.
            config: ModuleConfig | None: The configuration of the module.
            update_interval: int | None: The update interval of the module.

        Returns:
            WagoModule: The created WagoModule.

        Raises:
            NotImplementedError: If no subclass is found.

        """

        for subclass in cls.__subclasses__():
            if str(module_identifier) in subclass.aliases:
                return subclass(
                    index,
                    modbus_connection,
                    module_identifier=module_identifier,
                    modbus_address=modbus_address,
                    config=config,
                    update_interval=update_interval,
                )
        raise NotImplementedError(
            f"Subclass for Module type {module_identifier} not found"
        )

    def __init__(
        self,
        index: int,
        modbus_connection: ModbusConnection,
        modbus_address: AddressDict | None = None,
        module_identifier: ModuleIdentifier | None = None,
        config: ModuleConfig | None = None,
        auto_create_channels: bool = True,
        update_interval: int | None = None,
    ) -> None:
        """Initialize the WagoModule.

        This will set the spec, description, modbus_connection, modbus_channels and channels.
        If module_identifier or address is set, it will also set the module_identifier and modbus_address.

        Args:
            index: The index position of the module on the bus.
            modbus_connection: The modbus connection of the module.
            modbus_address: The modbus address of the module.
            module_identifier: The identifier of the module.
            config: The configuration settings for the module.
            auto_create_channels: Whether to automatically create channels during initialization.
            update_interval: The update interval of the module.

        Raises:
            WagoModuleError: If spec is not set in subclass.
            NotImplementedError: If module_identifier is not set and no address is provided.
            ValueError: If module_identifier is set and no address is provided.

        """
        self.spec: ModuleSpec = type(self).spec
        self.description: str = type(self).description
        self.modbus_connection: ModbusConnection = modbus_connection
        self._modbus_address: AddressDict | None = None
        self._display_name: str | None = None
        self._channel_init_config: list[ChannelConfig] | None = None
        self._config: ModuleConfig | None = None
        self.update_interval: int = update_interval or DEFAULT_SCAN_INTERVAL
        log.debug("Initializing module %s", self.__repr__())

        if module_identifier is not None:
            self.module_identifier = module_identifier

        self.index: int = index
        self._modbus_channels: dict[ModbusChannelType, list[ModbusChannel]] = {
            "coil": [],
            "discrete": [],
            "input": [],
            "holding": [],
        }

        if modbus_address is not None:
            self.modbus_address = modbus_address

        self.channels: list[WagoChannel] | None = None
        if config is not None:
            self.config = config
        if self.config is not None and self.config.index != index:
            raise ValueError(
                f"Module index {index} does not match config index {self.config.index}"
            )
        self.auto_create_channels = auto_create_channels
        if self.auto_create_channels:
            self.channels = []
            try:
                self.create_channels()
            except NotImplementedError:
                log.warning(
                    "Class not fully initialized yet, create_channels method not callable yet for %s.",
                    self.__class__.__name__,
                )
        log.debug("Finished initializing module %s", self.__repr__())

    @property
    def module_identifier(self) -> ModuleIdentifier:
        """Get the identifier of the module.

        The identifier of the module, usually a 3 digit number for most modules or DI and DO for digital modules.
        Identifier must match one of the aliases in one of the subclasses of WagoModule.
        """
        return self._module_identifier

    @module_identifier.setter
    def module_identifier(self, value: ModuleIdentifier) -> None:
        """Set the identifier of the module.

        This will also set the spec and description of the module for digital modules.
        Will raise an error for non-digital modules if spec is not set in subclass.
        """
        self._module_identifier = value
        if self.module_identifier.is_digital():
            self.spec = ModuleSpec(
                io_type=self.module_identifier.io_type(),
                modbus_channels=self.module_identifier.io_channels(),
                module_type=str(self.module_identifier),
            )
            self.description = f"{self.display_name} {self.module_identifier.channel_count()}-Kanal {self.module_identifier.io_type()}"
        else:
            if self.spec is None:
                raise WagoModuleError(
                    f"spec not set in {self.__class__.__name__}, must be set in subclass for non-digital modules"
                )
            self.spec.module_type = str(self.module_identifier)

    @property
    def modbus_address(self) -> AddressDict | None:
        """Get the modbus address of the module.

        The modbus address of the module.
        AddressDict is a dictionary the addresses of each type of modbus channel of the module.
        """
        return self._modbus_address

    @modbus_address.setter
    def modbus_address(self, value: AddressDict) -> None:
        """Set the modbus address of the module.

        This will also (re)create the modbus channels.
        """
        self._modbus_address = value
        self._reset_modbus_channel_configuration()
        self.modbus_channels = ModbusChannel.create_channels(
            self.spec.modbus_channels, self._modbus_address, self.modbus_connection
        )

    @property
    def modbus_channels(self) -> dict[ModbusChannelType, list[ModbusChannel]]:
        """Get the modbus channels of the module."""
        return self._modbus_channels

    @modbus_channels.setter
    def modbus_channels(
        self, value: dict[ModbusChannelType, list[ModbusChannel]]
    ) -> None:
        """Set the modbus channels of the module."""
        self._modbus_channels = value

    @property
    def config(self) -> ModuleConfig:
        """Get the configuration of the module."""
        if not hasattr(self, "_config") or self._config is None:
            self._config = ModuleConfig(
                index=self.index,
                type=self.spec.module_type,
                name=self.display_name or self.spec.module_type,
                update_interval=self.update_interval,
                channels=[channel.config for channel in self.channels]
                if self.channels is not None
                else None,
            )
        else:
            self._config.index = self.index
            self._config.name = self.display_name or self.spec.module_type
            self._config.channels = (
                [channel.config for channel in self.channels]
                if self.channels is not None
                else None
            )
        return self._config

    @config.setter
    def config(self, config: ModuleConfig | None) -> None:
        """Set the configuration of the module.

        This will also set the display name, index and config.
        """
        if config is not None:
            if config.type not in list(self.aliases):
                raise WagoModuleError(
                    f"Module type {config.type} does not match {self.spec.module_type}"
                )
            self._display_name = config.name or self.display_name
            self.index = config.index or self.index
            self.update_interval = config.update_interval or self.update_interval
            self._channel_init_config = config.channels or self._channel_init_config
            self._config = config
        else:
            self._config = self.config

    @property
    def name(self) -> str:
        """Get the display name of the module."""
        if not hasattr(self, "_display_name") or self._display_name is None:
            return self.spec.module_type
        return self._display_name

    @name.setter
    def name(self, value: str) -> None:
        """Set the display name of the module."""
        self._display_name = value

    @abstractmethod
    def create_channels(self) -> None:
        """Create the logical channels of the module. Must be implemented in the subclass."""
        raise NotImplementedError(
            f"create_channels method not implemented for {self.__class__.__name__}"
        )

    def append_channel(self, channel: WagoChannel) -> None:
        """Append a channel to the module."""
        # Channel index is the index of the current array position
        channel.channel_index = len(self.channels or [])
        channel.module_id = self.config.id
        if self._channel_init_config is not None:
            if channel.channel_index < len(self._channel_init_config):
                if (
                    self._channel_init_config[channel.channel_index].type
                    != channel.channel_type
                ):
                    raise ValueError(
                        f"""Channel type {self._channel_init_config[channel.channel_index].type} reported from
                        hub does not match channel type {channel.channel_type} specified in config"""
                    )
                channel.config = self._channel_init_config[channel.channel_index]
                channel.name = (
                    self._channel_init_config[channel.channel_index].name
                    or channel.channel_type
                )
                channel.update_interval = (
                    self._channel_init_config[channel.channel_index].update_interval
                    or self.update_interval
                )
            else:
                log.warning(
                    "More channels found (%d) in module %s than configured in config (%d). Check module configuration and update config.",
                    channel.channel_index + 1,
                    self.display_name,
                    len(self._channel_init_config),
                )
        if self.channels is None:
            self.channels = []
        self.channels.append(channel.get_instance())

    def _reset_modbus_channel_configuration(self) -> None:
        """Reset the channel configuration."""
        for channel_type in self.modbus_channels:
            self.modbus_channels[channel_type] = []

    @overload
    def get_next_address(self, channel_type: ModbusChannelType) -> int: ...

    @overload
    def get_next_address(self) -> AddressDict: ...

    def get_next_address(
        self, channel_type: ModbusChannelType | None = None
    ) -> AddressDict | int:
        """Get the next address for the given channel type.

        If channel_type is not provided, it will return the next address for all channel types.
        """
        if self.spec.modbus_channels is None:
            raise WagoModuleError(
                f"spec.io_channels not set in {self.__class__.__name__}"
            )
        if channel_type is None:
            result = {}
            for ch_type, value in self.spec.modbus_channels.items():
                if self.modbus_address is not None:
                    result[ch_type] = self.modbus_address.get(ch_type, 0) + value
                else:
                    result[ch_type] = value
            return result
        if self.modbus_address is not None:
            return self.modbus_address.get(
                channel_type, 0
            ) + self.spec.modbus_channels.get(channel_type, 0)
        return self.spec.modbus_channels.get(channel_type, 0)

    def config_dump(self) -> str:
        """Get a string representation of the module configuration."""
        return f"{self.description} ({self.spec})"

    def __iter__(self) -> Iterator[Self]:
        """Get an iterator with only the module itself."""
        return iter([self])

    def __str__(self) -> str:
        """Get a string representation of the module."""
        return self.description

    def __repr__(self) -> str:
        """Get a string representation of the module."""
        if self.spec is None:
            module_type = "Unknown"
        else:
            module_type = self.spec.module_type or "Unknown"
        return f"{self.__class__} object with id {hex(id(self))} ({module_type}:{self.display_name or 'Unknown'}:{self.modbus_address or 'Unknown'})"
