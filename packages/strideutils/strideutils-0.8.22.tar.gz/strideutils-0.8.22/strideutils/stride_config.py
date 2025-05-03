"""
This file loads and provide an object `config` to access all secrets, configs, and chain info
"""

import os
from dataclasses import dataclass, field, fields
from typing import Any, Dict, List, Optional, cast

import yaml
from dotenv import load_dotenv

MISSING_CONFIG_MSG = "Configuration or environment variable '{x}' is not set or unknown"

ENV = os.environ.get("ENV")
if ENV not in ["DEV", "PROD"]:
    raise ValueError("Environment variable 'ENV' must be set to either DEV or PROD")


def get_redis_password_env_var(db_name: str) -> str:
    """Generate the environment variable name for a Redis database password"""
    return f"REDIS_{db_name.upper()}_PASSWORD"


@dataclass(frozen=True)
class Environment:
    """
    List of all possible environment variables
    """

    TWILIO_ALERTS_NUMBER = "TWILIO_ALERTS_NUMBER"
    TWILIO_ACCOUNT_ID = "TWILIO_ACCOUNT_ID"
    TWILIO_API_TOKEN = "TWILIO_API_TOKEN"

    STRIDEBOT_API_TOKEN = "STRIDEBOT_API_TOKEN"
    STRIDEBOT_APP_TOKEN = "STRIDEBOT_APP_TOKEN"
    SLACK_CHANNEL_OVERRIDE = "SLACK_CHANNEL_OVERRIDE"

    PUBLICSHEETS_AUTH = "PUBLICSHEETS_AUTH"

    COINGECKO_API_TOKEN = "COINGECKO_API_TOKEN"

    TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN"

    @staticmethod
    def get_redis_password_var(db_name: str) -> str:
        """Get the environment variable name for a Redis database password"""
        return get_redis_password_env_var(db_name)


def get_env_or_raise(variable_name: str) -> str:
    """
    Attempts to fetch and return the environment variable, but errors
    if it's not set
    """
    value = os.getenv(variable_name)
    if not value:
        raise EnvironmentError(f"Environment variable {variable_name} must be set")
    return value


@dataclass
class ConfigObj:
    """Raise an error if a config is not set."""

    def __getattribute__(self, name):
        """
        Called every time a field is attempted to be accessed
        Falls back to getattr if the field is not found
        """
        value = super().__getattribute__(name)
        if value == "" or value is None:
            raise AttributeError(MISSING_CONFIG_MSG.format(x=name))
        return value

    def __iter__(self):
        """Allow iterating over set values"""
        for subfield in fields(self):
            if hasattr(self, subfield.name):
                yield getattr(self, subfield.name)

    def __contains__(self, field) -> bool:
        """Allows for checking if an attribute is present with `in`"""
        if not hasattr(self, field):
            return False
        return bool(getattr(self, field))


class ConfigDict(dict):
    def __getitem__(self, key):
        """Raise an error if an unset key is indexed."""
        if key not in self:
            raise KeyError(MISSING_CONFIG_MSG.format(x=key))
        value = super().__getitem__(key)
        if value == "" or value is None:
            raise KeyError(MISSING_CONFIG_MSG.format(x=key))
        return value


# Use ConfigDict in the yaml parser
class Loader(yaml.FullLoader):
    def construct_yaml_map(self, node):
        data = ConfigDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)


Loader.add_constructor('tag:yaml.org,2002:map', Loader.construct_yaml_map)


@dataclass(repr=False)
class ChainConfig(ConfigObj):
    """Config relevant for all chains"""

    name: str = ""
    id: str = ""
    coingecko_name: str = ""
    denom: str = ""
    denom_decimals: int = 6
    ticker: str = ""
    api_endpoint: str = ""
    rpc_endpoint: str = ""
    evm_chain: bool = False

    def __repr__(self) -> str:
        return f"ChainConfig(name={self.name}, id={self.id})"


@dataclass(repr=False)
class StrideChainConfig(ChainConfig):
    """Config specific to stride"""

    library_api_endpoint: str = ""
    library_rpc_endpoint: str = ""

    def __repr__(self) -> str:
        return f"StrideChainConfig(name={self.name}, id={self.id})"


@dataclass(repr=False)
class HostChainConfig(ChainConfig):
    """Config specific to stride's host zones"""

    # Frequency with which staking rewards are issued
    # -1 indicates every block
    inflation_frequency_hours: int = -1
    # IBC denom of the native token as it sits on stride
    denom_on_stride: str = ""
    # Indicates whether the chain has ICA enabled
    ica_enabled: bool = True
    # Indicates whether the chain has LSM enabled
    lsm_enabled: bool = False

    def __repr__(self) -> str:
        return f"HostChainConfig(name={self.name}, id={self.id})"


@dataclass
class RedisConfig(ConfigObj):
    """Configuration for a Redis instance"""

    host: str
    port: int
    ssl: bool = False


@dataclass(repr=False)
class Config(ConfigObj):
    ENV: str
    timezone: str = "US/Eastern"
    founders: List[str] = field(default_factory=lambda: ['riley', 'aidan', 'vishal'])

    redis: Dict[str, RedisConfig] = field(default_factory=dict)

    # Stride alerts
    alerts_playbook: str = ""
    slack_channels: ConfigDict = field(default_factory=ConfigDict)

    # Chain configs
    stride: StrideChainConfig = field(default_factory=StrideChainConfig)
    _host_zones: Dict[str, HostChainConfig] = field(default_factory=dict)
    _app_chains: Dict[str, ChainConfig] = field(default_factory=dict)

    @property
    def host_zones(self) -> List[HostChainConfig]:
        return [host_zone for host_zone in self._host_zones.values()]

    @property
    def stakeibc_host_zones(self) -> List[HostChainConfig]:
        return [host_zone for host_zone in self._host_zones.values() if host_zone.ica_enabled]

    @property
    def app_chains(self) -> List[ChainConfig]:
        return [app_chain for app_chain in self._app_chains.values()]

    @property
    def chains(self) -> List[ChainConfig]:
        return self.host_zones + self.app_chains

    @property
    def host_zone_names(self) -> List[str]:
        return [host_zone for host_zone in self._host_zones.keys()]

    @property
    def app_chain_names(self) -> List[str]:
        return [app_chain for app_chain in self._app_chains.keys()]

    def _evaluate_chain_match(
        self,
        chain: ChainConfig,
        name: Optional[str],
        id: Optional[str],
        ticker: Optional[str],
        denom: Optional[str],
        denom_on_stride: Optional[str],
    ) -> bool:
        try:
            if name is not None:
                return chain.name == name

            if id is not None:
                return chain.id == id

            if ticker is not None:
                if hasattr(chain, "denom"):
                    denom = chain.denom
                else:
                    denom = chain.ticker
                chain_tickers = [chain.ticker, chain.ticker.upper(), chain.ticker.lower(), denom]
                return ticker in chain_tickers

            if denom is not None:
                return chain.denom == denom

            if denom_on_stride is not None:
                if isinstance(chain, HostChainConfig):
                    return chain.denom_on_stride == denom_on_stride

        except AttributeError:
            # if our local config doesn't have the relevant attribute, e.g. "ticker"
            # we gracefully return "not a match"
            return False

        return False

    def get_chain(
        self,
        name: Optional[str] = None,
        id: Optional[str] = None,
        ticker: Optional[str] = None,
        denom: Optional[str] = None,
        denom_on_stride: Optional[str] = None,
    ) -> ChainConfig:
        """
        Fetch info about a host zone by name, id, ticker, denom, or token hash.

        Raises
            KeyError if a valid chain doesn't exist or if multiple parameters are specified.
        """
        if sum(map(bool, [name, id, ticker, denom, denom_on_stride])) != 1:
            raise KeyError("Exactly one of name, id, ticker, denom, or token hash must be specified.")

        if (
            name == self.stride.name
            or id == self.stride.id
            or ticker == self.stride.ticker
            or denom == self.stride.denom
        ):
            return self.stride

        for chain in self.chains:
            if self._evaluate_chain_match(
                chain=chain,
                name=name,
                id=id,
                ticker=ticker,
                denom=denom,
                denom_on_stride=denom_on_stride,
            ):
                return chain

        raise KeyError("No chain found for the given parameter")

    def get_host_chain(
        self,
        name: Optional[str] = None,
        id: Optional[str] = None,
        ticker: Optional[str] = None,
        denom: Optional[str] = None,
        denom_on_stride: Optional[str] = None,
    ) -> HostChainConfig:
        """
        Gets a host chain config from its various attributes.

        Raises:
            KeyError if a valid host chain doesn't exist or if multiple parameters are specified
            TypeError if the found chain is not a host chain
        """
        if sum(map(bool, [name, id, ticker, denom, denom_on_stride])) != 1:
            raise KeyError("Exactly one of name, id, ticker, denom, or token hash must be specified.")

        for chain in self.host_zones:
            if self._evaluate_chain_match(
                chain=chain,
                name=name,
                id=id,
                ticker=ticker,
                denom=denom,
                denom_on_stride=denom_on_stride,
            ):
                return chain

        raise KeyError("No host chain found for the given parameter")


def _load_raw_config() -> dict[str, Any]:
    """
    Loads the raw config yaml into a dictionary
    If STRIDEUTILS_CONFIG_PATH is set, it uses that for the config path, otherwise, it
    looks for a config/config.yaml
    """
    strideutils_config_path = os.environ.get('STRIDEUTILS_CONFIG_PATH', 'config/config.yaml')
    if not os.path.exists(strideutils_config_path):
        raise ValueError(
            'Shell var STRIDEUTILS_CONFIG_PATH is missing or the file does not exist in the default location.'
            'The default file and location is config/config.yaml in the current working directory'
        )
    with open(strideutils_config_path, 'r') as config_file:
        raw_config = yaml.load(config_file, Loader)
    return raw_config


def _load_raw_secrets() -> dict[str, Optional[str]]:
    """
    Loads the secret variables into a dictionary
    If this is running locally in dev mode, secrets are grabbed from the path defined by STRIDEUTILS_ENV_PATH
    Otherwise, their loaded as environment variables
    """
    strideutils_env_path = os.environ.get('STRIDEUTILS_ENV_PATH', '.env.local')
    if os.path.exists(strideutils_env_path):
        load_dotenv(strideutils_env_path)
    return {secret.name: os.environ.get(secret.name) for secret in fields(Config) if os.environ.get(secret.name)}


def _parse_raw_configs(raw_config: dict[str, Any], raw_secrets: dict[str, Optional[str]]) -> Config:
    """
    Builds the relevant config data classes from the raw jsons

    When parsing into the dataclasses, only consider fields that are defined in the dataclass
    so that the package maintains backwards compatibility when new fields are added
    """
    host_chain_fields = [field.name for field in fields(cast(Any, HostChainConfig))]
    app_chain_fields = [field.name for field in fields(cast(Any, ChainConfig))]
    redis_config_fields = [field.name for field in fields(cast(Any, RedisConfig))]

    # Parse Host Chain configs into new dict (instead of dict from raw_config)
    host_chain_config = {}
    for name, info in raw_config["host_zones"].items():
        filtered_info = {key: value for key, value in info.items() if key in host_chain_fields}
        host_chain_config[name] = HostChainConfig(**filtered_info)
    del raw_config["host_zones"]

    # Parse App Chain configs into new dict (instead of dict from raw_config)
    app_chain_config = {}
    for name, info in raw_config["app_chains"].items():
        filtered_info = {key: value for key, value in info.items() if key in app_chain_fields}
        app_chain_config[name] = ChainConfig(**filtered_info)
    del raw_config["app_chains"]

    # Parse Stride chain config
    stride_chain_config = StrideChainConfig(**raw_config["stride"])

    # Parse Redis configs
    redis_configs = {}
    for db_name, db_info in raw_config.get("redis", {}).items():
        filtered_info = {key: value for key, value in db_info.items() if key in redis_config_fields}
        redis_configs[db_name] = RedisConfig(**filtered_info)

    chain_configs = {
        "stride": stride_chain_config,
        "_host_zones": host_chain_config,
        "_app_chains": app_chain_config,
        "redis": redis_configs,
    }

    # Load non-nested configs, then overwrite with the chain configs
    config_dict = raw_secrets
    config_dict.update(raw_config)
    config_dict.update(cast(Dict[str, Any], chain_configs))
    return Config(**config_dict)  # type: ignore


def _init_config() -> Config:
    """
    Initializes the main config files
    """
    raw_config = _load_raw_config()
    raw_secrets = _load_raw_secrets()
    return _parse_raw_configs(raw_config, raw_secrets)


config: Config = _init_config()
