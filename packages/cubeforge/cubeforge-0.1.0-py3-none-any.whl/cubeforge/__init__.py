# cubeforge/__init__.py

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# Import main classes and constants to make them available
# directly under the 'cubeforge' namespace.
from .constants import CubeAnchor
from .model import VoxelModel
# Expose the writer factory function and specific writers if direct use is desired
from .writers import get_writer, StlAsciiWriter, StlBinaryWriter, MeshWriterBase

# Define what gets imported with 'from cubeforge import *'
__all__ = [
    'VoxelModel',
    'CubeAnchor',
    'get_writer',        # Allow getting writers by format string
    'MeshWriterBase',    # Allow extending with custom writers
    'StlAsciiWriter',    # Allow direct instantiation if needed
    'StlBinaryWriter',   # Allow direct instantiation if needed
]

# Define package version
__version__ = "0.1.0" # Incremented version for voxel dimension change

# logger.info(f"CubeForge package version {__version__} loaded.")
