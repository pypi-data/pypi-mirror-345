from __future__ import annotations
from pathlib import Path
from typing import Optional, Tuple, Dict, List
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio
import geopandas as gpd
from .utils import save_json, CONTINENT_COLORS
from collections import Counter
import powerlaw


class TradeNetwork:
    """
    Directed trade graph for one year and commodity.

    Offers methods to:
      - plot static network (Matplotlib)
      - export interactive network JSON (Plotly)
      - export Sankey diagram JSON
      - export geographic trade flow map JSON
      - fit a power-law to the degree distribution
      - compare two networks side-by-side
    """

    def __init__(self, node_df: pd.DataFrame, edge_df: pd.DataFrame, *, year: int, item: str):
        self.year = year
        self.item = item
        self._nr = node_df.copy()
        self._er = edge_df.copy()
        self.G = self._build_graph()
        self.centrality_df = self._calc_centrality()

    def _build_graph(self) -> nx.DiGraph:
        G = nx.from_pandas_edgelist(
            self._er, 'O_name', 'D_name', edge_attr='weight', create_using=nx.DiGraph())
        for _, row in self._nr.iterrows():
            country = row.get('country')
            if country in G.nodes:
                G.nodes[country]['continent'] = row.get('continent')
        return G

    def _calc_centrality(self) -> pd.DataFrame:
        strength = dict(self.G.out_degree(weight='weight'))
        return pd.DataFrame({'country': list(strength), 'strength': list(strength.values())})

    @staticmethod
    def _scale(vals: List[float], mn: float, mx: float, log: bool = True) -> List[float]:
        arr = np.log10(np.array(vals) + 1) if log else np.array(vals, float)
        if np.ptp(arr) == 0:
            return [mx] * len(arr)
        norm = (arr - arr.min()) / np.ptp(arr)
        return (mn + norm * (mx - mn)).tolist()

    def _layout_spring(self) -> Dict[str, Tuple[float, float]]:
        return nx.spring_layout(self.G, seed=42)

    def _layout_graphviz(self, prog: str = 'neato', args: Optional[str] = None) -> Dict[str, Tuple[float, float]]:
        return nx.nx_agraph.graphviz_layout(self.G, prog=prog, args=args or '')

    def _choose_layout(self, layout: str, args: Optional[str] = None) -> Dict[str, Tuple[float, float]]:
        name = layout.lower()
        if name == 'spring':
            return self._layout_spring()
        return self._layout_graphviz(name, args)

    def plot(
        self,
        *,
        layout: str = 'neato',
        gv_args: Optional[str] = None,
        top_n: int = 25,
        prune_q: Optional[float] = None,
        arrows: bool = True,
        ax: Optional[plt.Axes] = None,
        save_path: str | Path = None,
        fmt: str = 'png'
    ) -> plt.Axes:
        """
        Static network plot using Matplotlib.
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 10))
        else:
            fig = ax.figure

        strength = pd.Series(dict(self.G.degree(weight='weight')))
        top_nodes = strength.nlargest(top_n).index
        Gs = self.G.subgraph(top_nodes).copy()

        if prune_q is not None and Gs.number_of_edges():
            thresh = np.quantile([d['weight'] for *_, d in Gs.edges(data=True)], prune_q)
            Gs.remove_edges_from([(u, v) for u, v, d in Gs.edges(data=True) if d['weight'] < thresh])

        pos = self._choose_layout(layout, gv_args)
        pos = {n: pos[n] for n in Gs.nodes}

        sizes = self._scale([strength[n] for n in Gs.nodes], 300, 2000)
        colors = [CONTINENT_COLORS.get(Gs.nodes[n].get('continent'), 'gray') for n in Gs.nodes]

        nx.draw_networkx_nodes(Gs, pos, node_size=sizes, node_color=colors, alpha=0.85, ax=ax)
        if Gs.number_of_edges():
            widths = self._scale([d['weight'] for *_, d in Gs.edges(data=True)], 0.3, 4.0)
            ecols = [CONTINENT_COLORS.get(Gs.nodes[u].get('continent'), 'gray') for u, _ in Gs.edges]
            nx.draw_networkx_edges(Gs, pos, width=widths, edge_color=ecols,
                                    arrows=arrows, arrowsize=8, alpha=0.7, ax=ax)
        nx.draw_networkx_labels(Gs, pos, font_size=8,
            bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='grey', alpha=0.7), ax=ax)
        ax.set_title(f"{self.item} trade network – {self.year} ({layout})")
        ax.axis('off')

        if save_path:
            out = Path(save_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(out.with_suffix(f'.{fmt}'), dpi=300, bbox_inches='tight')
            plt.close(fig)

        return ax

    def plot_interactive(
        self,
        *,
        top_n: int = 25,
        json_path: str | Path = None
    ) -> go.Figure:
        """
        Interactive network via Plotly; export to JSON if `json_path` is provided.
        """
        strength = pd.Series(dict(self.G.degree(weight='weight')))
        nodes = strength.nlargest(top_n).index.tolist()
        Gs = self.G.subgraph(nodes)

        pos = self._layout_spring()
        edge_traces = []
        for u, v, d in Gs.edges(data=True):
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            edge_traces.append(
                go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines',
                           line=dict(width=self._scale([d['weight']], 0.3, 4.0, log=False)[0]),
                           hoverinfo='text', text=f"{u} → {v}: {d['weight']:,} t")
            )
        node_trace = go.Scatter(
            x=[pos[n][0] for n in Gs.nodes], y=[pos[n][1] for n in Gs.nodes],
            mode='markers+text', text=list(Gs.nodes), textposition='top center', hoverinfo='text',
            marker=dict(size=self._scale([strength[n] for n in Gs.nodes], 10, 40),
                        color=[CONTINENT_COLORS.get(Gs.nodes[n].get('continent'), 'gray') for n in Gs.nodes],
                        line=dict(width=0.5))
        )
        fig = go.Figure(edge_traces + [node_trace])
        fig.update_layout(showlegend=False, title=f"{self.item} – {self.year}",
                          margin=dict(l=0, r=0, t=40, b=0), xaxis=dict(visible=False), yaxis=dict(visible=False))

        if json_path:
            save_json(fig, json_path)
        else:
            fig.show()
        return fig

    def plot_sankey(
        self,
        *,
        top_n: int = 25,
        json_path: str | Path = None
    ) -> go.Figure:
        """
        Sankey diagram; export to JSON if `json_path` is provided.
        """
        strength = dict(self.G.degree(weight='weight'))
        keep = sorted(strength, key=strength.get, reverse=True)[:top_n]
        Gs = self.G.subgraph(keep)
        idx = {c: i for i, c in enumerate(keep)}
        link = dict(source=[idx[u] for u, v in Gs.edges()],
                    target=[idx[v] for u, v in Gs.edges()],
                    value=[d['weight'] for *_, d in Gs.edges(data=True)])
        node = dict(pad=15, thickness=20,
                    line=dict(color='black', width=0.5),
                    label=keep,
                    color=[CONTINENT_COLORS.get(Gs.nodes[n].get('continent'), 'gray') for n in keep])
        fig = go.Figure(go.Sankey(node=node, link=link))
        fig.update_layout(title_text=f"{self.item} Sankey – {self.year}", font_size=10)

        if json_path:
            save_json(fig, json_path)
        else:
            fig.show()
        return fig

    def plot_geo(
        self,
        *,
        top_n: int = 100,
        size_col: str = "population",
        json_path: str | Path = None
    ) -> go.Figure:
        """
        Geographic trade flow map; export to JSON if `json_path` is provided.
        """
        world = gpd.read_file(Path("data/naturalearth_lowres") / "ne_110m_admin_0_countries.shp")[['NAME','geometry']]
        world = world.to_crs(epsg=4326)
        world['lon'] = world.geometry.centroid.x
        world['lat'] = world.geometry.centroid.y

        nd = self._nr[['country', size_col]].dropna()
        nd = nd.merge(world[['NAME','lon','lat']], left_on='country', right_on='NAME', how='inner')

        edges = self._er.rename(columns={'O_name':'source','D_name':'target'})
        top_edges = edges.nlargest(top_n, 'weight')
        wmax = top_edges['weight'].max()

        fig = go.Figure()
        sizeref = 2.0 * nd[size_col].max() / (30.0 ** 2)
        fig.add_trace(go.Scattergeo(
            lon=nd['lon'], lat=nd['lat'], mode='markers',
            marker=dict(size=nd[size_col], sizemode='area', sizeref=sizeref),
            text=nd['country'] + ': ' + nd[size_col].astype(str), hoverinfo='text'
        ))
        for _, row in top_edges.iterrows():
            src = nd[nd['country'] == row['source']].iloc[0]
            dst = nd[nd['country'] == row['target']].iloc[0]
            fig.add_trace(go.Scattergeo(
                lon=[src['lon'], dst['lon']], lat=[src['lat'], dst['lat']], mode='lines',
                line=dict(width=0.5 + 4 * (row['weight']/wmax))
            ))
        fig.update_layout(title_text=f"{self.year} Global {self.item} trade (top {top_n})",
                          showlegend=False, margin=dict(l=0, r=0, t=50, b=0),
                          geo=dict(scope='world', projection_type='equirectangular'))

        if json_path:
            save_json(fig, json_path)
        else:
            fig.show()
        return fig

    def fit_power_law(self, *, plot: bool = False, save_path: str | Path = None, fmt: str = 'png') -> powerlaw.Fit:
        """
        Fit a power-law to the degree distribution; if `plot=True` outputs a Matplotlib plot.
        """
        degrees = list(dict(self.G.degree()).values())
        fit = powerlaw.Fit(degrees, verbose=False)
        if plot:
            dist = Counter(degrees)
            x, y = zip(*sorted((k, dist[k]/len(self.G)) for k in dist))
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.plot([k for k in x if k>=fit.xmin], [p for k,p in zip(x,y) if k>=fit.xmin], 'o')
            fit.plot_pdf(ax=ax)
            fit.power_law.plot_pdf(ax=ax)
            ax.set_title(f"Power-law fit for {self.item} ({self.year})")
            if save_path:
                out = Path(save_path)
                out.parent.mkdir(parents=True, exist_ok=True)
                fig.savefig(out.with_suffix(f'.{fmt}'), dpi=300, bbox_inches='tight')
                plt.close(fig)
            else:
                plt.show()
        return fit

    @staticmethod
    def compare(
        left: TradeNetwork,
        right: TradeNetwork,
        *,
        layout: str = 'neato',
        gv_args: Optional[str] = None,
        top_n: int = 25,
        prune_q: Optional[float] = None,
        arrows: bool = True,
        save_path: str | Path = None,
        fmt: str = 'png'
    ) -> None:
        """
        Side-by-side comparison of two networks; optionally save as static image.
        """
        fig, axes = plt.subplots(1, 2, figsize=(18, 9))
        left.plot(layout=layout, gv_args=gv_args, top_n=top_n, prune_q=prune_q, arrows=arrows, ax=axes[0])
        right.plot(layout=layout, gv_args=gv_args, top_n=top_n, prune_q=prune_q, arrows=arrows, ax=axes[1])
        plt.tight_layout()
        if save_path:
            out = Path(save_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(out.with_suffix(f'.{fmt}'), dpi=300, bbox_inches='tight')
            plt.close(fig)
        else:
            plt.show()
