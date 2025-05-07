from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union, cast

from wexample_config.config_option.abstract_config_option import AbstractConfigOption
from wexample_config.config_option.config_option import ConfigOption
from wexample_config.const.types import DictConfig
from wexample_config.options_provider.abstract_options_provider import (
    AbstractOptionsProvider,
)

if TYPE_CHECKING:
    from wexample_config.config_value.config_value import ConfigValue


class AbstractNestedConfigOption(AbstractConfigOption):
    allow_undefined_keys: bool = False
    options: dict[str, AbstractConfigOption] = {}
    options_providers: Optional[list[type[AbstractOptionsProvider]]] = None
    parent: Optional["AbstractConfigOption"] = None

    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return dict[str, Any]

    def set_value(self, raw_value: Any) -> None:
        # Config might have been modified
        raw_value = super().set_value(raw_value)

        if raw_value is None:
            return

        self._create_options(config=raw_value)

    def _create_options(self, config: DictConfig) -> List["AbstractConfigOption"]:
        from wexample_config.config_value.callback_render_config_value import (CallbackRenderConfigValue)

        options = self.get_available_options()
        valid_option_names = set(options.keys())
        new_options = []

        # Loop over all options classes to execute option_class.resolve_config(config)
        # This will modify config before using it, with extra configuration keys.
        # For instance, an option defining the content of a file may add the should_exist option to ensure existence.
        for option_class in options.values():
            config = option_class.resolve_config(config)

        unknown_keys = set(config.keys()) - valid_option_names
        if unknown_keys:
            if not self.allow_undefined_keys:
                from wexample_config.exception.option import InvalidOptionException

                raise InvalidOptionException(
                    f"Unknown configuration option \"{', '.join(sorted(unknown_keys))}\", "
                    f'in "{self.__class__.__name__}", '
                    f"allowed options are: {', '.join(valid_option_names)}"
                )
            else:
                for option_name in unknown_keys:
                    if not isinstance(config[option_name], AbstractConfigOption):
                        # Wrap unknown options
                        config[option_name] = ConfigOption(
                            key=option_name,
                            parent=self,
                            value=config[option_name]
                        )

        # Resolve callables and process children recursively
        for key, child_raw_value in list(config.items()):
            if isinstance(child_raw_value, CallbackRenderConfigValue):
                config[key] = child_raw_value.render(self)

        for option_name, option_config in config.items():
            if isinstance(option_config, AbstractConfigOption):
                new_option = option_config
                new_option.parent = self
            else:
                new_option = options[option_name](
                    parent=self,
                    value=option_config,
                )

            self.options[new_option.get_key()] = new_option
            new_options.append(new_option)

        return new_options

    def get_options_providers(self) -> list[type["AbstractOptionsProvider"]]:
        if self.parent:
            return self.parent.get_options_providers()

        if self.options_providers:
            return self.options_providers

        return []

    def get_available_options(self) -> dict[str, type["AbstractConfigOption"]]:
        providers = self.get_options_providers()
        options = {}

        for provider in providers:
            options.update(cast("AbstractOptionsProvider", provider).get_options_registry())

        return options

    def get_option(
        self, option_type: Union[type["AbstractConfigOption"], str]
    ) -> Optional["AbstractConfigOption"]:
        option_name = (
            option_type.get_name() if not isinstance(option_type, str) else option_type
        )

        if option_name in self.options:
            return self.options[option_name]

        return None

    def get_option_recursive(
        self, option_type: Union[type["AbstractConfigOption"], str]
    ) -> Optional["AbstractConfigOption"]:
        option = self.get_option(option_type)

        if option is not None:
            return option

        for option in self.options.values():
            if isinstance(option, AbstractNestedConfigOption):
                found_option = option.get_option_recursive(option_type)
                if found_option is not None:
                    return found_option

        return None

    def get_option_value(
        self, option_type: type["AbstractConfigOption"], default: Any = None
    ) -> "ConfigValue":
        from wexample_config.config_value.config_value import ConfigValue

        option = self.get_option(option_type)
        if option:
            return cast("ConfigValue", option.get_value())

        return ConfigValue(raw=default)

    def dump(self) -> Any:
        output = {}

        for name, option in self.options.items():
            output[name] = option.dump()

        return output
