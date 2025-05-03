'''
mglyph

The Malleable Glyph library.
'''

__author__ = 'Vojtech Bartl, Adam Herout'
__credits__ = 'FIT BUT'

from .canvas import Canvas, CanvasParameters
from .mglyph import export, render, interact, lerp, orbit, show, show_video, render_video, cubic_bezier_for_x, ease, clamped_linear
from .colormap import ColorMap
from .transform import Transformation


__all__ = ['Canvas', 'ColorMap', 'CanvasParameters', 'Transformation', 
           'export', 'render', 'interact', 'lerp', 'orbit', 'show', 'show_video', 'render_video',
           'cubic_bezier_for_x', 'ease', 'clamped_linear']