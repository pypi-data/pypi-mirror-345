import pygame
from .anchor import Anchor
from .element import Element

class Layout(Element):
    """
    Base layout class.
    """

    def __init__(self, x: int=0, y: int=0,
                width: int= 0, height: int=0, 
                anchor: Anchor = Anchor.TOP_LEFT,
                margin: int=0,
                relative_width: float = None, relative_height: float=None,
                min_width: int = 0, min_height: int = 0,
                max_width: int = None, max_height: int = None):
        """
        Initialize a new Layout.
        
        Args:
            x: x coordinate relative to parent
            y: y coordinate relative to parent
            width: Layout width
            height: Layout height
            anchor: Anchor point 
            margin: Margin between childrens
            relative_width: Width as a proportion of parent from 0 to 1
            relative_height: Height as a proportion of parent from 0 to 1
            min_width: Minimum width
            min_height: Minimum height
            max_width: Maximum width
            max_height: Maximum height
        """
        super().__init__(x,y, width, height)
        self.anchor = anchor
        self.margin = margin
        self.widgets = []

        # Responsive sizing
        self.relative_width = relative_width
        self.relative_height = relative_height
        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height

        # For development purposes
        self.debug = False

    def add_widget(self, widget: 'WidgetAdapter') -> 'WidgetAdapter':
        """
        Add a widget to the layout
        """
        self.widgets.append(widget)
        widget.parent = self
        self.arrange_widgets()
        return widget

    def render(self, surface: pygame.Surface):
        """
        Render all widgets in the layout.
        """
        # Debugging
        if self.debug:
            abs_x, abs_y = self.absolute_position
            rect = pygame.Rect(abs_x, abs_y, self.width, self.height)
            pygame.draw.rect(surface, (255, 0, 0), rect, 1)
            
            # Draw anchor point
            anchor_x, anchor_y = self.anchor.value
            point_x = int(abs_x + (self.width * anchor_x))
            point_y = int(abs_y + (self.height * anchor_y))
            pygame.draw.circle(surface, (0, 255, 0), (point_x, point_y), 3)

        for widget in self.widgets:
            widget.render(surface)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events and propagate to widgets."""
        # Check if event is within layout
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            mouse_pos = pygame.mouse.get_pos()
            abs_x, abs_y = self.absolute_position
            layout_rect = pygame.Rect(abs_x, abs_y, self.width, self.height)
            
            if not layout_rect.collidepoint(mouse_pos):
                return False

        for widget in self.widgets:
            if widget.handle_event(event):
                return True
        return False


    def update(self, dt: float) -> None:
        """Update all widgets in the layout."""
        for widget in self.widgets:
            widget.update(dt)
            
    def arrange_widgets(self) -> None:
        """
        Arrange widgets in the layout.
        Override this method in subclasses to implement specific layouts.
        """
        pass

    def on_parent_resize(self, parent_width: int, parent_height: int) -> None:
        """Handle parent container resize events."""
        old_width, old_height = self.width, self.height
        
        # Calculate new size based on relative dimensions
        if self.relative_width is not None:
            self.width = int(parent_width * self.relative_width)
        if self.relative_height is not None:
            self.height = int(parent_height * self.relative_height)
            
        # Apply min/max constraints
        if self.min_width:
            self.width = max(self.width, self.min_width)
        if self.min_height:
            self.height = max(self.height, self.min_height)
            
        if self.max_width:
            self.width = min(self.width, self.max_width)
        if self.max_height:
            self.height = min(self.height, self.max_height)
            
        # Calculate position based on anchor
        anchor_x, anchor_y = self.anchor.value
        self.x = int((parent_width - self.width) * anchor_x)
        self.y = int((parent_height - self.height) * anchor_y)
        
        # If size changed, rearrange widgets
        if old_width != self.width or old_height != self.height:
            self.arrange_widgets()
