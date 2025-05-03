# netviz_tools/utils.py

"""
Utility functions and shared constants for netviz_tools.
"""
from pathlib import Path
import plotly.io as pio
from plotly.graph_objects import Figure

# Color mapping for continents in visualizations
CONTINENT_COLORS: dict[str, str] = {
    "Africa": "red",
    "Asia": "green",
    "Europe": "blue",
    "Northern America": "purple",
    "Oceania": "orange",
    "South America": "pink",
    "Central America": "cyan",
    "Caribbean": "brown",
}


def save_json(fig: Figure, path: str | Path) -> None:
    """
    Save a Plotly Figure to a standalone JSON file, including data and layout.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        The figure to serialize.
    path : str or Path
        Destination file path for the JSON. Will create parent directories if needed.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(pio.to_json(fig, pretty=True))
