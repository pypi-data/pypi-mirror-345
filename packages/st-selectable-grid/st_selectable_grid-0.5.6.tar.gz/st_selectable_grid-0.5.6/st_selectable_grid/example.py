import streamlit as st
import random
from st_selectable_grid import st_selectable_grid

# make wide mode
st.set_page_config(layout="wide")

# hide streamlit branding and reduce padding so the viewer takes up most of the space
# add '#MainMenu {visibility: hidden;}' if we want to hide the hamburger menu
st.markdown(
    """
    <style>
            .block-container {
                padding-top: 2.5rem;
                padding-bottom: 5rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }

            footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Selectable Grid Example")

# Example data with cell dictionaries
cells = [
    [
        {"label": "A1", "cell_color": "#f0f8ff", "mark": True},
        {"label": "<b>A2</b>", "cell_color": "#e6e6fa", "html": True, "tooltip": "Tooltip for A2", "mark": True},
        {"label": "A3", "cell_color": "#f5f5dc"},
        {"label": "A4", "cell_color": "#ffe4c4", "mark": True}
    ],
    [
        {"label": "B1", "cell_color": "#f0ffff"},
        {"label": "B2", "cell_color": "#f5f5f5"},
        {"label": "<span style='color:red'>B3</span>", "cell_color": "#fffaf0", "html": True},
        {"label": "B4", "cell_color": "#f0fff0"}
    ],
    [
        {"label": "C1", "cell_color": "#fff0f5"},
        {"label": "C2", "cell_color": "#f0f0f0"},
        {"label": "C3", "cell_color": "#fffff0"},
        {"label": "C4", "cell_color": "#f0f8ff", "tooltip": "Tooltip for C4\nOn two lines", "mark": True}
    ],
    [
        {"label": "D1", "cell_color": "#f5fffa"},
        {"label": "D2", "cell_color": "#f8f8ff"},
        {"label": "D3", "cell_color": "#faf0e6"},
        {"label": "D4", "cell_color": "#fff5ee"}
    ]
]

header = ["Column 1", "Column 2", "Column 3", "Column 4"]
index = ["Row 1", "Row 2", "Row 3", "Row 4"]

# Create the selectable grid with all options
selection = st_selectable_grid(
    cells=cells,
    header=header,
    index=index,
    allow_header_selection=True,
    allow_secondary_selection=False,
    aspect_ratio=0.5,
    height=300,
    grid_position="center",
    #resize=False,
    key="my_grid"
)

# Show the selection in the sidebar
st.sidebar.header("Selection")

if selection:
    if "primary" in selection:
        st.sidebar.write("Primary selection (left click):")
        st.sidebar.json(selection["primary"])
    
    if "secondary" in selection:
        st.sidebar.write("Secondary selection (right click):")
        st.sidebar.json(selection["secondary"])
else:
    st.sidebar.write("No cell selected yet.")

# Example of grid without header
st.header("Grid without header")
selection2 = st_selectable_grid(
    cells=cells,
    index=index,
    key="grid_no_header",
    height=300,
)

header = [
    {"label": "Module 1", "cell_color": "#f0f8ff"},
    {"label": "Module 2", "cell_color": "#e6e6fa", "tooltip": "Tooltip for Module 2", "mark": True},
    {"label": "Module 3", "cell_color": "#f5f5dc"},
    {"label": "Module 4", "mark": True, "tooltip": "Tooltip for Module 4"}
]

# Example of grid without index
st.header("Grid without index")
selection3 = st_selectable_grid(
    cells=cells,
    header=header,
    mark_color="#FF5722", 
    primary_selection_color="#FF9800",
    secondary_selection_color="#FFEB3B",
    allow_header_selection=True,
    allow_secondary_selection=True,
    key="grid_no_index",
    height=300,
)

cells = [
    ["A1", "A2", "A3", "A4"],
    ["B1", "B2", "B3", "B4"],
    ["C1", "C2", "C3", "C4"],
    ["D1", "D2", "D3", "D4"]
]

# Example of basic grid
st.header("Basic grid - no colors")
selection4 = st_selectable_grid(
    cells=cells,
    key="basic_grid",
    height=300,
)




st.title("Large Selectable Grid Example (25x16)")

# Set dimensions for the grid
rows = 16
cols = 25
random.seed(17)  # For reproducibility

# Create header and index
header = [f"Mod {i+1}" for i in range(cols)]
index = [f"Chic {i+1}" for i in range(rows)]

# Initialize all cells as green
cells = []
for x in range(rows):
    row = []
    for y in range(cols):
        # get a number 1-5
        num = random.randint(1, 5)
        #num = ""
        row.append({"label": f"{num}", "cell_color": "#E0FFE0", "tooltip": f"Location: {x+1}.{y+1}\nSN: PLW1234.12345\nOriginal Location: 12.5"})  # Light green color
    cells.append(row)

for _ in range(5):
    x = random.randint(0, rows-1)
    y = random.randint(0, cols-1)
    cells[x][y]["cell_color"] =  "#FFCCCB"
    cells[x][y]["label"] =  "9"

# make 5 random cells have "mark" set to True
for _ in range(5):
    x = random.randint(0, rows-1)
    y = random.randint(0, cols-1)
    cells[x][y]["mark"] = True
    cells[x][y]["tooltip"] = f"Location: {x+1}.{y+1}\nSN: PLW1234.12345\nOriginal Location: {x+2}.{y+2}"  # Update tooltip


# Create the selectable grid
selection = st_selectable_grid(
    cells=cells,
    header=header,
    index=index,
    allow_secondary_selection=True,
    allow_header_selection=True,
    aspect_ratio=.5,
    key="large_grid"
)

# Show the selection in the sidebar
st.sidebar.header("Selection")

if selection:
    if "primary" in selection:
        st.sidebar.write("Primary selection (left click):")
        st.sidebar.json(selection["primary"])
    
    if "secondary" in selection:
        st.sidebar.write("Secondary selection (right click):")
        st.sidebar.json(selection["secondary"])
else:
    st.sidebar.write("No cell selected yet.")

# Check if the user found the red cells
if selection and "primary" in selection:
    primary_x = selection["primary"]["x"]
    primary_y = selection["primary"]["y"]
    