# Ghahreman

A PyVista-based 3D trophy visualization tool.

## Description

This package provides functionality to create and display a golden trophy with customizable parameters. The trophy consists of two cones connected at their vertices, with the upper cone being larger than the lower one. The trophy includes decorative elements such as disks, a base, spheres, and handles, all rendered in a golden color.

A package for the champion (ghahreman) from the master (ostad).

## Installation

You can install the package using pip:

```bash
pip install ghahreman
```

Or using uv:

```bash
uv pip install ghahreman
```

## Usage

```python
from ghahreman import Hero

# Create a trophy with default parameters
hero = Hero()

# Display the trophy
hero.display()

# Create a trophy with custom parameters
custom_hero = Hero(
    height1=2.0,          # Height of the upper cone
    radius1=1.0,          # Radius of the upper cone
    resolution=60,        # Resolution of the trophy elements
)

# Display the custom trophy with a white background
custom_hero.display(background_color="white", window_size=(1000, 800))
```

## Parameters

The `Hero` class accepts the following parameters:

- `height1`: Height of the upper cone
- `radius1`: Base radius of the upper cone
- `height2`: Height of the lower cone (if None, set to one-third of the upper cone's height)
- `radius2`: Base radius of the lower cone (if None, set to 80% of the upper cone's radius)
- `resolution`: Resolution (number of segments) for the cones and other elements
- `disk_radius`: Radius of the horizontal disk at the connection point of the two cones
- `disk_thickness`: Thickness of the horizontal disk at the connection point
- `bottom_disk_radius`: Radius of the horizontal disk below the lower cone
- `bottom_disk_thickness`: Thickness of the horizontal disk below the lower cone
- `cube_size`: Size of the cube below the bottom disk
- `cube_height`: Height of the cube below the bottom disk
- `sphere_radius`: Radius of the small sphere tangent to the upper cone's base
- `handle_thickness`: Thickness of the trophy handles

## Command Line Usage

After installation, you can also run the package from the command line:

```bash
ghahreman
```

This will display a trophy with default parameters.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Requirements

- Python 3.6 or higher
- PyVista 0.34.0 or higher
- NumPy 1.20.0 or higher

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/Elmino-19/ghahreman.git
cd ghahreman

# Install development dependencies
uv pip install -e ".[dev]"
```
