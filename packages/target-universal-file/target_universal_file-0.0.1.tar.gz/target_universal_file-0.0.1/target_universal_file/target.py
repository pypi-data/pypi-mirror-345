"""UniversalFile target class."""

from __future__ import annotations

from singer_sdk import typing as th
from singer_sdk.target_base import Target

import target_universal_file.filesystem as tuf_fs
import target_universal_file.sinks as tuf_s
import target_universal_file.writer as tuf_w


class TargetUniversalFile(Target):
    """Target for UniversalFile."""

    name = "target-universal-file"
    default_sink_class = tuf_s.UniversalFileSink

    config_jsonschema = th.PropertiesList(
        th.Property(
            "protocol",
            th.StringType,
            required=True,
            allowed_values=tuf_fs.FileSystemManagerRegistry.protocols(),
            description="The protocol to connect to the file system. See: [Protocols](#protocols).",
        ),
        th.Property(
            "file_type",
            th.StringType,
            required=True,
            allowed_values=tuf_w.WriterRegistry.file_types(),
            description="The file type to use when writing data. See: [File Types](#file-types).",
        ),
        th.Property(
            "path",
            th.StringType,
            required=True,
            description="The path on the file system where data will be written.",
        ),
        th.Property(
            "file_name_format",
            th.StringType,
            required=True,
            default="{stream_name}.{file_type}",
            description="The format for how to store data. `{stream_name}` will be replaced with the name of the stream and `{file_type}` will be replaced with the file type.",
        ),
        th.Property(
            "protocol_options",
            th.ObjectType(
                additional_properties=True,
            ),
            required=False,
            description="Extended options for the protocol specified in the `protocol` config. Provide this value as an object with key-value pairs as described by the protocol.See: [Protocols](#protocols).",
        ),
        th.Property(
            "file_type_options",
            th.ObjectType(
                additional_properties=True,
            ),
            required=False,
            description="Extended options for the file type specified in the `file_type` config. Provide this value as an object with key-value pairs as described by the file type. See: [File Types](#file-types).",
        ),
    ).to_dict()


if __name__ == "__main__":
    TargetUniversalFile.cli()
