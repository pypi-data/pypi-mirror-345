# omfpandas

[![PyPI](https://img.shields.io/pypi/v/omfpandas.svg?logo=python&logoColor=white)](https://pypi.org/project/omfpandas/)
[![Run Tests](https://github.com/Elphick/omfpandas/actions/workflows/poetry_build_and_test.yml/badge.svg?branch=main)](https://github.com/Elphick/omfpandas/actions/workflows/poetry_build_and_test.yml)
[![Publish Docs](https://github.com/Elphick/omfpandas/actions/workflows/poetry_sphinx_docs_to_gh_pages.yml/badge.svg?branch=main)](https://github.com/Elphick/omfpandas/actions/workflows/poetry_sphinx_docs_to_gh_pages.yml)

A pandas (and parquet) interface for the [Open Mining Format package (omf)](https://omf.readthedocs.io/en/latest/).

When working with OMF files, it is often useful to convert the data to a pandas DataFrame.
This package provides a simple interface to do so.

The parquet format is a nice, compact, efficient format to persist pandas DataFrames.
This package also provides a simple interface to convert an omf element to a parquet file.
When datasets do not fit into memory, parquet files can be read in chunks or by column.

> **Note:**
> This package *only* supports omf 2.0, which is currently only a pre-release.

## Installation

```bash
pip install omfpandas
```

If you intend to use the parquet functionality, you will need to install the optional dependencies.

```bash
pip install omfpandas[io]
```

## Roadmap

- [x] 0.2.0 - Add support for reading a VolumeElement (Block Model) from an OMF file as a pandas DataFrame. 
  Export a VolumeElement as a parquet file.
- [x] 0.3.0 - Add support for writing a DataFrame to an OMF BlockModel.  Version 2.0 of the OMF spec is supported.
- [x] 0.4.0 - Convert to omf 2.0 support.
- [x] 0.5.0 - Block model profiling, with reports persisted in the omf file.
- [x] 0.6.0 - Optional block model validation using pandera json schemas.
- [x] ...
- [ ] 0.9.0 - Add support for low-memory/out-of-core writing an omf element to parquet
- [ ] ...
