from typing import Sequence
from typing import Tuple
from numbers import Number
from numbers import Real

from ppb_vector import Vector
from ppb.sprites import Sprite
from ppb.flags import DoNotRender


class Camera:
    """
    A simple Camera.

    Intentionally tightly coupled to the renderer to allow information flow
    back and forth.

    There is a one-to-one relationship between cameras and scenes.
    """
    position = Vector(0, 0)
    size = 0  # Cameras never render, so their logical game unit size is 0

    def __init__(self, renderer, target_game_unit_width: Real,
                 viewport_dimensions: Tuple[int, int]):
        """
        You shouldn't instantiate your own camera in general. If you want to
        override the Camera, see :class:`~ppb.systems.renderer`.

        :param renderer: The renderer associated with the camera.
        :type renderer: ~ppb.systems.renderer.Renderer
        :param target_game_unit_width: The number of game units wide you
           would like to display. The actual width may be less than this
           depending on the ratio to the viewport (as it can only be as wide
           as there are pixels.)
        :type target_game_unit_width: Real
        :param viewport_dimensions: The pixel dimensions of the rendered
           viewport in (width, height) form.
        :type viewport_dimensions: Tuple[int, int]
        """
        self.renderer = renderer
        self.target_game_unit_width = target_game_unit_width
        self.viewport_dimensions = viewport_dimensions
        self.pixel_ratio = None
        self._width = None
        self._height = None
        self._set_dimensions(target_width=target_game_unit_width)

    @property
    def width(self) -> Real:
        """
        The game unit width of the viewport.

        See :mod:`ppb.sprites` for details about game units.

        When setting this property, the resulting width may be slightly
        different from the value provided based on the ratio between the width
        of the window in screen pixels and desired number of game units to
        represent.

        When you set the width, the height will change as well.
        """
        return self._width

    @width.setter
    def width(self, target_width):
        self._set_dimensions(target_width=target_width)

    @property
    def height(self) -> Real:
        """
        The game unit height of the viewport.

        See :mod:`ppb.sprites` for details about game units.

        When setting this property, the resulting height may be slightly
        different from the value provided based on the ratio between the height
        of the window in screen pixels and desired number of game units to
        represent.

        When you set the height, the width will change as well.
        """
        return self._height

    @height.setter
    def height(self, target_height):
        self._set_dimensions(target_height=target_height)

    def point_is_visible(self, point: Vector) -> bool:
        """
        Determine if a given point is in view of the camera.

        :param point: A vector representation of a point in game units.
        :type point: Vector
        :return: Whether the point is in view or not.
        :rtype: bool
        """
        return (
            self.left <= point.x <= self.right
            and self.bottom <= point.y <= self.top
        )

    def translate_point_to_screen(self, point: Vector) -> Vector:
        """
        Convert a vector from game position to screen position.

        :param point: A vector in game units
        :type point: Vector
        :return: A vector in pixels.
        :rtype: Vector
        """
        return Vector(point.x - self.left, self.top - point.y) * self.pixel_ratio

    @property
    def bottom(self):
        return self.position.y - (self.height / 2)

    @property
    def left(self):
        return self.position.x - (self.width / 2)

    @property
    def right(self):
        return self.position.x + (self.width / 2)

    @property
    def top(self):
        return self.position.y + (self.height / 2)

    @property
    def top_left(self):
        return Vector(self.left, self.top)

    @property
    def top_right(self):
        return Vector(self.right, self.top)

    @property
    def bottom_left(self):
        return Vector(self.left, self.bottom)

    @property
    def bottom_right(self):
        return Vector(self.right, self.bottom)

    def _set_dimensions(self, target_width=None, target_height=None):
        # Set new pixel ratio
        viewport_width, viewport_height = self.viewport_dimensions
        if target_width is not None and target_height is not None:
            raise ValueError("Can only set one dimension at a time.")
        elif target_width is not None:
            game_unit_target = target_width
            pixel_value = viewport_width
        elif target_height is not None:
            game_unit_target = target_height
            pixel_value = viewport_height
        else:
            raise ValueError("Must set target_width or target_height")
        self.pixel_ratio = int(pixel_value / game_unit_target)
        self._width = viewport_width / self.pixel_ratio
        self._height = viewport_height / self.pixel_ratio


class OldCamera(Sprite):

    image = DoNotRender

    def __init__(self, viewport: Sequence[int] = (0, 0, 800, 600),
                 pixel_ratio: float = 64):
        """

        viewport: A container of origin x, origin y, width, and
                  height. The origin is the top left point of the viewport
                  measured from the top left point of the window or screen.
                  The width and height are the raw pixel measurements of the
                  viewport.
        pixel_ratio: A number defining the pixel to game unit ratio. Divide
                     the viewport dimensions by the pixel ratio to get the
                     frame in game unit terms.
        """
        super().__init__(size=0)
        # Cameras don't take up game space, thus size 0.
        self.position = Vector(0, 0)
        self.viewport_origin = Vector(viewport[0], viewport[1])
        self._viewport_width = viewport[2]
        self._viewport_height = viewport[3]
        self.viewport_offset = Vector(self.viewport_width / 2,
                                      self.viewport_height / 2)
        self.pixel_ratio = pixel_ratio

    @property
    def frame_top(self) -> Number:
        return self.position.y + self.half_height

    @property
    def frame_bottom(self) -> Number:
        return self.position.y - self.half_height

    @property
    def frame_left(self) -> Number:
        return self.position.x - self.half_width

    @property
    def frame_right(self) -> Number:
        return self.position.x + self.half_width

    @property
    def frame_height(self) -> float:
        return self.viewport_height / self.pixel_ratio

    @property
    def frame_width(self) -> float:
        return self.viewport_width / self.pixel_ratio

    @property
    def half_height(self) -> float:
        return self.frame_height / 2

    @property
    def half_width(self) -> float:
        return self.frame_width / 2

    @property
    def viewport_width(self) -> int:
        return self._viewport_width

    @viewport_width.setter
    def viewport_width(self, value: int):
        self._viewport_width = value
        self.viewport_offset = Vector(value / 2, self.viewport_height / 2)

    @property
    def viewport_height(self) -> int:
        return self._viewport_height

    @viewport_height.setter
    def viewport_height(self, value: int):
        self._viewport_height = value
        self.viewport_offset = Vector(self.viewport_width / 2, value / 2)

    def point_in_viewport(self, point: Vector) -> bool:
        px, py = point
        vpx, vpy = self.viewport_origin
        vpw = self.viewport_width
        vph = self.viewport_height
        return vpx <= px <= (vpw+vpx) and vpy <= py <= (vph+vpy)

    def in_frame(self, sprite: Sprite) -> bool:
        return (self.frame_left <= sprite.right and
                self.frame_right >= sprite.left and
                self.frame_top >= sprite.bottom and
                self.frame_bottom <= sprite.top
                )

    def translate_to_frame(self, point: Vector) -> Vector:
        """
        Converts a vector from pixel-based window to in-game coordinate space
        """
        # 1. Scale from pixels to game unites
        scaled = point / self.pixel_ratio
        # 2. Reposition relative to frame edges
        return Vector(self.frame_left + scaled.x, self.frame_top - scaled.y)

    def translate_to_viewport(self, point: Vector) -> Vector:
        """
        Converts a vector from in-game to pixel-based window coordinate space
        """
        # 1. Reposition based on frame edges
        # 2. Scale from game units to pixels
        return Vector(point.x - self.frame_left, self.frame_top - point.y) * self.pixel_ratio
