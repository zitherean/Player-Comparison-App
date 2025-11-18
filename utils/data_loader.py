import streamlit as st
import pandas as pd
import glob

@st.cache_resource
def load_understat_data(base_path):
    # Find all parquet files recursively (each partition = league/season)
    paths = glob.glob(f"{base_path}/league=*/season=*/*.parquet")
    if not paths:
        raise FileNotFoundError(f"No data files found.")
    
    # Load and combine all league/season parquet files into a single DataFrame
    dfs = []
    for p in paths:
        df = pd.read_parquet(p)      
        df["league"] = df["league"].astype(str)
        df["season"] = df["season"].astype(str)
        dfs.append(df)

    # Return and merge all data
    return pd.concat(dfs, ignore_index=True)