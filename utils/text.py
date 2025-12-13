import html

def clean_html_entities(df, columns):
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(html.unescape)
    return df
