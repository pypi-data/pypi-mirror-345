from __future__ import annotations

import typing as t
from abc import ABCMeta, abstractmethod
from functools import cached_property

import fsspec

if t.TYPE_CHECKING:
    from target_universal_file.sinks import UniversalFileSink


class FileSystemManagerRegistry(ABCMeta):

    _registry: t.ClassVar[dict[str, type[BaseFileSystemManager]]] = {}

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        dct: dict[str, t.Any],
    ) -> type[BaseFileSystemManager]:
        new_cls = super().__new__(cls, name, bases, dct)
        if new_cls.__name__ == "BaseFileSystemManager":
            return new_cls
        if new_cls.protocol not in cls._registry:
            cls._registry[new_cls.protocol] = new_cls
        return new_cls

    @classmethod
    def protocols(cls) -> list[str]:
        return list(cls._registry.keys())

    @classmethod
    def get(cls, protocol: str) -> type[BaseFileSystemManager]:
        if protocol not in cls._registry:
            error_msg = f"FileSystemManager for protocol {protocol} not found."
            raise ValueError(error_msg)
        return cls._registry[protocol]


class BaseFileSystemManager(metaclass=FileSystemManagerRegistry):

    protocol: str
    required_protocol_options: tuple[str] = ()

    def __init__(self, stream: UniversalFileSink) -> None:
        self.config = stream.config
        self.logger = stream.logger
        self.protocol_options = stream.config.get("protocol_options", {})
        self.validate_protocol_options()

    def validate_protocol_options(self) -> None:
        for option in self.required_protocol_options:
            if option not in self.protocol_options:
                error_msg = (
                    f"Protocol option '{option}' is required for protocol "
                    f"'{self.protocol}'."
                )
                raise ValueError(error_msg)

    @property
    @abstractmethod
    def storage_options(self) -> dict[str, t.Any]:
        pass

    @cached_property
    def filesystem(self) -> fsspec.AbstractFileSystem:
        return fsspec.filesystem(
            self.protocol,
            **self.storage_options,
        )


class LocalFileSystemManager(BaseFileSystemManager):

    protocol = "local"

    @property
    def storage_options(self) -> dict[str, t.Any]:
        return {"auto_mkdir": True}


class GCSFileSystemManager(BaseFileSystemManager):

    protocol = "gcs"
    required_protocol_options = ("token",)

    @property
    def storage_options(self) -> dict[str, t.Any]:
        return {
            "token": self.protocol_options["token"],
            "auto_mkdir": True,
        }


class S3FileSystemManager(BaseFileSystemManager):

    protocol = "s3"
    required_protocol_options = ("key", "secret")

    @property
    def storage_options(self) -> dict[str, t.Any]:
        return {
            "key": self.protocol_options["key"],
            "secret": self.protocol_options["secret"],
        }
