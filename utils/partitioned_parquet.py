from pathlib import Path
import shutil
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime

# Define the base directory where all Parquet files will be stored
DATA_DIR = Path("data/understat_players")

def write_partitioned_players(df, mode: str = "append"):
    """
    Write player data as partitioned Parquet files by (league, season).
    
    mode:
      - 'append' (default): keep existing parts
      - 'overwrite': delete each (league, season) partition before writing
    """
    for (league, season), part in df.groupby(["league", "season"]):
        if part.empty:
            print(f"[INFO] Skipping empty partition: {league} {season}")
            continue

        path = DATA_DIR / f"league={league}" / f"season={season}"

        # If overwrite mode is selected, remove the existing folder before writing new files
        if mode == "overwrite" and path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)

        # Convert the DataFrame into a PyArrow Table (efficient columnar format)
        table = pa.Table.from_pandas(part.reset_index(drop=True), preserve_index=False)

        filename = f"part-{datetime.now():%Y%m%d-%H%M%S}.parquet"
        pq.write_table(table, path / filename, compression="snappy", use_dictionary=False)

        print(f"[OK] Wrote {len(part)} rows to {path / filename} ({mode=})")