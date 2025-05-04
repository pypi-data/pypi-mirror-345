import pygame
from .element import Element
from typing import Tuple

class Container(Element):
    """
    Primo element, contains layouts and manages the screen
    """
    def __init__(self, width: int, height: int,
                 background_color: Tuple[int, int, int] = (0, 0, 0)):
        """
        Initialize a new Container.
        
        Args:
            width: Container width
            height: Container height
            background_color: (R,G,B) background color
        """
        super().__init__(0,0, width, height)
        self.background_color = background_color
        # List containning all layouts inside a container.
        self.layouts = []

    def add_layout(self, layout: 'Layout') -> 'Layout':
        """
        Add a layout to the container.
        """
        self.layouts.append(layout)
        layout.parent = self
        layout.on_parent_resize(self.width, self.height)
        return layout

    def render(self, surface: pygame.Surface) -> None:
        """
        Render the container and its layouts.
        """         
        # Fill background
        surface.fill(self.background_color)
        
        # Render layouts
        for layout in self.layouts:
            layout.render(surface)
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        # Pass events to layout
        for layout in self.layouts:
            if layout.handle_event(event):
                return True
        return False

    def update(self, dt: float) -> None:
        """
        Update container and layouts.
        """
        for layout in self.layouts:
            layout.update(dt)

    def resize(self, width: int, height: int) -> None:
        """
        Resize the container and notify all layouts.
        """
        self.width = width
        self.height = height
        
        for layout in self.layouts:
            layout.on_parent_resize(width, height)

