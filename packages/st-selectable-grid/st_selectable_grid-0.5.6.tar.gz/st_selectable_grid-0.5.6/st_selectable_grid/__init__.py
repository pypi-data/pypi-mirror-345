import os
import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "st_selectable_grid",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("st_selectable_grid", path=build_dir)


def st_selectable_grid(
    cells,
    header=None,
    index=None,
    aspect_ratio=1,
    allow_secondary_selection=False,
    allow_header_selection=False,
    height=None,
    grid_position="center",
    resize=True,
    mark_color="#2196F3",
    primary_selection_color="#2196F3",
    secondary_selection_color="#FF9800",
    key=None,
):
    """Create a new instance of a selectable grid component.

    Parameters
    ----------
    cells: List[List[dict or str]]
        A 2D array of dictionaries or strings to be displayed in the grid.
        Dictionary items should contain:
        - "label": str - The text to display in the cell
        - "cell_color": str - The background color of the cell (CSS color format)
        - "tooltip": str - Optional tooltip text to display when hovering over the cell
        - "mark": bool - If True, marks the cell with a dot in the top right corner
        - "html": bool - If True, renders the label as HTML (allows formatting tags)
        If strings are provided, they will be converted to dictionaries with the string as the label.
    header: List[dict or str] or None
        An optional 1D array of dictionaries or strings to be displayed as column headers.
        Dictionary items follow the same format as cells.
    index: List[str or dict] or None
        An optional 1D array of strings or dictionaries to be displayed as row names.
        Dictionary items follow the same format as cells.
    aspect_ratio: float
        An optional argument to control the aspect ratio of cells. Defaults to 1.
    allow_secondary_selection: bool
        If True, allows right-click to select a secondary cell. Defaults to False.
    allow_header_selection: bool
        If True, allows header cells to be selected. Defaults to False.
        When a header is selected as primary, secondary selection can only be another header.
        When a grid cell is selected as primary, secondary selection can only be another grid cell.
    height: int or None
        An optional argument to cap the maximum height of the grid in pixels.
        If not specified, the grid will automatically size based on content and aspect ratio.
    grid_position: str
        Controls the horizontal alignment of the grid. Options: 'left', 'center' (default), 'right'.
    resize: bool
        If True (default), the grid will resize to fill available space.
        If False, the grid will maintain its size based on content.
    mark_color: str
        Color for marker dots that appear on cells with mark=True. Defaults to "#2196F3" (blue).
    primary_selection_color: str
        Color for the primary (left-click) selection highlight. Defaults to "#2196F3" (blue).
    secondary_selection_color: str
        Color for the secondary (right-click) selection highlight. Defaults to "#FF9800" (orange).
    key: str or None
        An optional key that uniquely identifies this component.

    Returns
    -------
    dict
        A dictionary containing selection information with the following structure:
        - For left click (primary): {'primary': {'x': col_index, 'y': row_index}}
        - For right click (secondary): {'secondary': {'x': col_index, 'y': row_index}}
        Secondary selection is only available after a primary selection.
    """
    # Process cells: Convert strings to dicts if needed
    if isinstance(cells, list) and all(isinstance(row, list) for row in cells):
        for i, row in enumerate(cells):
            if isinstance(row, list) and all(isinstance(cell, str) for cell in row):
                cells[i] = [{"label": cell} for cell in row]
            elif isinstance(row, list) and all(isinstance(cell, dict) for cell in row):
                for j, cell in enumerate(row):
                    if isinstance(cell, dict) and "label" not in cell:
                        cells[i][j]["label"] = str(cell)

    # Process header: Convert strings to dicts if needed
    if header is not None:
        if all(isinstance(item, str) for item in header):
            header = [{"label": item} for item in header]
        elif all(isinstance(item, dict) for item in header):
            for i, item in enumerate(header):
                if "label" not in item:
                    header[i]["label"] = str(item)

    # Process index: Convert strings to dicts if needed
    if index is not None:
        if all(isinstance(item, str) for item in index):
            index = [{"label": item} for item in index]
        elif all(isinstance(item, dict) for item in header):
            for i, item in enumerate(index):
                if "label" not in item:
                    index[i]["label"] = str(item)

    # Validate grid_position
    if grid_position not in ["left", "center", "right"]:
        grid_position = "center"

    # Call through to our private component function
    grid_value = _component_func(
        cells=cells,
        header=header,
        index=index,
        aspect_ratio=aspect_ratio,
        allow_secondary_selection=allow_secondary_selection,
        allow_header_selection=allow_header_selection,
        height=height,
        grid_position=grid_position,
        resize=resize,
        mark_color=mark_color,
        primary_selection_color=primary_selection_color,
        secondary_selection_color=secondary_selection_color,
        key=key,
        default={},
    )

    return grid_value
