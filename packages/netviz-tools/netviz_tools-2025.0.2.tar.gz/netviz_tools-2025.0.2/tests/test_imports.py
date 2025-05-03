# tests/test_imports.py

def test_imports():
    import netviz_tools
    from netviz_tools import DataManager, TradeNetwork, TradeSeries, save_json, CONTINENT_COLORS
    assert callable(DataManager)
    assert callable(TradeNetwork)
    assert callable(TradeSeries)
    assert callable(save_json)
    assert isinstance(CONTINENT_COLORS, dict)