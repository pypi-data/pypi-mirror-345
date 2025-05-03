# tests/test_trade_network.py
import pandas as pd
from netviz_tools.trade_network import TradeNetwork

def test_trade_network_basic():
    # Minimal node and edge frames
    nodes = pd.DataFrame([{'country': 'A', 'continent': 'Europe'}])
    edges = pd.DataFrame([{'O_name': 'A', 'D_name': 'A', 'weight': 5}])
    tn = TradeNetwork(nodes, edges, year=2000, item='test')
    # Graph constructed
    assert 'A' in tn.G.nodes
    assert tn.G.number_of_edges() == 1
    # Centrality
    df = tn.centrality_df
    assert df.loc[df.country=='A','strength'].iloc[0] == 5
