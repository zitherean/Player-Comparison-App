import html
import numpy as np

def clean_html_entities(df, columns):
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(html.unescape)
    return df

def to_float(x):
    """Best-effort numeric conversion for comparisons (works for numpy + strings)."""
    if isinstance(x, (int, float, np.integer, np.floating)):
        if np.isnan(x):
            return 0.0
        v = float(x)
        return v
    
def format_value(value):
    """
    Formats any metric consistently:
      - NaN -> "0"
      - Integer -> "5"
      - Float -> "0.45"
      - String -> unchanged
    """

    if value is None:
        return "—"

    # Handle pandas / numpy NaN
    if isinstance(value, float) and np.isnan(value):
        return 0

    # Try numeric conversion
    try:
        num = float(value)

        # integer-like (3.0 becomes "3")
        if num.is_integer():
            return str(int(num))

        # float -> format with 2 decimals
        return f"{num:.2f}"

    except (ValueError, TypeError):
        # Non-numeric: keep original (e.g. names, clubs)
        return str(value)
