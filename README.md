# ⚽ Player Comparison Dashboard

A Streamlit web app for comparing football player performance across the top 5 European leagues using data from [Understat.com](https://understat.com).

---

## 🚀 Features
- Compare two players side-by-side by league, season, and team.
- Visualize attacking, creative, and build-up play metrics.
- Toggle between **total stats** and **per 90 minutes** views.
- Interactive bar charts powered by Plotly.

---
## 🧩 Setup Instructions

### 1. Clone this repository
```bash
git clone https://github.com/zitherean/Player-Comparison-App.git
```

### 2. Move into the project folder you just cloned
```bash
cd path/Player-Comparison-App
```

### 3. Create and activate a virtual environment
```bash
python -m venv .venv
```
#### Windows
```bash
.venv\Scripts\activate
```
#### macOS/Linux
```bash
source .venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Fetch player data

Run the Understat data fetcher:

```bash
python scripts/fetch_player_data.py
```
This will create partitioned Parquet files under data/understat_players/.

### 6. Launch the Streamlit dashboard
```bash
streamlit run app.py
```
---
## 🧠 Notes

- Data sourced from Understat.com (for educational and informational use only).
- The app does not store or redistribute data.
- Some newer versions of python may not work. Python 3.11 was used for this project.
- Use on a computer screen. The dashboard layout is not optimized for mobile devices.

---
## 💡 Acknowledgments

Developed by Sami Finkbeiner.
Special thanks to the Understat community for providing open football data.

---
