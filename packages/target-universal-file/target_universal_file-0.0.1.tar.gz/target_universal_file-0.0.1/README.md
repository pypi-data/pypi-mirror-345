# target-universal-file

*target-universal-file* is a [Singer](https://www.singer.io/#what-it-is) target built with the [Meltano SDK](https://sdk.meltano.com) designed to load data to any file system (local, GCP, AWS, etc.) in any format (.csv, .json, .parquet, .xlsx, etc.).

## Installation

Install from [PyPI](https://pypi.org/project/target-universal-file/):

```bash
pipx install target-universal-file
```

Install from [GitHub](https://github.com/taliawsmiley/target-universal-file):

```bash
pipx install git+https://github.com/taliawsmiley/target-universal-file.git@main
```

Add to your Meltano project from the [Meltano Hub](https://hub.meltano.com/loaders/target-universal-file):

```bash
meltano add loader target-universal-file
```

## Configuration

### Accepted Config Options

| Setting | Required | Default | Description |
|:--------|:--------:|:-------:|:------------|
| protocol | True     | None    | The protocol to connect to the file system. See: [Protocols](#protocols). |
| file_type | True     | None    | The file type to use when writing data. See: [File Types](#file-types). |
| path | True     | None    | The path on the file system where data will be written. |
| file_name_format | True     | {stream_name}.{file_type} | The format for how to store data. `{stream_name}` will be replaced with the name of the stream and `{file_type}` will be replaced with the file type. |
| protocol_options | False    | None    | Extended options for the protocol specified in the `protocol` config. Provide this value as an object with key-value pairs as described by the protocol.See: [Protocols](#protocols). |
| file_type_options | False    | None    | Extended options for the file type specified in the `file_type` config. Provide this value as an object with key-value pairs as described by the file type. See: [File Types](#file-types). |
| add_record_metadata | False    | None    | Whether to add metadata fields to records. |
| load_method | False    | TargetLoadMethods.APPEND_ONLY | The method to use when loading data into the destination. `append-only` will always write all input records whether that records already exists or not. `upsert` will update existing records and insert new records. `overwrite` will delete all existing records and insert all input records. |
| batch_size_rows | False    | None    | Maximum number of rows in each batch. |
| validate_records | False    |       1 | Whether to validate the schema of the incoming streams. |
| stream_maps | False    | None    | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html). |
| stream_map_config | False    | None    | User-defined config values to be used within map expressions. |
| faker_config | False    | None    | Config for the [`Faker`](https://faker.readthedocs.io/en/master/) instance variable `fake` used within map expressions. Only applicable if the plugin specifies `faker` as an additional dependency (through the `singer-sdk` `faker` extra or directly). |
| faker_config.seed | False    | None    | Value to seed the Faker generator for deterministic output: https://faker.readthedocs.io/en/master/#seeding-the-generator |
| faker_config.locale | False    | None    | One or more LCID locale strings to produce localized output for: https://faker.readthedocs.io/en/master/#localization |
| flattening_enabled | False    | None    | 'True' to enable schema flattening and automatically expand nested properties. |
| flattening_max_depth | False    | None    | The max depth to flatten schemas. |


A full list of supported settings and capabilities for *target-universal-file* is available by running:

```bash
target-universal-file --about
```

### Environment Variables

*target-universal-file* will automatically import a `.env` file if `--config=ENV` is provided,.

## Protocols

*target-universal-file* uses [fsspec](https://filesystem-spec.readthedocs.io/en/latest/) to easily connect to a wide variety of external file systems. Determine the file system to connect to by specifying a `protocol` in target configuration.

The supported protocols are:
1. [`local`](#local): For writing data to a local file.
1. [`gcs`](#gcs): For connecting to a bucket on [Google Cloud](https://cloud.google.com/storage?hl=en).
1. [`s3`](#s3): For connecting to a bucket on [Amazon Web Services](https://aws.amazon.com/s3/).

### Local

**Protocol:** `local`<br>
**Description:** For writing data to a local file.<br>
**Protocol Options:** N/A<br>

Local paths support both relative `./folder` and absolute `/folder` reference. 

### GCS

**Protocol:** `gcs`<br>
**Description:** For connecting to a bucket on [Google Cloud](https://cloud.google.com/storage?hl=en).<br>
**Protocol Options:** `token`<br>

The suggested method of authenticating to GCS is to log in with gcloud and copy the provided credentials, such as from `~/.config/gcloud/application_default_credentials.json`.

Steps to authenticate:
1. Install the [gcloud CLI](https://cloud.google.com/sdk/docs/install-sdk).
1. Run `gcloud auth application-default login`.
1. Copy the output file from `~/.config/gcloud/application_default_credentials.json` and provide it as an environment variable to `protocol_options.token`.

Other options are available for authentication as described by the `gcsfs` [documention](https://gcsfs.readthedocs.io/en/latest/#credentials).

### S3

**Protocol:** `local`<br>
**Description:** For connecting to a bucket on [Amazon Web Services](https://aws.amazon.com/s3/).<br>
**Protocol Options:** `key`, `secret`<br>

Connecting to an S3 bucket anonymously is not supported.

## File Types

*target-universal-file* supports a variety of data formats. Determine the data format to use by specifying a `file_type` in target configuration.

The supported file types are:
1. `csv`: For [Comma-Separated Value](https://en.wikipedia.org/wiki/Comma-separated_values) files.
1. `jsonl`: For [JSON Lines](https://jsonlines.org/) files.
1. `parquet`: For [Apache Parquet](https://parquet.apache.org/) files.
1. `xlsx`: For [Microsoft Excel](https://www.microsoft.com/en-us/microsoft-365/excel) files.

## Usage Example

```bash
target-universal-file --version
target-universal-file --help
# Test using the "smoke test" sample tap from Meltano
tap-smoke-test | target-universal-file --config /path/to/target-universal-file-config.json
```