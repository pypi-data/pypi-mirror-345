# 📘 MPIToolbox User Guide

## Attribution

This work builds upon code originally developed by Nicolai Suppa (2022), licensed under the MIT License.
This guide introduces the `MPIToolbox` Python class, designed to estimate, compare, and summarize multidimensional poverty indices (MPI) using flexible specifications.

---

## 🔧 Initialization

```python
from mpitb.core import MPIToolbox
mpi = MPIToolbox()
```

---

## 🗂️ 1. Define Specifications

```python
mpi.set(
    name="trial01",
    description="Preferred trial specification",
    dimensions=[
        (["d_cm", "d_nutr"], "hl"),
        (["d_satt", "d_educ"], "ed"),
        (["d_elct", "d_wtr", "d_sani", "d_hsg", "d_ckfl", "d_asst"], "ls")
    ],
    replace=True
)
```

- `name`: Unique name for the specification
- `dimensions`: A list of (indicators, dimension name)
- `replace=True`: Overwrite existing spec

---

## ⚖️ 2. Set Weights

```python
mpi.setwgts("trial01", "health50", dimw=[0.5, 0.25, 0.25])
mpi.setwgts("trial01", "ind_equal", indw=[0.1]*10)
```

You can define:
- Dimension-level weights (`dimw`)
- Indicator-level weights (`indw`)

---

## 📏 3. Estimate MPI

```python
mpi.est(
    df=df,
    name="trial01",
    klist=[33],
    weights="equal",
    svy=True,
    lframe="myresults",
    over=["region", "area"]
)
```

### Output:
- Estimation records are stored in `mpi.results["myresults"]`
- Use `replace=True` to overwrite an existing frame

---

## 📊 4. Change-over-Time Estimation

```python
mpi.est_cot(
    df=df,
    name="trial01",
    yearvar="t",
    klist=[33],
    cotmeasures=["M0", "H", "A", "hd", "hdk"],
    wgts="equal",
    cotframe="mycot",
    replace=True,
    raw=True,
    ann=True,
    total=True,
    insequence=False,
    svy=True
)
```

- `cotmeasures`: include `M0`, `H`, `A`, and optional `hd`, `hdk`
- `raw` and `ann`: toggle raw/annual change
- `total` or `insequence`: whether to compute period vs. year-to-year changes

---

## 📁 5. Extract and Summarize Results

Use functions from `mpi_results_utils.py` (see companion guide):

```python
from mpi_results_utils import extract_core_measures, extract_cot_summary, pivot_cot_summary

summary = extract_core_measures(df_myresults)
cot_table = extract_cot_summary(mpi.results, "mycot", measure="H", k=[33])
pivot = pivot_cot_summary(mpi.results, "mycot", measure=["H", "M0"], k=[33, 50])
```

---

## 📌 6. Store Custom Results

```python
mpi.stores(
    frame="myresults",
    loa="nat",
    measure="M0",
    spec="trial01",
    k=33,
    estimate=0.115,
    ts=True
)
```

You can manually add structured metadata to `mpi.results["myresults"]`.

---

## 🛠️ Other Tools

- `mpi.svyset(...)`: Define survey weight/PSU/stratum variables.
- `mpi.get_equal_weights(name)`: View equal weighting structure.
- `mpi.show(name)`: Print full spec summary.
- `mpi.rframe(...)`: Register a new result frame structure.

---

## 🧪 Example Quick Start

```python
mpi = MPIToolbox()
mpi.svyset(psu="psu", weight="weight", strata="stratum")
mpi.set(name="trial01", description="baseline", dimensions=[
    (["d_cm", "d_nutr"], "hl"),
    (["d_satt", "d_educ"], "ed"),
    (["d_elct", "d_wtr", "d_sani", "d_hsg", "d_ckfl", "d_asst"], "ls")
])
mpi.setwgts("trial01", "equal", dimw=[1/3, 1/3, 1/3])
mpi.est(df=df, name="trial01", klist=[33], weights="equal", svy=True, lframe="results")
```

---