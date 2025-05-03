# tests/test_data_manager.py
import pytest
import pandas as pd
from netviz_tools.data_manager import DataManager

@pytest.fixture
def sample_node_edge(tmp_path):
    # Create minimal nodes and edges CSV files
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    # nodes.csv
    nodes = pd.DataFrame([
        {'year': 2020, 'cc': 'USA', 'country': 'United States', 'continent': 'Northern America'}
    ])
    nodes.to_csv(data_dir / 'nodes.csv', index=False)
    # edges.csv
    edges = pd.DataFrame([
        {'O_name': 'United States', 'D_name': 'United States', 'year': 2020, 'item': 'potatoes', 'weight': 100}
    ])
    edges.to_csv(data_dir / 'edges.csv', index=False)
    return tmp_path


def test_from_merged(sample_node_edge):
    dm = DataManager.from_merged(root=sample_node_edge)
    # list_years and list_items
    years = dm.list_years()
    items = dm.list_items()
    assert years == [2020]
    assert items == ['potatoes']
    # get_data returns dataframes
    nd, ed = dm.get_data(year=2020, item='potatoes')
    assert isinstance(nd, pd.DataFrame)
    assert isinstance(ed, pd.DataFrame)
    assert ed['weight'].iloc[0] == 100