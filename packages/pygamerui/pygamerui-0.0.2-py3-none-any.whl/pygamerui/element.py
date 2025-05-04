import pygame
from typing import Tuple

class Element():
    """
    Base class for all elements of GUI.
    Every GUI class should inhereit it.
    """

    def __init__(self, x: int = 0, y: int = 0,
                 width: int = 0, height: int = 0):
        """
        Initialize a new GUI element.

        Args:
            x: x coordinate
            y: y coordinate
            width: width of an element
            height: height of an elemnt
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.parent = None

    @property
    def rect(self) -> pygame.Rect:
        """
        Get's the element rect.
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def absolute_position(self) -> Tuple[int, int]:
        """
        Get absolute position.
        """
        # Account for parrent possition.
        if self.parent:
            parent_x, parent_y = self.parent.absolute_position
            return parent_x + self.x, parent_y + self.y
        return self.x, self.y

    def render(self, surface: pygame.Surface) -> None:
        """
        Render the element on the given surface.
        """
        pass

    def handle_event(self, surface: pygame.event.Event) -> bool:
        """
        Handle pygame event. Return true if handled.
        """
        return False

    def update(self, dt: float) -> None:
        """
        Update the element state.
        """
        pass

