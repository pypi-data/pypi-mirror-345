# cubeforge/writers.py
import struct
import logging
import abc # Abstract Base Classes

logger = logging.getLogger(__name__)


class MeshWriterBase(abc.ABC):
    """Abstract base class for mesh file writers."""

    @abc.abstractmethod
    def write(self, triangles, filename, **kwargs):
        """
        Writes the mesh data to a file.

        Args:
            triangles (list): A list of tuples, where each tuple represents a
                              triangle: (normal, vertex1, vertex2, vertex3).
                              Vertices and normals should be tuples/lists of 3 floats.
            filename (str): The path to the output file.
            **kwargs: Additional format-specific arguments.
        """
        pass


class StlAsciiWriter(MeshWriterBase):
    """Writes mesh data to an ASCII STL file."""

    def write(self, triangles, filename, **kwargs):
        """
        Writes triangles to an ASCII STL file.

        Args:
            triangles (list): List of (normal, v1, v2, v3) tuples.
            filename (str): Output filename.
            **kwargs: Expects 'solid_name' (str, optional).
        """
        solid_name = kwargs.get("solid_name", "cubeforge_model")
        # Use the logger instance obtained at the module level
        logger.info(f"Writing ASCII STL file: {filename} with {len(triangles)} triangles.")

        try:
            with open(filename, 'w') as f:
                f.write(f"solid {solid_name}\n")
                for normal, v1, v2, v3 in triangles:
                    self._write_triangle(f, normal, v1, v2, v3)
                f.write(f"endsolid {solid_name}\n")
            logger.info(f"Successfully wrote ASCII STL file: {filename}")
        except IOError as e:
            logger.error(f"Failed to write ASCII STL file {filename}: {e}")
            raise

    def _write_triangle(self, f, normal, v1, v2, v3):
        """Writes a single triangle in ASCII STL format."""
        f.write(f"  facet normal {normal[0]:.6f} {normal[1]:.6f} {normal[2]:.6f}\n")
        f.write("    outer loop\n")
        f.write(f"      vertex {v1[0]:.6f} {v1[1]:.6f} {v1[2]:.6f}\n")
        f.write(f"      vertex {v2[0]:.6f} {v2[1]:.6f} {v2[2]:.6f}\n")
        f.write(f"      vertex {v3[0]:.6f} {v3[1]:.6f} {v3[2]:.6f}\n")
        f.write("    endloop\n")
        f.write("  endfacet\n")


class StlBinaryWriter(MeshWriterBase):
    """Writes mesh data to a Binary STL file."""

    def write(self, triangles, filename, **kwargs):
        """
        Writes triangles to a Binary STL file.

        Args:
            triangles (list): List of (normal, v1, v2, v3) tuples.
            filename (str): Output filename.
            **kwargs: Expects 'solid_name' (str, optional).
        """
        solid_name = kwargs.get("solid_name", "cubeforge_model")
        logger.info(f"Writing Binary STL file: {filename} with {len(triangles)} triangles.")

        try:
            with open(filename, 'wb') as f:
                # Write header (80 bytes)
                header_name = solid_name[:80].encode('utf-8')
                header = header_name + b'\x00' * (80 - len(header_name))
                f.write(header)

                # Write number of triangles (4-byte unsigned integer, little-endian)
                num_triangles = len(triangles)
                f.write(struct.pack('<I', num_triangles)) # I = unsigned int

                # Write each triangle (50 bytes each)
                for normal, v1, v2, v3 in triangles:
                    self._write_triangle(f, normal, v1, v2, v3)

            logger.info(f"Successfully wrote Binary STL file: {filename}")
        except IOError as e:
            logger.error(f"Failed to write Binary STL file {filename}: {e}")
            raise
        except struct.error as e:
            logger.error(f"Failed to pack data for Binary STL file {filename}: {e}")
            raise

    def _write_triangle(self, f, normal, v1, v2, v3):
        """Writes a single triangle in Binary STL format."""
        # Pack data as little-endian floats (f) and an unsigned short (H)
        data = struct.pack('<3f 3f 3f 3f H',
                           normal[0], normal[1], normal[2],
                           v1[0], v1[1], v1[2],
                           v2[0], v2[1], v2[2],
                           v3[0], v3[1], v3[2],
                           0) # Attribute byte count = 0
        f.write(data)


# --- Factory Function ---
_writer_map = {
    'stl': StlBinaryWriter,
    'stl_binary': StlBinaryWriter,
    'stl_ascii': StlAsciiWriter,
}

def get_writer(format_id):
    """
    Gets an instance of the appropriate writer class based on the format ID.

    Args:
        format_id (str): The identifier for the desired format. Case-insensitive.

    Returns:
        MeshWriterBase: An instance of the corresponding writer class.

    Raises:
        ValueError: If the format_id is not recognized.
    """
    format_id = format_id.lower()
    writer_class = _writer_map.get(format_id)
    if writer_class:
        return writer_class()
    else:
        supported_formats = ", ".join(_writer_map.keys())
        raise ValueError(f"Unsupported format: '{format_id}'. Supported formats are: {supported_formats}")
