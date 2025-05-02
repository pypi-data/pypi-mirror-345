# Impresso Python Library

[![PyPI version](https://badge.fury.io/py/impresso.svg)](https://badge.fury.io/py/impresso)
![PyPI - License](https://img.shields.io/pypi/l/impresso)


Impresso is a library designed to facilitate interaction with the [Impresso](https://impresso-project.ch/app) dataset. It offers a comprehensive set of classes for API interaction and a variety of tools to streamline data manipulation and analysis.

You can find the full documentation at [https://impresso.github.io/impresso-py/](https://impresso.github.io/impresso-py/).

## Installation

With `pip`:

```bash
pip install impresso
```

## Usage

See sample notebooks in the [examples/notebooks](https://github.com/impresso/impresso-py/tree/main/examples/notebooks) directory or examples available in the [Impresso Datalab](https://impresso-project.ch/datalab/).

## Extending the library

We use [Poetry](https://python-poetry.org/) for dependency management. To install the package in development mode, run the following command in the root directory of the project:

```shell
poetry install
```

This will create and activate a virtual environment with all the dependencies installed.

### Testing

```shell
poetry run pytest
```

### Linting

```shell
poetry run pytest
poetry run flake8 impresso tests
poetry run mypy impresso tests
```

### OpenAPI client generation

The OpenAPI client is generated using the OpenAPI Generator. Pydantic models from the OpenAPI spec are generated too. The following command generates both the client code and the pydantic models:

```shell
poetry run generate-client
```

Whenever the OpenAPI spec of the Impresso Public API changes, the client code and the pydantic models must be regenerated.

### Protobuf

Filters used in some endpoints are serialized as a protobuf message. The protobuf message is defined in the [impresso-jscommons](https://github.com/impresso/impresso-jscommons) project. The python code is generated using the `protoc` compiler (must be [installed](https://google.github.io/proto-lens/installing-protoc.html) separately). The following command generates the python code for the protobuf message:

```shell
poetry run generate-protobuf
```

## About Impresso

### Impresso project

[Impresso - Media Monitoring of the Past](https://impresso-project.ch) is an interdisciplinary research project that aims to develop and consolidate tools for processing and exploring large collections of media archives across modalities, time, languages and national borders. The first project (2017-2021) was funded by the Swiss National Science Foundation under grant No. [CRSII5_173719](http://p3.snf.ch/project-173719) and the second project (2023-2027) by the SNSF under grant No. [CRSII5_213585](https://data.snf.ch/grants/grant/213585) and the Luxembourg National Research Fund under grant No. 17498891.

### Copyright

Copyright (C) 2024 The Impresso team.

### License

This program is provided as open source under the [GNU Affero General Public License](https://github.com/impresso/impresso-pyindexation/blob/master/LICENSE) v3 or later.

---

<p align="center">
  <img src="https://github.com/impresso/impresso.github.io/blob/master/assets/images/3x1--Yellow-Impresso-Black-on-White--transparent.png?raw=true" width="350" alt="Impresso Project Logo"/>
</p>
