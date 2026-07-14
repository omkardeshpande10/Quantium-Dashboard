import sys
import os

# Ensure the streamlit/ directory is on the path so import_app can find the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sales_visualizer2 import app


def _find_components(layout, component_type):
    """Recursively collect all components matching component_type in the layout tree."""
    found = []
    if isinstance(layout, component_type):
        found.append(layout)
    children = getattr(layout, "children", None)
    if isinstance(children, list):
        for child in children:
            found.extend(_find_components(child, component_type))
    elif children is not None:
        found.extend(_find_components(children, component_type))
    return found


def _find_by_id(layout, component_id):
    """Recursively find the first component with a matching id."""
    if getattr(layout, "id", None) == component_id:
        return layout
    children = getattr(layout, "children", None)
    if isinstance(children, list):
        for child in children:
            result = _find_by_id(child, component_id)
            if result is not None:
                return result
    elif children is not None:
        return _find_by_id(children, component_id)
    return None


def test_header_is_present():
    """The H1 banner heading exists in the layout with the correct text."""
    from dash import html

    h1_elements = _find_components(app.layout, html.H1)
    assert len(h1_elements) > 0, "No H1 element found in the layout"
    texts = [c.children for c in h1_elements if isinstance(c.children, str)]
    assert any("Pink Morsel Sales Dashboard" in t for t in texts), (
        f"Expected heading text not found. Found: {texts}"
    )


def test_visualisation_is_present():
    """A dcc.Graph with id='sales-chart' exists in the layout."""
    chart = _find_by_id(app.layout, "sales-chart")
    assert chart is not None, "No component with id='sales-chart' found in the layout"


def test_region_picker_is_present():
    """A dcc.RadioItems with id='region-filter' exists in the layout."""
    region_filter = _find_by_id(app.layout, "region-filter")
    assert region_filter is not None, (
        "No component with id='region-filter' found in the layout"
    )
