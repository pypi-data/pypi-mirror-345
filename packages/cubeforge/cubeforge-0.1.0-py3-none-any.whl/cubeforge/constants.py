# cubeforge/constants.py
import enum

class CubeAnchor(enum.Enum):
    """
    Defines the anchor point of a cube relative to its coordinates (x, y, z).

    Attributes:
        CORNER_NEG:    (x, y, z) is the corner with the minimum coordinates
                      (closest to negative infinity).
        CENTER:        (x, y, z) is the geometric center of the cube.
        CORNER_POS:    (x, y, z) is the corner with the maximum coordinates
                      (closest to positive infinity).
        BOTTOM_CENTER: (x, y, z) is the center of the bottom face (minimum Y face).
        TOP_CENTER:    (x, y, z) is the center of the top face (maximum Y face).
    """
    CORNER_NEG = "corner_neg"       # Minimum x, y, z corner
    CENTER = "center"               # Geometric center
    CORNER_POS = "corner_pos"       # Maximum x, y, z corner
    BOTTOM_CENTER = "bottom_center" # Center of the -Y face
    TOP_CENTER = "top_center"       # Center of the +Y face
