# netviz_tools

**Network visualization toolkit for FAOSTAT potato-trade data (2012–2022).**

`netviz_tools` provides:

- **DataManager**: Load, clean, and cache FAOSTAT node/edge data  
- **TradeNetwork**: Build NetworkX graphs, compute metrics, and export interactive Plotly JSON (networks, Sankeys, geo-maps)  
- **TradeSeries**: Generate and plot multi-year network statistics  
- **Utilities**: JSON exporters and shared constants (e.g., continent colors)  

---

## 📦 Installation

```bash
# From PyPI
pip install netviz_tools

# Or, for local development
git clone https://github.com/yourusername/netviz_tools.git
cd netviz_tools
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -e .[dev]
```

*(The `[dev]` extra pulls in testing tools like `pytest`.)*

---

## 🚀 Quick Start

```python
from netviz_tools import DataManager

# 1. Point at your raw or merged data folder
dm = DataManager(root="path/to/your/data")

# 2. Build a network for year & item
net = dm.get_network(year=2020, item="potatoes")

# 3. Export an interactive network JSON
net.plot_interactive(top_n=20, json_path="exports/json/net_2020_potatoes.json")

# 4. Make a Sankey JSON
net.plot_sankey(top_n=10, json_path="exports/json/sankey_2020_potatoes.json")

# 5. Geo-map JSON
net.plot_geo(top_n=50, json_path="exports/json/geo_2020_potatoes.json")
```

---

## 📚 Documentation

Detailed docs and examples in the [`docs/`](./docs) folder (or readthedocs once published).

---

## 🛠️ Development

1. **Create a virtualenv** (see Installation above).  
2. **Install dev requirements**:  
   ```bash
   pip install -e .[dev]
   ```
3. **Run tests**:  
   ```bash
   pytest
   ```
4. **Build distribution**:  
   ```bash
   python -m build
   ```
5. **Publish**:  
   ```bash
   twine upload dist/*
   ```

---

## 🤝 Contributing

1. Fork the repo  
2. Create a feature branch (`git checkout -b feat/my-feature`)  
3. Commit your changes  
4. Open a Pull Request  

Please follow the existing code style and write tests for new functionality.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](./LICENSE) file for details.

