from datetime import datetime

import numpy as np
import pandas as pd
from scipy.stats import norm


class MPIToolbox:
    def __init__(self):
        self.mpi_specs = {}
        self.results = {}
        self.svy_settings = None  # store survey design information

    def svyset(self, psu=None, weight=None, strata=None):
        self.svy_settings = {"psu": psu, "weight": weight, "strata": strata}

    def set(self, name=None, description="", dimensions=None, clear=False, replace=False):
        if clear:
            self.mpi_specs.clear()
            return

        if not name or dimensions is None:
            raise ValueError("Both name and dimensions must be provided unless clear=True")

        if name in self.mpi_specs and not replace:
            raise ValueError(f"Specification '{name}' already exists. Use replace=True to overwrite.")

        structured_dims = {}
        for i, entry in enumerate(dimensions):
            if not isinstance(entry, tuple) or not isinstance(entry[0], list):
                raise ValueError("Each dimension must be a tuple: (indicator list, optional dim name)")
            indicators = entry[0]
            dimname = entry[1] if len(entry) > 1 and entry[1] else f"d{i+1}"
            structured_dims[dimname] = indicators

        self.mpi_specs[name] = {
            "description": description,
            "dimensions": structured_dims
        }

    def show_specs(self):
        return self.mpi_specs

    def get_equal_weights(self, name):
        spec = self.mpi_specs[name]
        dimensions = spec["dimensions"]
        n_dims = len(dimensions)
        dim_weight = 1 / n_dims
        weights = {}
        for dim, inds in dimensions.items():
            for ind in inds:
                weights[ind] = dim_weight / len(inds)
        return weights

    def get_weights(self, df):
        if self.svy_settings and self.svy_settings.get("weight") in df.columns:
            return df[self.svy_settings["weight"]]
        return pd.Series(1.0, index=df.index)

    def weighted_mean(self, values, weights):
        return (values * weights).sum() / weights.sum() if weights.sum() > 0 else 0

    def est(self, df, name, klist, weights="equal", measures=["M0", "H", "A"], 
        indmeasures=["hdk", "actb", "pctb"], indklist=None, aux=["hd"], 
        over=None, svy=False, addmeta=None, skipgen=False, gen=False, replace=False, 
        double=False, noestimate=False, lframe=None):

        if name not in self.mpi_specs:
            raise ValueError(f"MPI spec '{name}' not found. Please define it using set().")

        results = []
        spec = self.mpi_specs[name]
        dimensions = spec["dimensions"]
        all_inds = [ind for inds in dimensions.values() for ind in inds]

        if weights == "equal":
            ind_weights = self.get_equal_weights(name)
            wgtsname = "equal"
        elif isinstance(weights, str):
            wgtsname = weights
            try:
                ind_weights = self.mpi_specs[name]["weights"][weights]
            except KeyError:
                raise ValueError(f"Named weight profile '{weights}' not found in spec '{name}'.")
        elif isinstance(weights, dict):
            ind_weights = weights
            wgtsname = None
        else:
            raise NotImplementedError("Only 'equal' and dict weighting schemes currently supported.")

        def compute(df_sub, label=None, subgroup=None, klist_override = None, indklist_override = None):
            current_klist = klist_override if klist_override else klist
            recs = []
            w = self.get_weights(df_sub) if svy else pd.Series(1.0, index=df_sub.index)

            for k in current_klist:
                score = df_sub[all_inds].dot([ind_weights[i] for i in all_inds])
                df_sub[f"score_{k}"] = score
                is_poor = (score >= k / 100).astype(int)
                df_sub[f"poor_{k}"] = is_poor

                if noestimate:
                    continue

                H = self.weighted_mean(is_poor, w)
                A = self.weighted_mean(score[is_poor == 1], w[is_poor == 1]) if H > 0 else 0
                M0 = H * A

                z = norm.ppf(0.975)


                for mname, value in zip(["H", "A", "M0"], [H, A, M0]):
                    rec = {
                        "spec": name,
                        "k": k,
                        "loa": label or "national",
                        "measure": mname,
                        "b": value
                    }
                    if wgtsname:
                        rec["wgts"] = wgtsname
                    if mname == "H":
                        se = np.sqrt(H * (1 - H) / len(df_sub))
                    elif mname == "A":
                        se = np.std(score[is_poor == 1]) / np.sqrt((is_poor == 1).sum()) if H > 0 else 0
                    elif mname == "M0":
                        if H > 0:
                            poor_mask = is_poor == 1
                            w_eff = w.sum() ** 2 / (w ** 2).sum()
                            w_poor = w[poor_mask]
                            eff_n_poor = w_poor.sum() ** 2 / (w_poor ** 2).sum()

                            # Var(H)
                            var_H = H * (1 - H) / w_eff

                            # Var(A)
                            score_poor = score[poor_mask]
                            var_A = self.weighted_mean((score_poor - A) ** 2, w_poor) / eff_n_poor if eff_n_poor > 0 else 0

                            se = np.sqrt((A ** 2) * var_H + (H ** 2) * var_A)
                        else:
                            se = 0

                        """
                        Kish effective sample size
                        if H > 0:
                            poor_mask = is_poor == 1
                            eff_n = w[poor_mask].sum() ** 2 / (w[poor_mask] ** 2).sum()
                            std_score = np.sqrt(self.weighted_mean((score[poor_mask] - A) ** 2, w[poor_mask]))
                            se = np.sqrt((A**2 * H * (1 - H) / eff_n) + (H**2 * std_score**2 / eff_n))"""

                    rec["se"] = se
                    if se > 0:
                        rec["ll"] = value - z * se
                        rec["ul"] = value + z * se
                        rec["tval"] = value / se
                        rec["pval"] = 2 * (1 - norm.cdf(abs(rec["tval"])))
                    else:
                        rec["ll"] = rec["ul"] = rec["tval"] = rec["pval"] = None
                    if subgroup is not None:
                        rec["subg"] = subgroup
                    if addmeta:
                        rec.update(addmeta)
                    recs.append(rec)    
                
                current_indklist_loop = indklist_override or indklist or [k]
                for ind in all_inds:
                    for k_ind in current_indklist_loop:
                        ind_rec = {
                            "spec": name,
                            "k": k_ind,
                            "indicator": ind,
                            "loa": label or "national",
                            "measure": None,
                            "b": None
                        }
                        if wgtsname:
                            ind_rec["wgts"] = wgtsname
                        if subgroup is not None:
                            ind_rec["subg"] = subgroup
                        if addmeta:
                            ind_rec.update(addmeta)

                        if "hdk" in indmeasures: 
                            # Censored headcount ratio = poor AND deprived
                            joint = (df_sub[ind] == 1) & (is_poor == 1)
                            ind_rec.update({
                            "measure": "hdk",
                            "b": self.weighted_mean(joint.astype(int), w)
                            })
                            recs.append(ind_rec.copy())
                        if "actb" in indmeasures:
                            # absolute contribution
                            valid = df_sub[ind].notna()
                            contrib = self.weighted_mean(is_poor[valid] * df_sub.loc[valid, ind], w[valid]) * ind_weights[ind]
                            ind_rec.update({
                            "measure": "actb",
                            "b": contrib
                            })
                            recs.append(ind_rec.copy())
                        if "pctb" in indmeasures:
                            # relative contribution
                            pctb = contrib / M0 if M0 > 0 else 0
                            ind_rec.update({
                            "measure": "pctb",
                            "b": pctb
                            })
                            recs.append(ind_rec.copy())
             # Auxiliary measures (e.g., uncensored headcounts)
                if "hd" in aux:
                    for ind in all_inds:
                        valid = df_sub[ind].notna()
                        hd_val = self.weighted_mean(df_sub.loc[valid, ind], w[valid])
                        aux_rec = {
                            "spec": name,
                            "k": k,
                            "indicator": ind,
                            "loa": label or "national",
                            "measure": "hd",
                            "b": hd_val
                        }
                        if wgtsname:
                            aux_rec["wgts"] = wgtsname
                        if subgroup is not None:
                            aux_rec["subg"] = subgroup
                        if addmeta:
                            aux_rec.update(addmeta)
                        recs.append(aux_rec)
            return recs
        results.extend(compute(df, label="nat"))

        if over:
            if isinstance(over, dict):
                for var, opts in over.items():
                    subgroup_klist = opts.get("k", klist)
                    subgroup_indklist = opts.get("indk", indklist)
                    for grp, grp_df in df.groupby(var):
                        results.extend(compute(grp_df, label=var, subgroup=grp, 
                                            klist_override=subgroup_klist, 
                                            indklist_override=subgroup_indklist))
            else:
                for var in over:
                    for grp, grp_df in df.groupby(var):
                        results.extend(compute(grp_df, label=var, subgroup=grp))

        if lframe:
            if replace or lframe not in self.results:
                self.results[lframe] = results
            else:
                self.results[lframe].extend(results)

        return results
    
    def est_cot(self, df, name, yearvar, klist, cotmeasures=["M0", "H", "A"],
                total=True, insequence=True, ann=True, raw=True,
                cotframe=None, replace=False, over=None, nooverall=False, svy=False,
                wgts = "equal"):
        if name not in self.mpi_specs:
            raise ValueError(f"MPI spec '{name}' not found.")

        if yearvar not in df.columns:
            raise ValueError(f"'{yearvar}' not found in data.")
        
        years = sorted(df[yearvar].dropna().unique())
        if len(years) < 2:
            raise ValueError("At least two time points required for change-over-time estimation.")

        cot_results = []
        dimensions = self.mpi_specs[name]['dimensions']
        indicators = [i for inds in dimensions.values() for i in inds]
        z = norm.ppf(0.975)

        # Resolve weights
        if "weights" not in self.mpi_specs[name]:
            self.mpi_specs[name]["weights"] = {}
        if wgts == "equal" and "equal" not in self.mpi_specs[name]["weights"]:
            self.mpi_specs[name]["weights"]["equal"] = self.get_equal_weights(name)

        ind_weights = self.mpi_specs[name]["weights"].get(wgts)
        if ind_weights is None:
            raise ValueError(f"Weight profile '{wgts}' not found in MPI spec '{name}'.")

        def get_weights(sub):
            return self.get_weights(sub) if svy else pd.Series(1.0, index=sub.index)
        
        def se_change(base_val, next_val, n):
        # Simplified: SE for difference between proportions or means
            return np.sqrt((base_val * (1 - base_val) + next_val * (1 - next_val)) / n)

        def compute_M0_subset(sub):
            records = {}
            weights = get_weights(sub)
            # Check indicators exist in data
            missing = [i for i in indicators if i not in sub.columns]
            if missing:
                raise ValueError(f"Missing indicator columns: {missing}")
            
            try:
                for k in klist:
                    score = sub[indicators].dot([ind_weights[i] for i in indicators])
                    is_poor = (score >= k / 100).astype(int)
                    H = self.weighted_mean(is_poor, weights)
                    A = self.weighted_mean(score[is_poor == 1], weights[is_poor == 1]) if H > 0 else 0
                    if "M0" in cotmeasures: records[f"M0_k{k}"] = H * A
                    if "H" in cotmeasures: records[f"H_k{k}"] = H
                    if "A" in cotmeasures: records[f"A_k{k}"] = A
                    if "hd" in cotmeasures:
                        for ind in indicators:
                            records[f"hd_{ind}_k{k}"] = self.weighted_mean(sub[ind], weights)
                    if "hdk" in cotmeasures:
                        for ind in indicators:
                            mask = is_poor == 1
                            wpoor = weights[mask]
                            if wpoor.sum() > 0:
                                records[f"hdk_{ind}_k{k}"] = self.weighted_mean(sub.loc[mask, ind], wpoor)
                            else:
                                records[f"hdk_{ind}_k{k}"] = 0
            except Exception as e:
                raise ValueError(f"Failed in compute_M0_subset: {e}")

            if not records:
                raise ValueError("No M0, H, or A values were computed — check klist and data.")    
                
            return records

        def process_block(df_block, label=None, subgroup=None):
            out = []
            if total:
                df0 = df_block[df_block[yearvar] == years[0]]
                dfl = df_block[df_block[yearvar] == years[-1]]
                print(f"Computing base for period {years[0]} using {len(df0)} records.")
                base = compute_M0_subset(df0)
                if not base or not isinstance(base, dict):
                    raise ValueError("Base computation failed — empty or invalid format.")
                last = compute_M0_subset(dfl)
                for m in base:
                    rawchg = last[m] - base[m] if raw else None
                    annchg = rawchg / (years[-1] - years[0]) if ann else None

                    if "_k" in m:
                        base_measure, k_str = m.split("_k")
                        rec = {
                            "measure": base_measure,
                            "k": int(k_str),
                            "change_type": "total",
                            "t0": years[0],
                            "t1": years[-1]
                        }
                    else:
                        rec = {
                            "measure": m,
                            "change_type": "total",
                            "t0": years[0],
                            "t1": years[-1]
                        }

                    rec["spec"] = name
                    rec["wgts"] = wgts
                    if label: rec[label] = subgroup
                    if raw: rec["raw"] = rawchg
                    if ann: rec["ann"] = annchg

                    if rawchg is not None:
                        n = len(df_block)
                        se_val = se_change(base[m], last[m], n)
                        rec["se"] = se_val
                        rec["ll"] = rawchg - z * se_val
                        rec["ul"] = rawchg + z * se_val
                        rec["tval"] = rawchg / se_val if se_val > 0 else None
                        rec["pval"] = 2 * (1 - norm.cdf(abs(rec["tval"]))) if rec["tval"] is not None else None

                    out.append(rec)


            # INSEQUENCE CHANGE
            if insequence:
                for y0, y1 in zip(years[:-1], years[1:]):
                    df0 = df_block[df_block[yearvar] == y0]
                    df1 = df_block[df_block[yearvar] == y1]
                    base = compute_M0_subset(df0)
                    next = compute_M0_subset(df1)
                    for m in base:
                        rawchg = next[m] - base[m] if raw else None
                        annchg = rawchg / (y1 - y0) if ann else None

                        if "_k" in m:
                            base_measure, k_str = m.split("_k")
                            rec = {
                                "measure": base_measure,
                                "k": int(k_str),
                                "change_type": "insequence",
                                "t0": y0,
                                "t1": y1
                            }
                        else:
                            rec = {
                                "measure": m,
                                "change_type": "insequence",
                                "t0": y0,
                                "t1": y1
                            }

                        rec["spec"] = name
                        rec["wgts"] = wgts
                        if label: rec[label] = subgroup
                        if raw: rec["raw"] = rawchg
                        if ann: rec["ann"] = annchg

                        if rawchg is not None:
                            n = len(df_block)
                            se_val = se_change(base[m], next[m], n)
                            rec["se"] = se_val
                            rec["ll"] = rawchg - z * se_val
                            rec["ul"] = rawchg + z * se_val
                            rec["tval"] = rawchg / se_val if se_val > 0 else None
                            rec["pval"] = 2 * (1 - norm.cdf(abs(rec["tval"]))) if rec["tval"] is not None else None
                        
                        out.append(rec)

                return out

        if not nooverall:
            cot_results.extend(process_block(df))

        if over:
            for var in over:
                for group, group_df in df.groupby(var):
                    cot_results.extend(process_block(group_df, label=var, subgroup=group))

        if cotframe:
            if replace or cotframe not in self.results:
                self.results[cotframe] = cot_results
            else:
                self.results[cotframe].extend(cot_results)

        return cot_results
    
    def stores(self, frame, loa, measure, spec, ctype=0, k=None, indicator=None, wgts=None,
               tvar=None, t0=None, t1=None, yt0=None, yt1=None, ann=None, subg=None,
               add=None, ts=False, estimate=None):

        if frame not in self.results:
            self.results[frame] = []

        entry = {
            "frame": frame,
            "loa": loa,
            "measure": measure,
            "spec": spec,
            "ctype": ctype
        }

        if k is not None:
            entry["k"] = k
        if indicator is not None:
            entry["indicator"] = indicator
        if wgts is not None:
            entry["wgts"] = wgts
        if tvar is not None:
            entry["tvar"] = tvar
        if t0 is not None:
            entry["t0"] = t0
        if t1 is not None:
            entry["t1"] = t1
        if yt0 is not None:
            entry["yt0"] = yt0
        if yt1 is not None:
            entry["yt1"] = yt1
        if ann is not None:
            entry["ann"] = ann
        if subg is not None:
            entry["subg"] = subg
        if add is not None:
            entry["add"] = add
        if ts:
            entry["timestamp"] = datetime.now().isoformat()
        if estimate is not None:
            entry["estimate"] = estimate

        self.results[frame].append(entry)
        return entry

    def gafvars(self, df, indvars, indw, wgtsid, klist=None, cvector=False, indicator=False,
                replace=False, double=False):
        if len(indvars) != len(indw):
            raise ValueError("Length of indicator variables and weights must match.")

        results = df.copy()
        dtype = "float64" if double else "float32"

        weights = pd.Series(indw, index=indvars)
        scores = results[indvars].dot(weights)

        if cvector:
            cname = f"{wgtsid}_score"
            if cname in results.columns and not replace:
                raise ValueError(f"{cname} already exists. Use replace=True to overwrite.")
            results[cname] = scores.astype(dtype)

        if klist:
            for k in klist:
                pname = f"{wgtsid}_poor_k{k}"
                if pname in results.columns and not replace:
                    raise ValueError(f"{pname} already exists. Use replace=True to overwrite.")
                results[pname] = (scores >= k / 100).astype(int)

                if indicator:
                    for ind in indvars:
                        colname = f"{wgtsid}_{ind}_k{k}"
                        if colname in results.columns and not replace:
                            raise ValueError(f"{colname} already exists. Use replace=True to overwrite.")
                        results[colname] = (results[pname] == 1) & (results[ind] == 1)

        return results
    
    def setwgts(self, name, wgtsname, dimw=None, indw=None, store=False):
        if name not in self.mpi_specs:
            raise ValueError(f"Specification '{name}' not found.")

        spec = self.mpi_specs[name]
        dimensions = spec["dimensions"]
        all_inds = [ind for inds in dimensions.values() for ind in inds]

        if dimw is not None:
            if len(dimw) != len(dimensions):
                raise ValueError("dimw must match number of dimensions.")
            dimnames = list(dimensions.keys())
            ind_weights = {}
            for i, dim in enumerate(dimnames):
                inds = dimensions[dim]
                for ind in inds:
                    ind_weights[ind] = dimw[i] / len(inds)
        elif indw is not None:
            if len(indw) != len(all_inds):
                raise ValueError("indw must match number of indicators.")
            ind_weights = dict(zip(all_inds, indw))
        else:
            raise ValueError("Either dimw or indw must be provided.")

        spec.setdefault("weights", {})[wgtsname] = ind_weights

        if store:
            spec.setdefault("stored_weights", {})[wgtsname] = {
                "dimw": dimw,
                "indw": [ind_weights[ind] for ind in all_inds]
            }

    def rframe(self, frame, replace=False, double=False, t=False, cot=False, add=None, ts=False):
        if frame in self.results and not replace:
            raise ValueError(f"Frame '{frame}' already exists. Use replace=True to overwrite.")

        base_columns = {
            "b": float,
            "se": float,
            "ll": float,
            "ul": float,
            "pval": float,
            "tval": float,
            "spec": str,
            "loa": str,
            "measure": str,
            "wgts": str,
            "indicator": str,
            "k": float,
            "subg": str,
            "ctype": int
        }

        if t:
            base_columns["t"] = int
        if cot:
            base_columns.update({"t0": int, "t1": int, "yt0": float, "yt1": float, "ann": int})
        if add:
            base_columns[add] = str
        if ts:
            base_columns["timestamp"] = str

        # Initialize an empty list to store rows
        self.results[frame] = []
        self.results[frame + "_schema"] = base_columns
    
    def show(self, name=None, list_all=False):
        if list_all:
            print("Available MPI specifications:")
            for key, val in self.mpi_specs.items():
                print(f"  {key}: {val.get('description', '')}")
            return

        if not name or name not in self.mpi_specs:
            raise ValueError("Specify a valid MPI name.")

        spec = self.mpi_specs[name]
        dims = spec["dimensions"]
        stored_weights = spec.get("stored_weights", {})

        print("\nSpecification")
        print(f"Name: {name}")
        print(f"Description: {spec.get('description', '')}\n")

        print(f"{'Dimension':<12} {'Indicators'}")
        for i, (dim, inds) in enumerate(dims.items(), 1):
            print(f"  {dim:<10} ({', '.join(inds)})")

        # Default: equal weights
        equal_weights = self.get_equal_weights(name)
        print("\nDefault Equal Weights:")
        for ind in equal_weights:
            print(f"  {ind:<10} {equal_weights[ind]:.4f}")

        # Also show any stored weighting profiles
        if stored_weights:
            print("\nStored Weight Profiles:")
            for wgtsname, entry in stored_weights.items():
                print(f"\n  Profile: {wgtsname}")
                if "dimw" in entry:
                    print("    Dimension weights:")
                    for dimname, val in zip(dims.keys(), entry["dimw"]):
                        print(f"      {dimname:<10} {val:.4f}")
                if "indw" in entry:
                    print("    Indicator weights:")
                    for indname, val in zip([ind for inds in dims.values() for ind in inds], entry["indw"]):
                        print(f"      {indname:<10} {val:.4f}")
        else:
            print("\nNo stored weighting profiles found.\n")


