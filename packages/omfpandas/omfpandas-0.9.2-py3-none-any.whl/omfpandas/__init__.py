from omfpandas.reader import OMFPandasReader
from omfpandas.writer import OMFPandasWriter
from importlib import metadata

try:
    __version__ = metadata.version('omfpandas')
except metadata.PackageNotFoundError:
    # Package is not installed
    pass
