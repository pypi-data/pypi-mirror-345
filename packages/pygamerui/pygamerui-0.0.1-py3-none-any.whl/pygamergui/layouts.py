from typing import List, Tuple, Optional, Dict, Any, Callable, Union
from enum import Enum
from .layout import Layout
from .widget_adapter import WidgetAdapter
from .anchor import Anchor

class StackDirection(Enum):
    HORIZONTAL = 0
    VERTICAL = 1

class StackLayout(Layout):
    """Layout that stacks widgets horizontally or vertically."""
    
    def __init__(self, direction: StackDirection = StackDirection.VERTICAL, 
                 spacing: int = 5, **kwargs):
        """
        Initialize a new StackLayout.
        
        Args:
            direction: Direction to stack widgets (horizontal or vertical)
            spacing: Space between widgets
            **kwargs: Additional arguments passed to Layout
        """
        super().__init__(**kwargs)
        self.direction = direction
        self.spacing = spacing
        
    def arrange_widgets(self) -> None:
        """Arrange widgets in a stack."""
        if not self.widgets:
            return
            
        if self.direction == StackDirection.VERTICAL:
            self._arrange_vertical()
        else:
            self._arrange_horizontal()
            
    def _arrange_vertical(self) -> None:
        """Stack widgets vertically."""
        y_offset = self.margin
        
        for widget in self.widgets:
            # Center horizontally in layout with respect to margin
            available_width = self.width - (2 * self.margin)
            x_pos = self.margin + (available_width - widget.width) // 2
            widget.x = max(self.margin, x_pos)  # Ensure widgets stay within margin
            widget.y = y_offset
            
            # Move to next position
            y_offset += widget.height + self.spacing
            
    def _arrange_horizontal(self) -> None:
        """Stack widgets horizontally."""
        x_offset = self.margin
        
        for widget in self.widgets:
            # Center vertically in layout
            widget.x = x_offset
            widget.y = (self.height - widget.height) // 2
            
            # Move to next position
            x_offset += widget.width + self.spacing

class GridLayout(Layout):
    """Layout that arranges widgets in a grid."""
    
    def __init__(self, rows: int = 1, cols: int = 1, 
                 h_spacing: int = 5, v_spacing: int = 5, **kwargs):
        """
        Initialize a new GridLayout.
        
        Args:
            rows: Number of rows in the grid
            cols: Number of columns in the grid
            h_spacing: Horizontal spacing between cells
            v_spacing: Vertical spacing between cells
            **kwargs: Additional arguments passed to Layout
        """
        super().__init__(**kwargs)
        self.rows = rows
        self.cols = cols
        self.h_spacing = h_spacing
        self.v_spacing = v_spacing
        
        # Initialize grid with None values
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
        
    def add_widget(self, widget: WidgetAdapter, row: int = None, col: int = None) -> WidgetAdapter:
        """
        Add a widget to a specific grid cell.
        
        Args:
            widget: Widget to add
            row: Row index (0-based)
            col: Column index (0-based)
            
        Returns:
            The added widget
        """
        # Find next available cell if row/col not specified
        if row is None or col is None:
            row, col = self._find_next_available_cell()
            
            if row is None or col is None:
                raise ValueError("Grid is full. Cannot add more widgets.")
                
        # Add widget to grid and widget list
        self.grid[row][col] = widget
        super().add_widget(widget)
        return widget
        
    def _find_next_available_cell(self) -> Tuple[Optional[int], Optional[int]]:
        """Find the next available cell in the grid."""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] is None:
                    return r, c
        return None, None
        
    def arrange_widgets(self) -> None:
        """Arrange widgets in a grid."""
        # Calculate cell dimensions
        cell_width = (self.width - self.margin * 2 - self.h_spacing * (self.cols - 1)) // self.cols
        cell_height = (self.height - self.margin * 2 - self.v_spacing * (self.rows - 1)) // self.rows
        
        # Position each widget in its cell
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] is not None:
                    widget = self.grid[r][c]
                    
                    # Calculate cell position
                    cell_x = self.margin + c * (cell_width + self.h_spacing)
                    cell_y = self.margin + r * (cell_height + self.v_spacing)
                    
                    # Center widget in cell
                    widget.x = cell_x + (cell_width - widget.width) // 2
                    widget.y = cell_y + (cell_height - widget.height) // 2
