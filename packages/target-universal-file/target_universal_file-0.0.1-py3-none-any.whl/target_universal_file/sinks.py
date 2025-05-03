"""UniversalFile target sink class, which handles writing streams."""

from __future__ import annotations

import sys
from functools import cached_property
from pathlib import Path

from singer_sdk.sinks import BatchSink

import target_universal_file.filesystem as tuf_fs
import target_universal_file.writer as tuf_w


class UniversalFileSink(BatchSink):

    max_size = sys.maxsize  # All records in one batch.

    @cached_property
    def filesystem_manager(self) -> tuf_fs.BaseFileSystemManager:
        protocol = self.config["protocol"]
        return tuf_fs.FileSystemManagerRegistry.get(protocol)(stream=self)

    @cached_property
    def writer(self) -> tuf_w.BaseWriter:
        file_type = self.config["file_type"]
        return tuf_w.WriterRegistry.get(file_type)(stream=self)

    @property
    def file_name(self) -> str:
        return self.config["file_name_format"].format(
            stream_name=self.stream_name,
            file_type=self.config["file_type"],
        )

    @property
    def full_path(self) -> Path:
        return Path(self.config["path"], self.file_name)

    def process_batch(self, context: dict) -> None:
        """Write out any prepped records and return once fully written.

        Args:
            context: Stream partition or context dictionary.
        """
        filesystem = self.filesystem_manager.filesystem

        with (
            filesystem.transaction,
            filesystem.open(self.full_path, self.writer.open_mode) as file,
        ):
            self.writer.write_records(file, context["records"])
