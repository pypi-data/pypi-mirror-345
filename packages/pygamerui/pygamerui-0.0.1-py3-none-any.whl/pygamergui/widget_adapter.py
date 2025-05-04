import pygame
from .element import Element
from typing import Tuple, Any

class WidgetAdapter(Element):
    """Adapter for Pygame UI elements to work with the framework."""
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0):
        """Initialize widget adapter."""
        super().__init__(x, y, width, height)
        self.pygame_element = None
        
    def set_pygame_element(self, element: Any) -> None:
        """Set the pygame element this adapter wraps."""
        self.pygame_element = element
        
    def render(self, surface: pygame.Surface) -> None:
        """Render the pygame element."""
        # Different pygame UI elements have different rendering methods
        # This is a simple example - adapt as needed for your specific widgets
        abs_x, abs_y = self.absolute_position
        
        # Update element position before rendering
        if hasattr(self.pygame_element, 'rect'):
            self.pygame_element.rect.x = abs_x
            self.pygame_element.rect.y = abs_y
            
        if hasattr(self.pygame_element, 'render'):
            # For elements with a render method
            self.pygame_element.render(surface)
        elif hasattr(self.pygame_element, 'draw'):
            # For elements with a draw method
            self.pygame_element.draw(surface)
        elif isinstance(self.pygame_element, pygame.Surface):
            # For Surface objects
            surface.blit(self.pygame_element, (abs_x, abs_y))
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for the pygame element."""         
        # Different pygame UI elements handle events differently
        # Implement based on your specific widget types
        if hasattr(self.pygame_element, 'handle_event'):
            return self.pygame_element.handle_event(event)
            
        # Default handling for clickable elements
        if event.type == pygame.MOUSEBUTTONDOWN:
            abs_x, abs_y = self.absolute_position
            element_rect = pygame.Rect(abs_x, abs_y, self.width, self.height)
            
            if element_rect.collidepoint(event.pos):
                # Call onClick handler if exists
                if hasattr(self.pygame_element, 'onClick'):
                    self.pygame_element.onClick()
                return True
                
        return False
        
    def update(self, dt: float) -> None:
        """Update the pygame element."""
        # Update position of the pygame element based on adapter position
        abs_x, abs_y = self.absolute_position
        
        if hasattr(self.pygame_element, 'rect'):
            self.pygame_element.rect.x = abs_x
            self.pygame_element.rect.y = abs_y
        elif hasattr(self.pygame_element, 'x') and hasattr(self.pygame_element, 'y'):
            self.pygame_element.x = abs_x
            self.pygame_element.y = abs_y
            
        # Call update method if exists
        if hasattr(self.pygame_element, 'update'):
            self.pygame_element.update(dt)
