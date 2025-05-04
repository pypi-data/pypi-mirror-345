# PixelGen

PixelGen is a Python library that simplifies pixel art creation, making it faster and more detailed. This library provides various tools to create, manipulate, and generate pixel art.

## 🚀 Features

- Create pixel art canvas with customizable dimensions
- Individual pixel manipulation
- Area filling with colors
- Color gradient generation
- Pattern creation
- Save results in image format

## 📦 Installation

```bash
pip install pixelgen
```

## 🎨 Basic Usage

### Creating Simple Pixel Art

```python
from pixelgen.core import PixelGenerator
from pixelgen.tools import create_gradient, create_pattern

# Initialize a 32x32 canvas
pixel_art = PixelGenerator(32, 32)

# Set individual pixels
pixel_art.set_pixel(0, 0, (255, 0, 0))  # Red
pixel_art.set_pixel(1, 1, (0, 255, 0))  # Green

# Fill area with color
pixel_art.fill_area(10, 10, 20, 20, (0, 0, 255))  # Blue area

# Save result
pixel_art.save_image("pixel_art_result.png")
```

### Creating Gradients

```python
# Create gradient from red to blue with 10 steps
gradient = create_gradient((255, 0, 0), (0, 0, 255), 10)
```

### Creating Patterns

```python
# Create 8x8 checkered pattern
pattern = create_pattern(8, (255, 0, 0), (0, 0, 255))
```

## 📚 API Reference

### PixelGenerator

#### `__init__(width: int, height: int)`
Creates a new pixel art canvas with specified dimensions.

#### `set_pixel(x: int, y: int, color: tuple)`
Sets color for a specific pixel.
- `x, y`: Pixel coordinates
- `color`: RGB tuple (red, green, blue)

#### `fill_area(x1: int, y1: int, x2: int, y2: int, color: tuple)`
Fills a rectangular area with a specific color.
- `x1, y1`: Top-left corner coordinates
- `x2, y2`: Bottom-right corner coordinates
- `color`: RGB tuple (red, green, blue)

#### `save_image(filename: str)`
Saves pixel art as an image file.
- `filename`: Output filename

### Tools

#### `create_gradient(color1: tuple, color2: tuple, steps: int)`
Creates a gradient between two colors.
- `color1`: Starting color (RGB)
- `color2`: Ending color (RGB)
- `steps`: Number of gradient steps

#### `create_pattern(pattern_size: int, color1: tuple, color2: tuple)`
Creates a checkered pattern.
- `pattern_size`: Pattern size
- `color1, color2`: Colors for pattern (RGB)

## 🌟 Advanced Examples

### Creating Complex Patterns

```python
# Create a rainbow gradient
colors = [
    (255, 0, 0),    # Red
    (255, 127, 0),  # Orange
    (255, 255, 0),  # Yellow
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (75, 0, 130),   # Indigo
    (148, 0, 211)   # Violet
]

# Apply gradient to canvas
for i, color in enumerate(colors):
    pixel_art.fill_area(i*4, 0, (i+1)*4, 32, color)
```

## 🔧 Requirements

- Python >= 3.6
- PIL >= 5.2.0
- NumPy

## 🤝 Contributing

Contributions are always welcome! Please feel free to submit a Pull Request or create an Issue for any improvements or suggestions.

### Development Setup

1. Clone the repository
```bash
git clone https://github.com/rifqanzalbina/product-generator.git
```

2. Install development dependencies
```bash
pip install -r requirements.txt
```

3. Run tests
```bash
python -m pytest
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

- Rifqan Zalbina (zalbinarifqan19@gmail.com)

## 🔗 Links

- [GitHub Repository](https://github.com/rifqanzalbina/product-generator)
- [Bug Tracker](https://github.com/rifqanzalbina/product-generator/issues)

## 🗺️ Roadmap

- [ ] Add more pattern generation tools
- [ ] Implement layer system
- [ ] Add undo/redo functionality
- [ ] Add AI-powered pixel art generation
- [ ] Implement real-time preview
- [ ] Add export to multiple formats

## ❓ FAQ

**Q: Can I use this for commercial projects?**
A: Yes, PixelGen is released under the MIT license, which allows commercial use.

**Q: What image formats are supported?**
A: Currently, PixelGen supports saving to common image formats like PNG, JPEG, and BMP.

**Q: Is there a size limit for pixel art?**
A: The size is limited only by your system's memory capacity.