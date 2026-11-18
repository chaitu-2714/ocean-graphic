import pandas as pd
import numpy as np
import os
from datetime import datetime

class DatasetProcessor:
    @staticmethod
    def load_and_validate(file_path):
        """
        Loads CSV, Excel, or NetCDF (.nc) file and validates oceanographic dataset rules.
        Returns: (valid_records, validation_report_dict)
        """
        ext = os.path.splitext(file_path)[1].lower()

        if ext in ['.csv', '.txt']:
            df = pd.read_csv(file_path)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif ext in ['.nc', '.netcdf']:
            df = DatasetProcessor._parse_netcdf(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Allowed: CSV, Excel, NetCDF (.nc)")

        # Standardize column headers
        df = DatasetProcessor._standardize_columns(df)

        total_rows = len(df)
        errors = []
        warnings = []

        # Required columns check
        required = ['latitude', 'longitude', 'depth', 'temperature', 'salinity']
        missing_cols = [col for col in required if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing mandatory oceanographic columns: {', '.join(missing_cols)}")

        # Fill optional columns if missing
        if 'float_id' not in df.columns:
            df['float_id'] = 'ARGO_' + np.random.randint(10000, 99999, size=total_rows).astype(str)
        if 'region' not in df.columns:
            df['region'] = 'Bay of Bengal'
        if 'dissolved_oxygen' not in df.columns:
            df['dissolved_oxygen'] = 210.0
        if 'date_time' not in df.columns:
            df['date_time'] = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Data Type Conversions & Cleanups
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        df['depth'] = pd.to_numeric(df['depth'], errors='coerce')
        df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
        df['salinity'] = pd.to_numeric(df['salinity'], errors='coerce')
        df['dissolved_oxygen'] = pd.to_numeric(df['dissolved_oxygen'], errors='coerce').fillna(210.0)

        # Latitude validation (-90 to 90)
        invalid_lat = df[(df['latitude'] < -90) | (df['latitude'] > 90) | (df['latitude'].isna())]
        if len(invalid_lat) > 0:
            warnings.append(f"Removed {len(invalid_lat)} rows with invalid latitude (outside -90° to +90°)")
            df = df.drop(invalid_lat.index)

        # Longitude validation (-180 to 180)
        invalid_lon = df[(df['longitude'] < -180) | (df['longitude'] > 180) | (df['longitude'].isna())]
        if len(invalid_lon) > 0:
            warnings.append(f"Removed {len(invalid_lon)} rows with invalid longitude (outside -180° to +180°)")
            df = df.drop(invalid_lon.index)

        # Depth validation (non-negative)
        invalid_depth = df[(df['depth'] < 0) | (df['depth'].isna())]
        if len(invalid_depth) > 0:
            warnings.append(f"Removed {len(invalid_depth)} rows with negative depth")
            df = df.drop(invalid_depth.index)

        # Temperature / Salinity check
        invalid_temp = df[(df['temperature'] < -3) | (df['temperature'] > 45) | (df['temperature'].isna())]
        if len(invalid_temp) > 0:
            warnings.append(f"Removed {len(invalid_temp)} rows with anomalous temperature")
            df = df.drop(invalid_temp.index)

        # Duplicate check
        duplicates = df.duplicated(subset=['latitude', 'longitude', 'depth', 'date_time'])
        dup_count = duplicates.sum()
        if dup_count > 0:
            warnings.append(f"Deduplicated {dup_count} duplicate coordinate profiles")
            df = df.drop_duplicates(subset=['latitude', 'longitude', 'depth', 'date_time'])

        df['source_file'] = os.path.basename(file_path)
        valid_records = df.to_dict(orient='records')

        report = {
            "source_file": os.path.basename(file_path),
            "total_rows_read": total_rows,
            "valid_rows_imported": len(valid_records),
            "rejected_rows": total_rows - len(valid_records),
            "warnings": warnings,
            "regions_found": list(df['region'].unique()) if 'region' in df.columns else []
        }

        return valid_records, report

    @staticmethod
    def _standardize_columns(df):
        col_map = {}
        for col in df.columns:
            c = col.strip().lower()
            if 'lat' in c:
                col_map[col] = 'latitude'
            elif 'lon' in c or 'lng' in c:
                col_map[col] = 'longitude'
            elif 'depth' in c or 'pres' in c or 'pressure' in c:
                col_map[col] = 'depth'
            elif 'temp' in c or 'temperature' in c:
                col_map[col] = 'temperature'
            elif 'sal' in c or 'salinity' in c:
                col_map[col] = 'salinity'
            elif 'oxy' in c or 'oxygen' in c:
                col_map[col] = 'dissolved_oxygen'
            elif 'float' in c or 'platform' in c or 'id' in c:
                col_map[col] = 'float_id'
            elif 'date' in c or 'time' in c:
                col_map[col] = 'date_time'
            elif 'region' in c or 'location' in c or 'sea' in c or 'ocean' in c:
                col_map[col] = 'region'

        return df.rename(columns=col_map)

    @staticmethod
    def _parse_netcdf(file_path):
        import xarray as xr
        ds = xr.open_dataset(file_path)
        df = ds.to_dataframe().reset_index()
        ds.close()
        return df

    @staticmethod
    def create_sample_dataset(file_path="sample_argo_bay_of_bengal.csv"):
        """Generates a realistic oceanographic Argo float CSV dataset for testing/demo."""
        np.random.seed(42)
        n = 120

        floats = [f"ARGO_{np.random.randint(2900000, 2999999)}" for _ in range(n)]
        regions = np.random.choice(["Bay of Bengal", "Arabian Sea", "Equatorial Indian Ocean", "Andaman Sea"], size=n)
        lats = np.round(np.random.uniform(5.0, 20.0, size=n), 4)
        lons = np.round(np.random.uniform(80.0, 95.0, size=n), 4)
        depths = np.random.choice([5.0, 10.0, 25.0, 50.0, 100.0, 200.0, 500.0, 1000.0], size=n)
        
        # Temp decreases with depth
        temps = np.round(30.0 - (depths / 50.0) + np.random.uniform(-0.5, 0.5, size=n), 2)
        temps = np.clip(temps, 4.0, 31.5)

        salin = np.round(33.5 + (depths / 400.0) + np.random.uniform(-0.3, 0.3, size=n), 2)
        salin = np.clip(salin, 32.0, 36.0)

        d_oxy = np.round(220.0 - (depths / 10.0) + np.random.uniform(-5.0, 5.0, size=n), 1)
        d_oxy = np.clip(d_oxy, 20.0, 240.0)

        dates = pd.date_range(start="2021-01-15", end="2024-06-30", periods=n).strftime("%Y-%m-%d %H:%M").tolist()

        df = pd.DataFrame({
            "float_id": floats,
            "region": regions,
            "latitude": lats,
            "longitude": lons,
            "depth": depths,
            "temperature": temps,
            "salinity": salin,
            "dissolved_oxygen": d_oxy,
            "date_time": dates
        })

        df.to_csv(file_path, index=False)
        return file_path
