# CubeForge

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**CubeForge** is a Python library designed to easily generate 3D mesh files (currently STL format) by defining models voxel by voxel. It allows for flexible voxel dimensions and positioning using various anchor points.

## Features

- [x] **Voxel-based Modeling:** Define 3D shapes by adding individual voxels (cubes).
- [x] **Non-Uniform Voxel Dimensions:** Specify custom width, height, and depth for voxels.
- [x] **Flexible Anchoring:** Position voxels using different anchor points ([`cubeforge.CubeAnchor`](cubeforge/constants.py)) like corners or centers.
- [x] **STL Export:** Save the generated mesh to both ASCII and Binary STL file formats.
- [x] **Simple API:** Easy-to-use interface with the core [`cubeforge.VoxelModel`](cubeforge/model.py) class.

## Installation

**Install from PyPI:**
You can install CubeForge directly from [PyPI](https://pypi.org/project/cubeforge/) using `pip`:

```bash
pip install cubeforge
```

**Install from source:**
You can also clone the repository and install the package using pip:

```bash
pip install .
```

## Usage

Here's a basic example of how to create a simple shape and save it as an STL file:

```python
import cubeforge
import os

# Create a model with default 1x1x1 voxel dimensions
model = cubeforge.VoxelModel()

# Add some voxels using the default CORNER_NEG anchor
model.add_voxel(0, 0, 0)
model.add_voxel(1, 0, 0)
model.add_voxel(1, 1, 0)

# --- Or add multiple voxels at once ---
# model.add_voxels([(0, 0, 0), (1, 0, 0), (1, 1, 0)])

# --- Example with non-uniform dimensions and different anchor ---
model_non_uniform = cubeforge.VoxelModel(voxel_dimensions=(2.0, 1.0, 3.0))
# Add a voxel centered at (0, 0, 0)
model_non_uniform.add_voxel(0, 0, 0, anchor=cubeforge.CubeAnchor.CENTER)

# Define output path
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)
output_filename = os.path.join(output_dir, "my_shape.stl")

# Save the mesh as a binary STL file
model.save_mesh(output_filename, format='stl_binary', solid_name="MyCustomShape")

print(f"Saved mesh to {output_filename}")
```

## Examples

The [`examples/create_shapes.py`](examples/create_shapes.py ) script demonstrates various features, including:
*   Creating simple and complex shapes.
*   Using different voxel dimensions.
*   Utilizing various [`CubeAnchor`](cubeforge/constants.py ) options.
*   Saving in both ASCII and Binary STL formats.
*   Generating a surface with random heights.

To run the examples:

```bash
python examples/create_shapes.py
```

The output STL files will be saved in the [`examples`](examples ) directory.

## API Overview

*   **[`cubeforge.VoxelModel`](cubeforge/model.py ):** The main class for creating and managing the voxel model.
    *   [`__init__(self, voxel_dimensions=(1.0, 1.0, 1.0))`](cubeforge/model.py ): Initializes the model, optionally setting default voxel dimensions.
    *   [`add_voxel(self, x, y, z, anchor=CubeAnchor.CORNER_NEG)`](cubeforge/model.py ): Adds a single voxel.
    *   [`add_voxels(self, coordinates, anchor=CubeAnchor.CORNER_NEG)`](cubeforge/model.py ): Adds multiple voxels.
    *   [`remove_voxel(self, x, y, z, anchor=CubeAnchor.CORNER_NEG)`](cubeforge/model.py ): Removes a voxel.
    *   [`clear(self)`](cubeforge/model.py ): Removes all voxels.
    *   [`generate_mesh(self)`](cubeforge/model.py ): Generates the triangle mesh data.
    *   [`save_mesh(self, filename, format='stl_binary', **kwargs)`](cubeforge/model.py ): Generates and saves the mesh to a file.
*   **[`cubeforge.CubeAnchor`](cubeforge/constants.py ):** An [`enum`](/opt/homebrew/Cellar/python@3.13/3.13.2/Frameworks/Python.framework/Versions/3.13/lib/python3.13/enum.py ) defining the reference points for voxel placement ([`CORNER_NEG`](cubeforge/constants.py ), [`CENTER`](cubeforge/constants.py ), [`CORNER_POS`](cubeforge/constants.py ), [`BOTTOM_CENTER`](cubeforge/constants.py ), [`TOP_CENTER`](cubeforge/constants.py )).
*   **[`cubeforge.get_writer(format_id)`](cubeforge/writers.py ):** Factory function to get mesh writer instances (used internally by [`save_mesh`](cubeforge/model.py )). Supports `'stl'`, `'stl_binary'`, `'stl_ascii'`.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests on the [GitHub repository](https://github.com/Teddy-van-Jerry/cubeforge).

## License

This project is licensed under the [MIT License](LICENSE).

This project is developed and maintained by [Teddy van Jerry](https://github.com/Teddy-van-Jerry) ([Wuqiong Zhao](https://wqzhao.org)).
The development is assisted by *Gemini 2.5 Pro*.
