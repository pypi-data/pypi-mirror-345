import numpy as np
from PIL import Image
from typing import Tuple, List, Optional
import cv2

class Layer:
    def __init__(self, width: int, height: int, name: str):
        self.width = width
        self.height = height
        self.name = name
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        self.visible = True
        self.opacity = 1.0

    def fill_area(self, x1: int, y1: int, x2: int, y2: int, color: tuple):
        """Fill rectangular area with color"""
        self.canvas[y1:y2, x1:x2] = color

    def clear(self):
        """Clear the layer"""
        self.canvas.fill(0)

    def paste(self, image: np.ndarray, position: tuple):
        """Paste an image onto the layer at specified position"""
        x, y = position
        h, w = image.shape[:2]
        
        # Make sure we don't go out of bounds
        x_end = min(x + w, self.width)
        y_end = min(y + h, self.height)
        w = x_end - x
        h = y_end - y
        
        # Only copy the part that fits
        self.canvas[y:y_end, x:x_end] = image[:h, :w]

class PixelGenerator:
    def __init__(self, width: int, height: int):
        """Initialize a new pixel art canvas"""
        self.width = width
        self.height = height
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        self.layers = []
        self.history = []
        self.redo_stack = []
        self.active_layer = None
        self.section : Optional[Selection] = None
        self.color_pallete : []
        self.show_grid = False
        self.grid_color = (200, 200, 200)
        self.section : Optional[Selection] = None
        self.color_pallete : []
        self._save_initial_state()

    def _save_initial_state(self):
        """Save initial state to history"""
        self.history = [self.canvas.copy()]
        self.redo_stack = []

    def create_selection(self, x1 : int, y1 : int, x2 : int, y2 : int): 
        """Create a rectangular selection"""
        self.selection = Selection(x1, y1, x2, y2)

    def add_layer(self, name: str):
        """Add a new layer and make it active"""
        layer = Layer(self.width, self.height, name)
        self.layers.append(layer)
        self.active_layer = layer
        return layer

    def merge_layers(self, layer_names=None):
        """Merge specified layers or all layers if none specified"""
        result = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        layers_to_merge = self.layers
        if layer_names:
            layers_to_merge = [layer for layer in self.layers if layer.name in layer_names]

        for layer in layers_to_merge:
            if layer.visible:
                alpha = layer.opacity
                # Convert to float for calculation, then back to uint8
                temp = result.astype(float) * (1 - alpha) + layer.canvas.astype(float) * alpha
                result = np.clip(temp, 0, 255).astype(np.uint8)

        return result

    def get_merged_frame(self):
        """Get current frame with all visible layers merged"""
        return self.merge_layers()

    def toggle_grid(self):
        """Toggle grid visibility"""
        self.show_grid = not self.show_grid
        
    def get_canvas_with_grid(self):
        """Get the canvas with grid overlay if grid is enabled"""
        canvas_with_grid = self.canvas.copy()
        if self.show_grid:
            for x in range(0, self.width, 1):  # Draw vertical grid lines
                canvas_with_grid[:, x] = self.grid_color
            for y in range(0, self.height, 1):  # Draw horizontal grid lines
                canvas_with_grid[y, :] = self.grid_color
        return canvas_with_grid

    def save_state(self):
        """Save current state to history"""
        self.redo_stack = []  # Clear redo stack
        self.history.append(self.canvas.copy())

    def undo(self):
        """Restore previous state"""
        if len(self.history) > 1:
            # Move current state to redo stack
            current_state = self.history.pop()
            self.redo_stack.append(current_state)
            # Restore previous state
            self.canvas = self.history[-1].copy()
            return True
        return False

    def redo(self):
        """Redo previously undone action"""
        if self.redo_stack:
            # Get next state from redo stack
            next_state = self.redo_stack.pop()
            # Add it to history
            self.history.append(next_state)
            # Update canvas
            self.canvas = next_state.copy()
            return True
        return False

    def set_pixel(self, x: int, y: int, color: tuple):
        """Set color of a single pixel"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.canvas[y, x] = color
            self.save_state()

    def fill_area(self, x1: int, y1: int, x2: int, y2: int, color: tuple):
        """Fill rectangular area with color"""
        x1 = max(0, min(x1, self.width))
        y1 = max(0, min(y1, self.height))
        x2 = max(0, min(x2, self.width))
        y2 = max(0, min(y2, self.height))
        
        self.canvas[y1:y2, x1:x2] = color
        self.save_state()

    def clear(self):
        """Clear the entire canvas"""
        self.canvas.fill(0)
        self.save_state()

    def paste(self, image: np.ndarray, position: tuple):
        """Paste an image onto the canvas at specified position"""
        x, y = position
        h, w = image.shape[:2]
        
        # Make sure we don't go out of bounds
        x_end = min(x + w, self.width)
        y_end = min(y + h, self.height)
        w = x_end - x
        h = y_end - y
        
        # Only copy the part that fits
        self.canvas[y:y_end, x:x_end] = image[:h, :w]
        self.save_state()

    def save_image(self, filename: str, format: str = "PNG", frames=None):
        """Save the pixel art as image"""
        if frames:
            # Save animated GIF
            frames_pil = [Image.fromarray(frame) for frame in frames]
            frames_pil[0].save(
                filename,
                format="GIF",
                save_all=True,
                append_images=frames_pil[1:],
                duration=200,
                loop=0
            )
        else:
            # Save static image
            merged = self.get_merged_frame()
            img = Image.fromarray(merged)
            img.save(filename, format=format.upper())

    def get_canvas(self):
        """Get current canvas state"""
        return self.canvas.copy()

    def rotate_canvas(self, angle : float) -> None:
        """Rotate entire canvas by angle degrees"""

        center = (self.width // 2, self.height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        self.canvas = cv2.warpAffine(self.canvas, rotation_matrix, (self.width, self.height))
        self.save_state()

    def scale_canvas(self, scale_factor : float) -> None:
        """Scale canvas by factor"""
        new_width = int(self.width  * scale_factor)
        new_height = int(self.height * scale_factor)
        self.canvas = cv2.resize(self.canvas, (new_width, new_height))
        self.width, self.height = new_width, new_height
        self.save_state()

class Selection : 
    def __init__(self, x1 : int, y1 : int, x2 : int, y2 : int):
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        self.content = None

    @property
    def width(self):
        return self.x2 - self.x1

    @property
    def height(self):
        return self.y2 - self.y1
    











