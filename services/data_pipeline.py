"""
Data Pipeline — Sentinel AI V2.0
Merges GTD, ACLED, GDELT (live), and NewsAPI (live) datasets,
normalizes, cleans, and produces a single unified intelligence
dataset for all downstream use.
"""
import os
import re
import pandas as pd
import numpy as np
from loguru import logger
from typing import Optional
from utils.config import settings
from services.dataset_loader import DatasetLoader


class DataPipeline:
    """
    Unified data pipeline that merges GTD + ACLED,
    applies comprehensive cleaning, and saves the processed dataset.
    Designed to support future dataset sources without modification.
    """

    def __init__(self):
        self.loader = DatasetLoader()

    def run(self, force_rebuild: bool = False) -> Optional[pd.DataFrame]:
        """
        Full pipeline execution.
        Returns the unified DataFrame (also saved to parquet).
        """
        output_path = settings.UNIFIED_DATASET_PATH

        if os.path.exists(output_path) and not force_rebuild:
            logger.info(f"Loading existing unified dataset from {output_path}")
            try:
                return pd.read_parquet(output_path)
            except Exception as e:
                logger.warning(f"Failed to load cached dataset: {e}. Rebuilding...")

        logger.info("Starting unified data pipeline...")

        datasets = []

        # 1. Load GTD
        gtd = self.loader.load_gtd()
        if gtd is not None and not gtd.empty:
            datasets.append(gtd)
            logger.info(f"GTD: {len(gtd):,} records loaded")

        # 2. Load ACLED
        acled = self.loader.load_acled()
        if acled is not None and not acled.empty:
            datasets.append(acled)
            logger.info(f"ACLED: {len(acled):,} records loaded")

        # 3. Load GDELT live feed (free, no API key)
        if settings.GDELT_ENABLED:
            gdelt = self.loader.load_gdelt_live(max_records=5000)
            if gdelt is not None and not gdelt.empty:
                datasets.append(gdelt)
                logger.info(f"GDELT live: {len(gdelt):,} records loaded")
        else:
            logger.info("GDELT feed disabled (set GDELT_ENABLED=true in .env to enable)")

        # 4. Load NewsAPI live feed (requires NEWSAPI_KEY)
        if settings.NEWSAPI_ENABLED and settings.NEWSAPI_KEY:
            newsapi = self.loader.load_newsapi_live(max_records=100)
            if newsapi is not None and not newsapi.empty:
                datasets.append(newsapi)
                logger.info(f"NewsAPI live: {len(newsapi):,} records loaded")
        else:
            logger.info("NewsAPI feed disabled (set NEWSAPI_ENABLED=true and NEWSAPI_KEY in .env)")

        # 5. Fallback to sample data if real datasets unavailable
        if not datasets:
            logger.warning("No real datasets found. Loading sample data as fallback.")
            sample_path = os.path.join(settings.DATASETS_DIR, "sample_dataset.csv")
            if os.path.exists(sample_path):
                df = pd.read_csv(sample_path)
                df['source_dataset'] = 'SAMPLE'
                datasets.append(df)
            else:
                logger.error("No datasets available. Cannot build pipeline.")
                return None

        # 6. Merge all sources
        df = pd.concat(datasets, ignore_index=True)
        logger.info(f"Merged dataset: {len(df):,} total records from {len(datasets)} source(s)")

        # 7. Clean
        df = self._clean(df)
        logger.info(f"After cleaning: {len(df):,} records")

        # 8. Add engineered features
        df = self._engineer_features(df)

        # 9. Save full dataset to parquet (used by Analytics, Map, Search)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_parquet(output_path, index=False)
        logger.success(f"Unified dataset saved to {output_path} ({len(df):,} records)")

        return df

    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Comprehensive cleaning: missing values, duplicates, invalid coordinates, encoding."""
        logger.info("Cleaning unified dataset...")

        # --- Date cleaning ---
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
            df = df.dropna(subset=['date'])  # must have a valid date

        # --- Deduplicate ---
        before = len(df)
        df = df.drop_duplicates(subset=['date', 'country', 'city', 'attack_type', 'fatalities'], keep='first')
        logger.info(f"Removed {before - len(df)} duplicate records")

        # --- Coordinate cleaning ---
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        # Remove clearly invalid coordinates
        df = df[
            df['latitude'].between(-90, 90) | df['latitude'].isna()
        ]
        df = df[
            df['longitude'].between(-180, 180) | df['longitude'].isna()
        ]
        df['latitude'] = df['latitude'].fillna(0.0)
        df['longitude'] = df['longitude'].fillna(0.0)

        # --- Numeric cleaning ---
        for col in ['fatalities', 'injuries']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).clip(lower=0).astype(int)

        df['property_damage'] = pd.to_numeric(df['property_damage'], errors='coerce').fillna(0.0).clip(lower=0)

        # --- Categorical cleaning ---
        categorical_cols = ['country', 'city', 'region', 'attack_type', 'target_type', 'weapon_type', 'group_name']
        for col in categorical_cols:
            if col in df.columns:
                # Fix encoding issues
                df[col] = df[col].astype(str).str.encode('ascii', errors='replace').str.decode('ascii')
                df[col] = df[col].replace({'nan': 'Unknown', '': 'Unknown', 'None': 'Unknown'})
                df[col] = df[col].fillna('Unknown')

        # --- Summary cleaning ---
        if 'summary' in df.columns:
            df['summary'] = df['summary'].astype(str).fillna('No summary available.')
            df['summary'] = df['summary'].replace({'nan': 'No summary available.', '': 'No summary available.'})
            # Truncate very long summaries
            df['summary'] = df['summary'].str[:1000]

        # --- Region normalization (GTD vs ACLED use different region names) ---
        df['region'] = df['region'].replace({
            'Middle East & North Africa': 'Middle East & North Africa',
            'Middle East': 'Middle East & North Africa',
            'Sub-Saharan Africa': 'Sub-Saharan Africa',
            'Eastern Africa': 'Sub-Saharan Africa',
            'Western Africa': 'Sub-Saharan Africa',
            'Northern Africa': 'Middle East & North Africa',
            'Southern Asia': 'South Asia',
            'South Asia': 'South Asia',
            'Southeast Asia': 'Southeast Asia',
            'East Asia': 'East Asia',
            'Central Asia': 'Central Asia',
            'Eastern Europe': 'Eastern Europe',
            'Western Europe': 'Western Europe',
            'North America': 'North America',
            'Central America & Caribbean': 'Central America & Caribbean',
            'South America': 'South America',
            'Australasia & Oceania': 'Australasia & Oceania',
        })

        logger.info("Data cleaning complete.")
        return df

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features for ML training and analytics."""
        logger.info("Engineering features...")

        # Severity score
        df['severity_score'] = (
            df['fatalities'] * 2.0
            + df['injuries'] * 1.0
            + (df['property_damage'].clip(upper=1_000_000) / 10_000)
        )

        # Threat level from severity
        def classify_threat(score):
            if score >= 20:
                return "HIGH"
            elif score >= 5:
                return "MEDIUM"
            return "LOW"

        df['threat_level'] = df['severity_score'].apply(classify_threat)

        # Year extraction for time-series
        df['year'] = pd.to_datetime(df['date'], errors='coerce').dt.year
        df['month'] = pd.to_datetime(df['date'], errors='coerce').dt.month

        logger.info("Feature engineering complete.")
        return df

    def get_stats(self, df: pd.DataFrame) -> dict:
        """Return summary statistics for dashboard display."""
        if df is None or df.empty:
            return {}

        return {
            "total_incidents": int(len(df)),
            "total_fatalities": int(df['fatalities'].sum()),
            "total_injuries": int(df['injuries'].sum()),
            "countries_covered": int(df['country'].nunique()),
            "regions_covered": int(df['region'].nunique()),
            "date_range_start": str(df['date'].min()),
            "date_range_end": str(df['date'].max()),
            "source_datasets": df['source_dataset'].value_counts().to_dict(),
            "top_countries": df['country'].value_counts().head(10).to_dict(),
            "top_attack_types": df['attack_type'].value_counts().head(10).to_dict(),
            "high_threat_areas": df[df['threat_level'] == 'HIGH']['country'].value_counts().head(5).to_dict(),
            "last_updated": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M UTC'),
        }
