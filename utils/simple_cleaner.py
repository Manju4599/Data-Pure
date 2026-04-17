import re
import os
import csv
import chardet
import numpy as np
import pandas as pd
from datetime import datetime


class SimpleDataCleaner:
    def __init__(self, filepath, options=None):
        self.filepath = filepath
        self.options = options or {}
        self.df = None
        self.report = {}
        self._load_data()

    # ------------------------------------------------------------------
    # Data Loading
    # ------------------------------------------------------------------
    def _load_data(self):
        """Load data from file with robust error handling."""
        print(f"\nLoading file: {self.filepath}")

        ext = os.path.splitext(self.filepath)[1].lower()

        if ext == ".csv":
            self.df = self._read_csv_robustly()
        elif ext in [".xlsx", ".xls"]:
            try:
                self.df = pd.read_excel(self.filepath)
            except Exception as e:
                print(f"  Excel read failed: {e}")
                self.df = pd.DataFrame()
        elif ext == ".json":
            try:
                self.df = pd.read_json(self.filepath)
            except Exception as e:
                print(f"  JSON read failed: {e}")
                self.df = pd.DataFrame()
        else:
            # Fallback: try as CSV
            self.df = self._read_csv_robustly()

        if self.df is not None and not self.df.empty:
            self.original_shape = self.df.shape
            self.report["original_rows"] = int(self.original_shape[0])
            self.report["original_columns"] = int(self.original_shape[1])
            print(f"[OK] File loaded successfully! Shape: {self.df.shape}")
            print(f"  Columns: {list(self.df.columns)}")
        else:
            print("[!!] Failed to load file or file is empty")
            self.df = pd.DataFrame()
            self.original_shape = (0, 0)

    def _read_csv_robustly(self):
        """Try multiple strategies to read a CSV file."""
        for strategy in [self._try_pandas_read, self._try_csv_module, self._try_manual_parse]:
            df = strategy()
            if df is not None and not df.empty:
                return df
        return pd.DataFrame()

    def _try_pandas_read(self):
        encodings = ["utf-8", "latin1", "cp1252", "iso-8859-1", "utf-16"]
        for enc in encodings:
            try:
                df = pd.read_csv(self.filepath, encoding=enc, on_bad_lines="skip", engine="python")
                if not df.empty:
                    print(f"  Pandas read with {enc}: OK")
                    return df
            except Exception:
                continue
        return None

    def _try_csv_module(self):
        encodings = ["utf-8", "latin1", "cp1252", "iso-8859-1"]
        for enc in encodings:
            try:
                with open(self.filepath, "r", encoding=enc, errors="replace") as f:
                    first_line = f.readline()
                    f.seek(0)
                    delimiters = [",", ";", "\t", "|"]
                    delimiter = max(delimiters, key=lambda d: first_line.count(d))
                    reader = csv.reader(f, delimiter=delimiter)
                    rows = list(reader)
                    if rows and len(rows) > 1:
                        df = pd.DataFrame(rows[1:], columns=rows[0])
                        print(f"  CSV module with {enc}: OK")
                        return df
            except Exception:
                continue
        return None

    def _try_manual_parse(self):
        try:
            with open(self.filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = [l.strip() for l in f if l.strip()]
            if not lines:
                return None
            rows = [[cell.strip() for cell in line.split(",")] for line in lines]
            max_cols = max(len(r) for r in rows)
            for row in rows:
                row.extend([""] * (max_cols - len(row)))
            if len(rows) > 1:
                df = pd.DataFrame(rows[1:], columns=rows[0])
                print("  Manual parse: ✓")
                return df
        except Exception:
            pass
        return None

    # ------------------------------------------------------------------
    # Cleaning Pipeline
    # ------------------------------------------------------------------
    def clean_data(self):
        """Full cleaning pipeline respecting all user options."""
        if self.df is None or self.df.empty:
            self.report["error"] = "Empty DataFrame"
            return self.report

        original_rows = int(self.original_shape[0])
        original_cols = int(self.original_shape[1])

        steps_performed = []
        column_renames = {}
        missing_values_filled = 0
        duplicates_removed = 0
        outliers_removed = 0

        print(f"\nStarting cleaning process... Initial shape: {self.df.shape}")

        # ── 1. Standardize column names ──────────────────────────────
        new_columns = []
        for col in self.df.columns:
            cleaned = self._clean_column_name(col)
            new_columns.append(cleaned)
            if cleaned != str(col).strip():
                column_renames[str(col)] = cleaned
        self.df.columns = new_columns
        if column_renames:
            steps_performed.append("column_standardization")
        print(f"  Column names: {list(self.df.columns)}")

        # ── 2. Drop columns with too many missing values ─────────────
        threshold = float(self.options.get("missing_threshold", 0.5))
        if 0 < threshold < 1 and len(self.df) > 0:
            missing_pct = self.df.isnull().sum() / len(self.df)
            cols_to_drop = missing_pct[missing_pct > threshold].index.tolist()
            if cols_to_drop:
                self.df = self.df.drop(columns=cols_to_drop)
                print(f"  Dropped columns (>{threshold*100:.0f}% missing): {cols_to_drop}")

        # ── 3. Handle missing values ─────────────────────────────────
        handle_missing = self.options.get("handle_missing", "auto")
        if handle_missing != "none" and len(self.df) > 0:
            for col in self.df.columns:
                null_count = int(self.df[col].isnull().sum())
                if null_count == 0:
                    continue

                if handle_missing == "drop":
                    before = len(self.df)
                    self.df = self.df.dropna(subset=[col])
                    missing_values_filled += before - len(self.df)
                elif pd.api.types.is_numeric_dtype(self.df[col]):
                    if handle_missing == "mean":
                        fill = self.df[col].mean()
                    elif handle_missing == "mode":
                        mode_vals = self.df[col].mode()
                        fill = mode_vals.iloc[0] if not mode_vals.empty else self.df[col].median()
                    else:  # median or auto
                        fill = self.df[col].median()
                    self.df[col] = self.df[col].fillna(fill)
                    missing_values_filled += null_count
                    print(f"  '{col}': filled {null_count} nulls with {handle_missing} ({fill:.4g})")
                else:
                    if handle_missing == "mode":
                        mode_vals = self.df[col].mode()
                        fill = mode_vals.iloc[0] if not mode_vals.empty else "Unknown"
                    else:
                        fill = "Unknown"
                    self.df[col] = self.df[col].fillna(fill)
                    missing_values_filled += null_count
                    print(f"  '{col}': filled {null_count} nulls with '{fill}'")

            if missing_values_filled > 0 or handle_missing == "drop":
                steps_performed.append("missing_values")

        # ── 4. Remove duplicates ─────────────────────────────────────
        dup_action = self.options.get("handle_duplicates", "drop")
        if dup_action == "drop":
            dup_count = int(self.df.duplicated().sum())
            if dup_count > 0:
                self.df = self.df.drop_duplicates()
                duplicates_removed = dup_count
                steps_performed.append("duplicates")
                print(f"  Removed {dup_count} duplicate rows")
        elif dup_action == "flag":
            self.df["is_duplicate"] = self.df.duplicated()
            steps_performed.append("duplicates")
            print("  Flagged duplicates (is_duplicate column added)")

        # ── 5. Standardize text ──────────────────────────────────────
        if self.options.get("standardize_text"):
            text_cols = self.df.select_dtypes(include=["object"]).columns
            for col in text_cols:
                self.df[col] = self.df[col].astype(str).str.strip()
                self.df[col] = self.df[col].replace("nan", "")
                self.df[col] = self.df[col].replace("None", "")
            if len(text_cols) > 0:
                steps_performed.append("text_standardization")
                print(f"  Text standardized for {len(text_cols)} columns")

        # ── 6. Standardize dates ─────────────────────────────────────
        date_columns = []
        if self.options.get("standardize_dates"):
            date_formats = [
                "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y",
                "%m-%d-%Y", "%Y/%m/%d", "%d.%m.%Y", "%Y%m%d",
                "%d %b %Y", "%b %d %Y", "%B %d %Y",
            ]
            for col in self.df.select_dtypes(include=["object"]).columns:
                converted = self._try_parse_dates(self.df[col], date_formats)
                if converted is not None:
                    self.df[col] = converted.dt.strftime("%Y-%m-%d")
                    date_columns.append(col)
                    print(f"  Date column standardized: {col}")
            if date_columns:
                steps_performed.append("date_standardization")

        # ── 7. Infer / convert data types ────────────────────────────
        if self.options.get("infer_types"):
            for col in self.df.select_dtypes(include=["object"]).columns:
                if col in date_columns:
                    continue
                try:
                    numeric_converted = pd.to_numeric(self.df[col], errors="coerce")
                    # Only convert if majority of values are valid numbers
                    if numeric_converted.notna().sum() / max(len(self.df), 1) > 0.6:
                        self.df[col] = numeric_converted
                except Exception:
                    pass
            steps_performed.append("type_inference")
            print("  Data types inferred")

        # ── 8. Remove outliers ───────────────────────────────────────
        if self.options.get("remove_outliers"):
            method = self.options.get("outlier_method", "iqr")
            before = len(self.df)
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                if method == "zscore":
                    from scipy import stats as scipy_stats
                    z_scores = np.abs(scipy_stats.zscore(self.df[numeric_cols].fillna(0)))
                    mask = (z_scores < 3).all(axis=1)
                    self.df = self.df[mask]
                else:  # IQR
                    mask = pd.Series([True] * len(self.df), index=self.df.index)
                    for col in numeric_cols:
                        Q1 = self.df[col].quantile(0.25)
                        Q3 = self.df[col].quantile(0.75)
                        IQR = Q3 - Q1
                        if IQR > 0:
                            lower = Q1 - 1.5 * IQR
                            upper = Q3 + 1.5 * IQR
                            mask = mask & self.df[col].between(lower, upper)
                    self.df = self.df[mask]
                outliers_removed = before - len(self.df)
                if outliers_removed > 0:
                    steps_performed.append("outlier_removal")
                    print(f"  Removed {outliers_removed} outlier rows ({method.upper()})")

        # ── 9. Build report ──────────────────────────────────────────
        self.report.update({
            "final_rows": int(len(self.df)),
            "final_columns": int(len(self.df.columns)),
            "rows_removed": int(original_rows - len(self.df)),
            "columns_removed": int(original_cols - len(self.df.columns)),
            "duplicates_removed": duplicates_removed,
            "outliers_removed": outliers_removed,
            "missing_values_filled": missing_values_filled,
            "date_columns": date_columns,
            "column_renames": column_renames,
            "steps_performed": steps_performed if steps_performed else ["no_action_needed"],
            "cleaning_timestamp": datetime.now().isoformat(),
        })

        print(f"[OK] Cleaning complete. Final shape: {self.df.shape}")
        return self.report

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _clean_column_name(self, col):
        """Sanitise a column name to snake_case."""
        if pd.isna(col):
            return "unknown_column"
        col = str(col).strip()
        col = re.sub(r"[^\w\s]", "", col)
        col = re.sub(r"\s+", "_", col)
        col = col.lower()
        return col if col else "column"

    def _try_parse_dates(self, series, formats):
        """Return a datetime Series if the column looks like dates, else None."""
        sample = series.dropna().head(20)
        if len(sample) < 3:
            return None
        success = 0
        for fmt in formats:
            try:
                converted = pd.to_datetime(series, format=fmt, errors="coerce")
                valid = converted.notna().sum()
                if valid / max(len(series), 1) > 0.6:
                    return converted
                success += valid
            except Exception:
                pass
        # Try pandas infer
        try:
            converted = pd.to_datetime(series, errors="coerce")
            if converted.notna().sum() / max(len(series), 1) > 0.6:
                return converted
        except Exception:
            pass
        return None