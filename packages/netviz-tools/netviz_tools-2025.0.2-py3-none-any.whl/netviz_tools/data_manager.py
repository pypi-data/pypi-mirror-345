from __future__ import annotations
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import pandas as pd
import geopandas as gpd

from .trade_network import TradeNetwork

class DataManager:
    """
    Load, clean, cache, and serve node/edge data for network visualization.

    Supports loading from pre-merged files or from arbitrary lists of CSVs.

    Usage:
      # From merged CSVs:
      dm = DataManager.from_merged(root="/path/to/project")

      # From custom node/edge CSV lists:
      dm = DataManager.from_csvs(
          node_files=["gdp.csv","pop.csv","unp.csv","continents.csv"],
          node_keys=["year","cc","country"],
          edge_files=["potatoes.csv","potatoes_frozen.csv"],
          edge_keys=["O_name","D_name","year","item"],
          weight_col="weight",
          cache_dir="/path/to/project/data"
      )
    """

    def __init__(self, nodes: pd.DataFrame, edges: pd.DataFrame):
        # Copy + clean
        self.nodes = nodes.copy()
        self.edges = edges.copy()
        self._basic_clean()

        # Index for available filters
        self.available_years = sorted(self.edges['year'].unique().tolist())
        self.available_items = sorted(self.edges['item'].unique().tolist())

        # Caches
        self._data_cache: Dict[Tuple[int,str], Tuple[pd.DataFrame,pd.DataFrame]] = {}
        self._net_cache: Dict[Tuple[int,str], TradeNetwork] = {}

    @classmethod
    def from_merged(cls, root: str | Path) -> DataManager:
        """
        Load nodes.csv and edges.csv from `root/data` directory.
        """
        root = Path(root)
        data_dir = root / "data"
        nodes = pd.read_csv(data_dir / "nodes.csv")
        edges = pd.read_csv(data_dir / "edges.csv")
        return cls(nodes, edges)

    @classmethod
    def from_csvs(
        cls,
        *,
        node_files: List[str | Path],
        node_keys: List[str],
        edge_files: List[str | Path],
        edge_keys: List[str],
        weight_col: str = "weight",
        cache_dir: Optional[str | Path] = None
    ) -> DataManager:
        """
        Load and merge node and edge data from lists of CSV paths.

        Parameters
        ----------
        node_files : list of CSV paths to merge (outer join on `node_keys`)
        node_keys : list of column names to join node files
        edge_files : list of CSV paths to concatenate
        edge_keys : list of column names to group edges by (excluding `weight_col`)
        weight_col : column name to sum when grouping edges
        cache_dir : optional directory to write merged CSVs under `<cache_dir>/data`
        """
        # Merge nodes on specified keys
        dfs = [pd.read_csv(p) for p in node_files]
        nodes = dfs[0]
        for df in dfs[1:]:
            nodes = nodes.merge(df, on=node_keys, how="outer")
        # Rename continent columns if present
        if 'continent' not in nodes.columns and 'Country Group' in nodes.columns:
            nodes = nodes.rename(columns={'Country Group':'continent','Country':'country'})

        # Concatenate edge files and group by specified keys
        edfs = [pd.read_csv(p) for p in edge_files]
        edges = pd.concat(edfs, ignore_index=True)
        edges = edges.groupby(edge_keys, as_index=False)[weight_col].sum()
        edfs = [pd.read_csv(p) for p in edge_files]
        edges = pd.concat(edfs, ignore_index=True)
        # group to sum weights
        keys = edge_keys
        edges = edges.groupby(keys, as_index=False)[weight_col].sum()

        # Prune to matching nodes
        country_col = 'country' if 'country' in nodes.columns else node_keys[-1]
        valid = nodes[country_col]
        u, v = edge_keys[0], edge_keys[1]
        edges = edges[edges[u].isin(valid) & edges[v].isin(valid)]
        nodes = nodes[nodes[country_col].isin(edges[u]) | nodes[country_col].isin(edges[v])]

        # Optional caching
        if cache_dir:
            out = Path(cache_dir) / "data"
            out.mkdir(parents=True, exist_ok=True)
            nodes.to_csv(out / "nodes.csv", index=False)
            edges.to_csv(out / "edges.csv", index=False)

        return cls(nodes, edges)

    def list_years(self) -> list[int]:
        """Return available years in the data."""
        return self.available_years

    def list_items(self) -> list[str]:
        """Return available commodity items in the data."""
        return self.available_items

    def _basic_clean(self) -> None:
        """Strip whitespace, drop invalid aggregates, and standardize columns."""
        # Strip whitespace on country columns
        for col in ['country', 'O_name', 'D_name']:
            if col in self.nodes.columns:
                self.nodes['country'] = self.nodes['country'].str.strip()
        if {'O_name','D_name'}.issubset(self.edges.columns):
            self.edges[['O_name','D_name']] = self.edges[['O_name','D_name']].apply(lambda c: c.str.strip())
        # Remove aggregate region codes if present
        if 'cc' in self.nodes.columns:
            self.nodes = self.nodes[~self.nodes['cc'].isin({'WLD','EUU','OECD'})]

    def get_data(self, *, year: int, item: str) -> Tuple[pd.DataFrame,pd.DataFrame]:
        """Return filtered (nodes, edges) for a given year and item."""
        if year not in self.available_years:
            raise ValueError(f"Year {year} not in {self.available_years}")
        if item not in self.available_items:
            raise ValueError(f"Item '{item}' not in {self.available_items}")
        key = (year, item)
        if key not in self._data_cache:
            nd = self.nodes.query("year==@year").copy()
            ed = self.edges.query("year==@year & item==@item").copy()
            self._data_cache[key] = (nd, ed)
        return self._data_cache[key]

    def get_network(self, *, year: int, item: str) -> TradeNetwork:
        """Build or retrieve a TradeNetwork for a given year and item."""
        key = (year, item)
        if key not in self._net_cache:
            nd, ed = self.get_data(year=year, item=item)
            self._net_cache[key] = TradeNetwork(nd, ed, year=year, item=item)
        return self._net_cache[key]

    @staticmethod
    def load_naturalearth_lowres(shapefile_dir: str = "data/naturalearth_lowres") -> gpd.GeoDataFrame:
        """Load Natural Earth shapefile as GeoDataFrame."""
        shp = Path(shapefile_dir) / "ne_110m_admin_0_countries.shp"
        if not shp.exists():
            raise FileNotFoundError("Run DataManager.load_naturalearth_lowres first.")
        return gpd.read_file(shp)[['ISO_A3', 'geometry']]