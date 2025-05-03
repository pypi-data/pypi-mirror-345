from __future__ import annotations
from pathlib import Path
from typing import List
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


class TradeSeries:
    """
    Build and analyze time series of global network metrics over multiple years and items.

    Parameters
    ----------
    dm : DataManager
        A DataManager instance for loading networks.
    items : list of str
        Commodity items to include (e.g., ['potatoes', 'potatoes_frozen']).
    years : list of int
        Years to include (e.g., list(range(2012, 2023))).
    """
    def __init__(self, dm, *, items: List[str], years: List[int]):
        self.dm = dm
        self.items = items
        self.years = years
        self.global_df: pd.DataFrame = pd.DataFrame()
        self._build_all()

    def _build_all(self) -> None:
        """
        Constructs TradeNetwork for each (year, item) and compiles global metrics.
        """
        records = []
        for item in self.items:
            for year in self.years:
                net = self.dm.get_network(year=year, item=item)
                # total trade weight
                _, ed = self.dm.get_data(year=year, item=item)
                total_trade = ed['weight'].sum()
                # network density
                density = nx.density(net.G)
                # average node strength
                avg_strength = net.centrality_df['strength'].mean()
                records.append({
                    'year': year,
                    'item': item,
                    'density': density,
                    'total_trade': total_trade,
                    'avg_strength': avg_strength
                })
        self.global_df = pd.DataFrame(records)

    def plot_global_metric(
        self,
        metric: str,
        *,
        save_path: str | Path = None,
        fmt: str = 'png'
    ) -> None:
        """
        Plot a global metric over time for each item.

        Parameters
        ----------
        metric : {'density', 'total_trade', 'avg_strength'}
            Which metric to plot.
        save_path : str or Path, optional
            If given, save the figure to this path.
        fmt : str
            Format for saved figure (e.g., 'png', 'pdf').
        """
        if self.global_df.empty:
            raise ValueError("No data available. Did you call _build_all()?")
        pivot = self.global_df.pivot(index='year', columns='item', values=metric)
        fig = pivot.plot(figsize=(10, 4), marker='o').figure
        plt.xlabel('Year')
        if metric == 'total_trade':
            plt.ylabel('Total trade (weight units)')
            plt.title('Total Trade Over Years')
        elif metric == 'density':
            plt.ylabel('Network Density')
            plt.title('Network Density Over Years')
        elif metric == 'avg_strength':
            plt.ylabel('Average Node Strength')
            plt.title('Average Node Strength Over Years')
        else:
            plt.title(f'{metric} Over Years')
        if save_path:
            out = Path(save_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(out.with_suffix(f'.{fmt}'), dpi=300, bbox_inches='tight')
            plt.close(fig)
        else:
            plt.show()
