from __future__ import annotations

import csv
import typing as t
from abc import ABCMeta, abstractmethod

import pyarrow as pa
import pyarrow.parquet as pq
import simplejson as json
import xlsxwriter.workbook as xlsx_workbook
import xlsxwriter.worksheet as xlsx_worksheet

if t.TYPE_CHECKING:
    import target_universal_file.sinks as tuf_s


class WriterRegistry(ABCMeta):

    _registry: t.ClassVar[dict[str, type[BaseWriter]]] = {}

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        dct: dict[str, t.Any],
    ) -> type[BaseWriter]:
        new_cls = super().__new__(cls, name, bases, dct)
        if new_cls.__name__ == "BaseWriter":
            return new_cls
        if new_cls.file_type not in cls._registry:
            cls._registry[new_cls.file_type] = new_cls
        return new_cls

    @classmethod
    def file_types(cls) -> list[str]:
        return list(cls._registry.keys())

    @classmethod
    def get(cls, file_type: str) -> type[BaseWriter]:
        if file_type not in cls._registry:
            error_msg = f"Writer for file type {file_type} not found."
            raise ValueError(error_msg)
        return cls._registry[file_type]


class BaseWriter(metaclass=WriterRegistry):

    open_mode = "wt"
    file_type: str

    def __init__(self, stream: tuf_s.UniversalFileSink) -> None:
        self.config = stream.config
        self.schema = stream.schema
        self.logger = stream.logger

    def write_records(
        self,
        file: t.TextIO,
        records: t.Iterable[dict],
    ) -> None:
        try:
            self.write_begin(file)
            for record in records:
                self.write_record(file, record)
            self.write_end(file)
        finally:
            self.cleanup(file)

    @abstractmethod
    def write_record(self, file: t.TextIO, record: dict) -> None:
        error_msg = "write_record must be implemented by a subclass."
        raise NotImplementedError(error_msg)

    def write_begin(self, file: t.TextIO) -> None:
        pass

    def write_end(self, file: t.TextIO) -> None:
        pass

    def cleanup(self, file: t.TextIO) -> None:
        pass

    @property
    def properties(self) -> dict:
        return self.schema.get("properties", {})

    @property
    def fieldnames(self) -> list[str]:
        return list(self.properties.keys())


class CSVWriter(BaseWriter):

    file_type = "csv"

    def __init__(self, stream: tuf_s.UniversalFileSink) -> None:
        super().__init__(stream)
        self.csv_dict_writer: csv.DictWriter

    def write_begin(self, file: t.TextIO) -> None:
        self.csv_dict_writer = csv.DictWriter(f=file, fieldnames=self.fieldnames)
        self.csv_dict_writer.writeheader()

    def write_record(self, file: t.TextIO, record: dict) -> None:  # noqa: ARG002
        self.csv_dict_writer.writerow(record)


class JSONLWriter(BaseWriter):

    file_type = "jsonl"

    def write_record(self, file: t.TextIO, record: dict) -> None:
        json.dump(record, file)
        file.write("\n")


class ParquetWriter(BaseWriter):

    open_mode = "wb"
    file_type = "parquet"

    def __init__(self, stream: tuf_s.UniversalFileSink) -> None:
        super().__init__(stream)
        self.records = []

    def write_record(self, file: t.TextIO, record: dict) -> None:  # noqa: ARG002
        self.records.append(record)

    def write_end(self, file: t.TextIO) -> None:
        table = pa.Table.from_pylist(self.records, schema=self._parquet_schema)
        pq.write_table(table, file)

    def _parquet_type(self, property_dict: dict) -> pa.DataType:
        simple_types = {
            "integer": pa.int64(),
            "number": pa.float64(),
            "string": pa.string(),
            "boolean": pa.bool_(),
        }
        jsonschema_type = property_dict.get("type")
        if jsonschema_type in simple_types:
            return simple_types[jsonschema_type]
        if jsonschema_type == "array":
            items = property_dict.get("items")
            if items is None or len(items) != 1:
                error_msg = "arrays must contain values of exactly one type."
                raise ValueError(error_msg)
            return pa.list_(self._parquet_type(items))
        if jsonschema_type == "object":
            error_msg = "objects for parquet haven't been implemented yet."
            raise NotImplementedError(error_msg)
        if jsonschema_type is None:
            error_msg = f"jsonschema type not found for property: {property_dict}"
            raise ValueError(error_msg)
        error_msg = (
            f"jsonschema type of {jsonschema_type} not recognized for property: "
            f"{property_dict}"
        )
        raise ValueError(error_msg)

    @property
    def _parquet_schema(self) -> pa.Schema:
        fields = []
        for field_name, property_dict in self.properties.items():
            field_type = self._parquet_type(property_dict=property_dict)
            field = pa.field(field_name, field_type)
            fields.append(field)
        return pa.schema(fields)


class XLSXWriter(BaseWriter):

    open_mode = "wb"
    file_type = "xlsx"

    def __init__(self, stream: tuf_s.UniversalFileSink) -> None:
        super().__init__(stream)
        self.workbook: xlsx_workbook.Workbook
        self.worksheet: xlsx_worksheet.Worksheet
        self.row_idx = 0

    def write_begin(self, file: t.TextIO) -> None:
        self.workbook = xlsx_workbook.Workbook(file)
        self.worksheet = self.workbook.add_worksheet()
        for col_idx, field_name in enumerate(self.fieldnames):
            self.worksheet.write(0, col_idx, field_name)

    def write_record(self, file: t.TextIO, record: dict) -> None:  # noqa: ARG002
        for col_idx, field_name in enumerate(self.fieldnames):
            data = record[field_name]
            if isinstance(data, (list, dict)):
                data = str(data)
            self.worksheet.write(self.row_idx, col_idx, data)
        self.row_idx += 1

    def cleanup(self, file: t.TextIO) -> None:
        if self.workbook:
            self.workbook.close()
        super().cleanup(file)
