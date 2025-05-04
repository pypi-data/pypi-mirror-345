import unittest
import numpy as np
from pixelgen.core import PixelGenerator, Layer
from pixelgen.tools import create_gradient, create_pattern, create_circle, create_noise
import os

class TestPixelGenerator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.width = 32
        self.height = 32
        self.pixel_gen = PixelGenerator(self.width, self.height)

    def test_toggle_grid(self):
        """Test toggling grid visibility"""
        self.assertFalse(self.pixel_gen.show_grid)  # Default is False
        self.pixel_gen.toggle_grid()
        self.assertTrue(self.pixel_gen.show_grid)  # Should be True after toggle
        self.pixel_gen.toggle_grid()
        self.assertFalse(self.pixel_gen.show_grid)  # Should be False after another toggle

    def test_get_canvas_with_grid(self):
        """Test canvas with grid overlay"""
        self.pixel_gen.toggle_grid()  # Enable grid
        canvas_with_grid = self.pixel_gen.get_canvas_with_grid()
        grid_color = (200, 200, 200)

        # Check vertical grid lines
        for x in range(0, self.width, 1):
            np.testing.assert_array_equal(canvas_with_grid[:, x, :], np.full((self.height, 3), grid_color))

        # Check horizontal grid lines
        for y in range(0, self.height, 1):
            np.testing.assert_array_equal(canvas_with_grid[y, :, :], np.full((self.width, 3), grid_color))

    def test_initialization(self):
        """Test if PixelGenerator initializes correctly"""
        self.assertEqual(self.pixel_gen.width, self.width)
        self.assertEqual(self.pixel_gen.height, self.height)
        self.assertEqual(self.pixel_gen.canvas.shape, (self.height, self.width, 3))
        self.assertEqual(len(self.pixel_gen.layers), 0)

    def test_set_pixel(self):
        """Test setting individual pixels"""
        color = (255, 0, 0)  # Red
        self.pixel_gen.set_pixel(0, 0, color)
        np.testing.assert_array_equal(self.pixel_gen.canvas[0, 0], color)

    def test_fill_area(self):
        """Test filling rectangular area"""
        color = (0, 255, 0)  # Green
        self.pixel_gen.fill_area(0, 0, 10, 10, color)
        np.testing.assert_array_equal(self.pixel_gen.canvas[0:10, 0:10], 
                                    np.full((10, 10, 3), color))

    def test_layer_management(self):
        """Test layer creation and management"""
        layer = self.pixel_gen.add_layer("test_layer")
        self.assertEqual(len(self.pixel_gen.layers), 1)
        self.assertEqual(layer.name, "test_layer")
        self.assertEqual(layer.width, self.width)
        self.assertEqual(layer.height, self.height)

    def test_undo_redo(self):
        """Test undo and redo functionality"""
        # Make initial change
        self.pixel_gen.set_pixel(0, 0, (255, 0, 0))
        initial_state = self.pixel_gen.canvas.copy()
        
        # Make second change
        self.pixel_gen.set_pixel(1, 1, (0, 255, 0))
        second_state = self.pixel_gen.canvas.copy()
        
        # Test undo
        self.pixel_gen.undo()
        np.testing.assert_array_equal(self.pixel_gen.canvas, initial_state)
        
        # Test redo
        self.pixel_gen.redo()
        np.testing.assert_array_equal(self.pixel_gen.canvas, second_state)

    def test_save_image(self):
        """Test saving image functionality"""
        test_filename = "test_output.png"
        self.pixel_gen.set_pixel(0, 0, (255, 0, 0))
        self.pixel_gen.save_image(test_filename)
        
        # Check if file exists
        self.assertTrue(os.path.exists(test_filename))
        
        # Clean up
        if os.path.exists(test_filename):
            os.remove(test_filename)

class TestTools(unittest.TestCase):
    def test_create_gradient(self):
        """Test gradient creation"""
        color1 = (255, 0, 0)
        color2 = (0, 0, 255)
        steps = 5
        gradient = create_gradient(color1, color2, steps)
        self.assertEqual(gradient.shape, (steps, 1, 3))

    def test_create_pattern(self):
        """Test pattern creation"""
        size = 4
        color1 = (255, 0, 0)
        color2 = (0, 0, 255)
        pattern = create_pattern(size, color1, color2)
        self.assertEqual(pattern.shape, (size, size, 3))

    def test_create_circle(self):
        """Test circle creation"""
        radius = 5
        color = (255, 0, 0)
        circle = create_circle(radius, color)
        self.assertEqual(circle.shape, (radius * 2 + 1, radius * 2 + 1, 3))

    def test_create_noise(self):
        """Test noise pattern creation"""
        width = 10
        height = 10
        density = 0.5
        noise = create_noise(width, height, density)
        self.assertEqual(noise.shape, (height, width, 3))

if __name__ == '__main__':
    unittest.main()