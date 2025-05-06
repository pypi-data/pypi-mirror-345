import pandas as pd


def extract_model_summary(*dfs, measures=["H", "A", "M0"], stats=["b", "se", "ll", "ul"]):
    """
    Extracts and tabulates core MPI measures (H, A, M0) across multiple models AND k-values.

    Returns a wide-format summary with one row per measure, and columns like:
    'equal_k33_b', 'equal_k33_se', etc.
    """
    df = pd.concat(dfs, ignore_index=True)
    filtered = df[
        df["measure"].isin(measures) &
        (df["loa"] == "nat") &
        df["wgts"].notna() &
        df["k"].notna()
    ].copy()

    filtered["wgts"] = filtered["wgts"].astype(str)
    filtered["k"] = filtered["k"].astype(int)

    wide_tables = []
    for stat in stats:
        pivot = filtered.pivot_table(
            index="measure",
            columns=["wgts", "k"],
            values=stat
        )
        pivot.columns = [f"{w}_k{k}_{stat}" for (w, k) in pivot.columns]
        wide_tables.append(pivot)

    return pd.concat(wide_tables, axis=1).reset_index()


def extract_and_sort_by_time(
    results_dict, 
    frame_name="myresults", 
    measure=None, 
    wgts=None, 
    k=None, 
    include_nat=False
):
    df = pd.DataFrame(results_dict.get(frame_name, []))
    if df.empty:
        raise ValueError(f"No results found in frame '{frame_name}'.")

    df = df[df["loa"].isin(["t", "nat"] if include_nat else ["t"])].copy()
    df["t"] = pd.to_numeric(df["subg"], errors="coerce")

    if measure:
        df = df[df["measure"].isin([measure] if isinstance(measure, str) else measure)]
    if wgts:
        df = df[df["wgts"] == wgts]
    if k is not None and "k" in df.columns:
        if isinstance(k, list):
            df = df[df["k"].isin(k)]
        else:
            df = df[df["k"] == k]

    sort_cols = ["measure", "t", "k"] if "k" in df.columns else ["measure", "t"]
    return df.sort_values(by=sort_cols)


def extract_and_pivot_all_stats_by_time(
    results_dict,
    frame_name="myresults",
    measure=None,
    wgts=None,
    k=None,
    include_nat=False,
    stats=["b", "se", "ll", "ul"]
):
    df = pd.DataFrame(results_dict.get(frame_name, []))
    if df.empty:
        raise ValueError(f"No results found in frame '{frame_name}'.")

    df = df[df["loa"].isin(["t", "nat"] if include_nat else ["t"])].copy()
    df["t"] = pd.to_numeric(df["subg"], errors="coerce")

    if measure:
        df = df[df["measure"].isin([measure] if isinstance(measure, str) else measure)]
    if wgts:
        df = df[df["wgts"] == wgts]
    if k is not None and "k" in df.columns:
        if isinstance(k, list):
            df = df[df["k"].isin(k)]
        else:
            df = df[df["k"] == k]

    wide_parts = []
    for stat in stats:
        part = df.pivot_table(index="t", columns="measure", values=stat)
        part.columns = [f"{m}_{stat}" for m in part.columns]
        wide_parts.append(part)

    return pd.concat(wide_parts, axis=1).reset_index()


def extract_and_pivot_by_group(
    results_dict,
    frame_name="myresults",
    measure=["H", "A", "M0"],
    group_level="region",
    k=None,
    stats=["b"]
):
    df = pd.DataFrame(results_dict.get(frame_name, []))
    if df.empty:
        raise ValueError(f"No results found in frame '{frame_name}'.")

    df = df[df["loa"] == group_level].copy()

    if measure:
        df = df[df["measure"].isin(measure)]
    if k is not None and "k" in df.columns:
        if isinstance(k, list):
            df = df[df["k"].isin(k)]
        else:
            df = df[df["k"] == k]

    wide_parts = []
    for stat in stats:
        part = df.pivot_table(index="subg", columns="measure", values=stat)
        part.columns = [f"{m}_{stat}" for m in part.columns]
        wide_parts.append(part)

    return pd.concat(wide_parts, axis=1).reset_index()

def pivot_cot_summary(
    results_dict,
    frame_name="mycot",
    measure=["H", "A", "M0"],
    k=None,  # optional: if None, include all k-values
    change_type="total",
    ann=False,
    index=["spec"],  # e.g. ['spec'], ['subg'], ['t0', 't1']
    include_se=True,
    verbose=False
):
    """
    Pivot COT results to wide format with optional SE and multi-k support.

    Parameters:
    - results_dict: mpi.results
    - frame_name: result frame name
    - measure: list of measures (e.g., ['H', 'M0'])
    - k: cutoff value(s) to filter (int, list, or None)
    - change_type: 'total' or 'insequence'
    - ann: True for annual change, False for raw change
    - index: columns for row index
    - include_se: whether to include SEs in output
    - verbose: print preview

    Returns:
    - Wide-format DataFrame with columns like H_k33_raw, H_k33_se, etc.
    """
    df = pd.DataFrame(results_dict.get(frame_name, []))
    if df.empty:
        raise ValueError(f"No results found in frame '{frame_name}'.")

    df = df[df["change_type"] == change_type]

    if measure:
        df = df[df["measure"].isin(measure)]
    if k is not None:
        if isinstance(k, list):
            df = df[df["k"].isin(k)]
        else:
            df = df[df["k"] == k]

    # Determine value columns
    val_col = "ann" if ann else "raw"
    se_col = "se" if "se" in df.columns else None

    if df.empty:
        raise ValueError("No matching rows found after filtering by measure/k.")

    # Create key like H_k33_raw
    df["colkey"] = df["measure"].astype(str) + "_k" + df["k"].astype(str) + "_" + val_col

    value_df = df.pivot(index=index, columns="colkey", values=val_col)

    if include_se and se_col and se_col in df.columns:
        df["sekey"] = df["measure"].astype(str) + "_k" + df["k"].astype(str) + "_se"
        se_df = df.pivot(index=index, columns="sekey", values=se_col)
        combined = pd.concat([value_df, se_df], axis=1)
    else:
        combined = value_df

    if verbose:
        print(f"[pivot_cot_summary] shape = {combined.shape}")
        print(combined.head())

    return combined.reset_index()


def extract_cot_summary(
    results_dict,
    frame_name="mycot",
    measure=None,
    k=None,
    change_type="total",  # or "insequence"
    ann=False
):
    """
    Extract and summarize MPI change-over-time results (from est_cot).

    Parameters:
    - results_dict: mpi.results
    - frame_name: name of cot result frame
    - measure: filter for 'H', 'A', 'M0', etc.
    - k: optional k-value filter (e.g. 33)
    - change_type: 'total' or 'insequence'
    - ann: True for annual change, False for raw

    Returns:
    - A tidy DataFrame of change results
    """
    df = pd.DataFrame(results_dict.get(frame_name, []))
    if df.empty:
        raise ValueError(f"No results found in frame '{frame_name}'.")

    df = df[df["change_type"] == change_type]
    if measure:
        df = df[df["measure"] == measure]
    if k is not None and "k" in df.columns:
        if isinstance(k, list):
            df = df[df["k"].isin(k)]
        else:
            df = df[df["k"] == k]

    value_col = "ann" if ann else "raw"
    cols = ["measure", "k", "t0", "t1", value_col]

    for opt in ["spec", "wgts", "loa", "subg"]:
        if opt in df.columns:
            cols.append(opt)

    return df[cols]
