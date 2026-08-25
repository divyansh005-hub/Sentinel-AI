"""
Dataset Loader — Sentinel AI V2.0
Unified abstraction for loading GTD, ACLED, GDELT, and NewsAPI datasets.
Never hardcodes filenames — discovers files from configured directories.
Handles full GTD database (200K+ records) with memory-efficient loading.
"""
import os
import glob
import requests
import io
import zipfile
import pandas as pd
from loguru import logger
from typing import Optional
from utils.config import settings
from utils.constants import GTD_COLUMN_MAP, ACLED_COLUMN_MAP, SOURCE_GTD, SOURCE_ACLED, SOURCE_LIVE


class DatasetLoader:
    """
    Dataset abstraction layer supporting GTD, ACLED, GDELT, and NewsAPI.
    Discovers dataset files automatically from configured directories.
    Designed to be extended with new sources without modifying the pipeline.
    """

    def __init__(self):
        self.gtd_dir = settings.GTD_DIR
        self.acled_dir = settings.ACLED_DIR

    # ─────────────────────────────────────────────────────────────
    # File Discovery
    # ─────────────────────────────────────────────────────────────
    def _discover_files(self, directory: str, extensions=("*.xlsx", "*.csv")) -> list:
        """Discover all dataset files in a directory regardless of filename."""
        files = []
        for ext in extensions:
            files.extend(glob.glob(os.path.join(directory, ext)))
        return sorted(files)

    # ─────────────────────────────────────────────────────────────
    # GTD Loading — Full Database (1970–2022+)
    # ─────────────────────────────────────────────────────────────
    def load_gtd(self) -> Optional[pd.DataFrame]:
        """
        Load and normalize Global Terrorism Database (GTD) data.
        Loads ALL discovered GTD files (full history + supplements).
        """
        files = self._discover_files(self.gtd_dir)
        if not files:
            logger.warning(f"No GTD files found in {self.gtd_dir}")
            return None

        # Sort: larger files first (full DB), smaller supplement files after
        files = sorted(files, key=lambda f: os.path.getsize(f), reverse=True)

        dfs = []
        total_raw = 0
        for fpath in files:
            fname = os.path.basename(fpath)
            fsize_mb = os.path.getsize(fpath) / (1024 * 1024)
            logger.info(f"Loading GTD file: {fname} ({fsize_mb:.1f} MB)")
            try:
                if fpath.endswith(".xlsx"):
                    df = pd.read_excel(fpath, engine='openpyxl')
                else:
                    df = pd.read_csv(fpath, low_memory=False, encoding='latin-1')

                logger.info(f"  -> Loaded {len(df):,} raw records from {fname}")
                total_raw += len(df)
                dfs.append(df)
            except Exception as e:
                logger.error(f"Failed to load GTD file {fpath}: {e}")

        if not dfs:
            return None

        # Concatenate all GTD files
        df = pd.concat(dfs, ignore_index=True)
        logger.info(f"GTD raw total: {total_raw:,} records across {len(files)} file(s)")

        # Normalize to unified schema
        df = self._normalize_gtd(df)

        # Deduplicate across files (overlap between full DB and supplement)
        before = len(df)
        df = df.drop_duplicates(
            subset=['date', 'country', 'city', 'attack_type', 'fatalities'],
            keep='first'
        )
        logger.info(f"GTD deduplication: {before:,} -> {len(df):,} records")

        df['source_dataset'] = SOURCE_GTD
        logger.success(f"GTD loaded: {len(df):,} records")
        return df

    def _normalize_gtd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map GTD raw columns to unified schema."""
        # GTD has both numeric ID columns (country, region, attacktype1…) and
        # human-readable text columns (country_txt, region_txt, attacktype1_txt…).
        # Drop the numeric ID columns FIRST so the rename of the _txt columns
        # doesn't get overwritten.
        numeric_id_cols = [
            'country', 'region',
            'attacktype1', 'attacktype2', 'attacktype3',
            'targtype1', 'targtype2', 'targtype3',
            'weaptype1', 'weaptype2', 'weaptype3',
            'weapsubtype1', 'weapsubtype2', 'weapsubtype3',
        ]
        cols_to_drop = [c for c in numeric_id_cols if c in df.columns]
        df = df.drop(columns=cols_to_drop)

        rename_map = {k: v for k, v in GTD_COLUMN_MAP.items() if k in df.columns}
        df = df.rename(columns=rename_map)

        # Build date from year/month/day columns
        if 'year' in df.columns:
            df['month'] = pd.to_numeric(df.get('month', 1), errors='coerce').fillna(1).astype(int)
            df['day'] = pd.to_numeric(df.get('day', 1), errors='coerce').fillna(1).astype(int)
            df['month'] = df['month'].clip(1, 12)
            df['day'] = df['day'].clip(1, 28)
            df['date'] = pd.to_datetime(
                df[['year', 'month', 'day']].rename(
                    columns={'year': 'year', 'month': 'month', 'day': 'day'}
                ),
                errors='coerce'
            ).dt.strftime('%Y-%m-%d')

        return self._ensure_unified_schema(df)


    # ─────────────────────────────────────────────────────────────
    # ACLED Loading — Regional Aggregated Files
    # ─────────────────────────────────────────────────────────────
    def load_acled(self) -> Optional[pd.DataFrame]:
        """Load and normalize ACLED data (regional aggregated files)."""
        files = self._discover_files(self.acled_dir)
        if not files:
            logger.warning(f"No ACLED files found in {self.acled_dir}")
            return None

        # Load only per-event regional files, skip summary stat files
        regional_files = [
            f for f in files
            if any(region in os.path.basename(f) for region in [
                'Africa', 'Asia-Pacific', 'Europe', 'Latin-America', 'Middle-East', 'US-and-Canada'
            ])
            and 'number_of' not in os.path.basename(f).lower()
        ]

        if not regional_files:
            regional_files = [f for f in files if 'number_of' not in os.path.basename(f).lower()]

        if not regional_files:
            logger.warning("No valid ACLED regional event files found")
            return None

        dfs = []
        total_raw = 0
        for fpath in regional_files:
            fname = os.path.basename(fpath)
            logger.info(f"Loading ACLED file: {fname}")
            try:
                if fpath.endswith(".xlsx"):
                    df = pd.read_excel(fpath, engine='openpyxl')
                else:
                    df = pd.read_csv(fpath, low_memory=False, encoding='utf-8')

                logger.info(f"  -> Loaded {len(df):,} raw records from {fname}")
                total_raw += len(df)
                dfs.append(df)
            except Exception as e:
                logger.error(f"Failed to load ACLED file {fpath}: {e}")

        if not dfs:
            return None

        df = pd.concat(dfs, ignore_index=True)
        logger.info(f"ACLED raw total: {total_raw:,} records")
        df = self._normalize_acled(df)
        df['source_dataset'] = SOURCE_ACLED
        logger.success(f"ACLED loaded: {len(df):,} records")
        return df

    def _normalize_acled(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map ACLED raw columns to unified schema."""
        rename_map = {k: v for k, v in ACLED_COLUMN_MAP.items() if k in df.columns}
        df = df.rename(columns=rename_map)

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')

        if 'weapon_type' not in df.columns:
            df['weapon_type'] = 'Unknown'

        if 'actor1' in df.columns and 'group_name' not in df.columns:
            df['group_name'] = df['actor1']

        return self._ensure_unified_schema(df)

    # ─────────────────────────────────────────────────────────────
    # GDELT Live Feed — Free, No API Key Required
    # ─────────────────────────────────────────────────────────────
    def load_gdelt_live(self, max_records: int = 5000) -> Optional[pd.DataFrame]:
        """
        Load recent conflict events from GDELT 2.0 (free, no API key).
        Pulls the latest 15-minute event export.
        Filters for conflict/violence-relevant CAMEO event codes.
        """
        logger.info("Fetching GDELT live intelligence feed...")
        try:
            master_url = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"
            resp = requests.get(master_url, timeout=30)
            resp.raise_for_status()

            lines = resp.text.strip().split('\n')
            export_line = next((l for l in lines if 'export.CSV' in l), None)
            if not export_line:
                logger.warning("GDELT: Could not find export file URL")
                return None

            parts = export_line.split(' ')
            if len(parts) < 3:
                logger.warning("GDELT: Unexpected master file format")
                return None

            export_url = parts[2].strip()
            logger.info(f"GDELT: Downloading latest export from {export_url}")

            resp2 = requests.get(export_url, timeout=60, stream=True)
            resp2.raise_for_status()

            with zipfile.ZipFile(io.BytesIO(resp2.content)) as z:
                csv_name = z.namelist()[0]
                with z.open(csv_name) as f:
                    gdelt_cols = self._gdelt_columns()
                    df = pd.read_csv(f, sep='\t', header=None,
                                     names=gdelt_cols, low_memory=False)

            logger.info(f"GDELT: Retrieved {len(df):,} raw events")

            # Filter: CAMEO root codes 14=Protest, 15=Force Posture, 17=Coerce,
            # 18=Assault, 19=Fight, 20=Mass Violence
            conflict_codes = ['14', '15', '17', '18', '19', '20']
            if 'EventRootCode' in df.columns:
                df = df[df['EventRootCode'].astype(str).isin(conflict_codes)]

            logger.info(f"GDELT: {len(df):,} conflict-relevant events after filtering")

            if len(df) > max_records:
                df = df.head(max_records)

            df = self._normalize_gdelt(df)
            df['source_dataset'] = SOURCE_LIVE
            logger.success(f"GDELT live feed loaded: {len(df):,} records")
            return df

        except requests.exceptions.RequestException as e:
            logger.warning(f"GDELT feed unavailable (network error): {e}")
            return None
        except Exception as e:
            logger.warning(f"GDELT feed error: {e}")
            return None

    def _gdelt_columns(self) -> list:
        """Return GDELT 2.0 column names (61 columns, no header in file)."""
        return [
            'GlobalEventID', 'Day', 'MonthYear', 'Year', 'FractionDate',
            'Actor1Code', 'Actor1Name', 'Actor1CountryCode', 'Actor1KnownGroupCode',
            'Actor1EthnicCode', 'Actor1Religion1Code', 'Actor1Religion2Code',
            'Actor1Type1Code', 'Actor1Type2Code', 'Actor1Type3Code',
            'Actor2Code', 'Actor2Name', 'Actor2CountryCode', 'Actor2KnownGroupCode',
            'Actor2EthnicCode', 'Actor2Religion1Code', 'Actor2Religion2Code',
            'Actor2Type1Code', 'Actor2Type2Code', 'Actor2Type3Code',
            'IsRootEvent', 'EventCode', 'EventBaseCode', 'EventRootCode',
            'QuadClass', 'GoldsteinScale', 'NumMentions', 'NumSources',
            'NumArticles', 'AvgTone', 'Actor1Geo_Type', 'Actor1Geo_FullName',
            'Actor1Geo_CountryCode', 'Actor1Geo_ADM1Code', 'Actor1Geo_ADM2Code',
            'Actor1Geo_Lat', 'Actor1Geo_Long', 'Actor1Geo_FeatureID',
            'Actor2Geo_Type', 'Actor2Geo_FullName', 'Actor2Geo_CountryCode',
            'Actor2Geo_ADM1Code', 'Actor2Geo_ADM2Code', 'Actor2Geo_Lat',
            'Actor2Geo_Long', 'Actor2Geo_FeatureID', 'ActionGeo_Type',
            'ActionGeo_FullName', 'ActionGeo_CountryCode', 'ActionGeo_ADM1Code',
            'ActionGeo_ADM2Code', 'ActionGeo_Lat', 'ActionGeo_Long',
            'ActionGeo_FeatureID', 'DATEADDED', 'SOURCEURL'
        ]

    def _normalize_gdelt(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map GDELT 2.0 columns to unified Sentinel schema."""
        cameo_map = {
            '14': 'Protest',
            '15': 'Armed Threat/Force Posture',
            '17': 'Coercion/Sanctions',
            '18': 'Armed Assault',
            '19': 'Armed Conflict/Fight',
            '20': 'Mass Violence/Atrocity'
        }

        normalized = pd.DataFrame()

        if 'Day' in df.columns:
            normalized['date'] = pd.to_datetime(
                df['Day'].astype(str), format='%Y%m%d', errors='coerce'
            ).dt.strftime('%Y-%m-%d')
        else:
            normalized['date'] = None

        normalized['country'] = df.get('ActionGeo_CountryCode', 'Unknown').fillna('Unknown')
        normalized['city'] = df.get('ActionGeo_FullName', 'Unknown').fillna('Unknown')
        normalized['region'] = df.get('ActionGeo_CountryCode', 'Unknown').fillna('Unknown')
        normalized['latitude'] = pd.to_numeric(df.get('ActionGeo_Lat', 0), errors='coerce').fillna(0.0)
        normalized['longitude'] = pd.to_numeric(df.get('ActionGeo_Long', 0), errors='coerce').fillna(0.0)

        if 'EventRootCode' in df.columns:
            normalized['attack_type'] = df['EventRootCode'].astype(str).map(cameo_map).fillna('Political Violence')
        else:
            normalized['attack_type'] = 'Political Violence'

        normalized['group_name'] = df.get('Actor1Name', 'Unknown').fillna('Unknown')
        normalized['target_type'] = df.get('Actor2Name', 'Civilian/Government').fillna('Civilian/Government')
        normalized['weapon_type'] = 'Unknown'
        normalized['fatalities'] = 0
        normalized['injuries'] = 0

        # Use Goldstein scale (inverted) as a damage proxy
        if 'GoldsteinScale' in df.columns:
            goldstein = pd.to_numeric(df['GoldsteinScale'], errors='coerce').fillna(0)
            normalized['property_damage'] = ((goldstein * -1).clip(lower=0) * 1000).astype(float)
        else:
            normalized['property_damage'] = 0.0

        source_urls = df.get('SOURCEURL', pd.Series(['Unknown'] * len(df))).fillna('Unknown').astype(str)
        normalized['summary'] = (
            'GDELT Intelligence Event: ' +
            normalized['attack_type'].astype(str) + ' in ' +
            normalized['city'].astype(str) + '. Source: ' +
            source_urls.str[:200]
        )

        normalized['source_dataset'] = SOURCE_LIVE
        return self._ensure_unified_schema(normalized)

    # ─────────────────────────────────────────────────────────────
    # NewsAPI Live Feed — Requires NEWSAPI_KEY in .env
    # ─────────────────────────────────────────────────────────────
    def load_newsapi_live(self, max_records: int = 100) -> Optional[pd.DataFrame]:
        """
        Load recent security/conflict headlines from NewsAPI.
        Requires NEWSAPI_KEY to be set in .env.
        """
        api_key = settings.NEWSAPI_KEY
        if not api_key:
            logger.warning("NewsAPI: No NEWSAPI_KEY configured in .env. Skipping.")
            return None

        logger.info("Fetching NewsAPI live intelligence feed...")
        try:
            query = (
                'terrorism OR "armed conflict" OR "military attack" OR '
                '"suicide bombing" OR "militant" OR "insurgency" OR '
                '"airstrike" OR "rebel attack"'
            )
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': min(max_records, 100),
                'apiKey': api_key,
            }
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            articles = data.get('articles', [])
            if not articles:
                logger.warning("NewsAPI: No articles returned")
                return None

            logger.info(f"NewsAPI: Retrieved {len(articles)} articles")
            df = self._normalize_newsapi(articles)
            df['source_dataset'] = SOURCE_LIVE
            logger.success(f"NewsAPI live feed loaded: {len(df)} records")
            return df

        except requests.exceptions.RequestException as e:
            logger.warning(f"NewsAPI feed unavailable: {e}")
            return None
        except Exception as e:
            logger.warning(f"NewsAPI feed error: {e}")
            return None

    def _normalize_newsapi(self, articles: list) -> pd.DataFrame:
        """Convert NewsAPI articles to unified Sentinel schema."""
        rows = []
        for art in articles:
            title = art.get('title', '') or ''
            description = art.get('description', '') or ''
            content = art.get('content', '') or ''
            text = f"{title}. {description}. {content}"

            rows.append({
                'date': pd.to_datetime(art.get('publishedAt', ''), errors='coerce'),
                'country': 'Unknown',
                'city': 'Unknown',
                'region': 'Unknown',
                'latitude': 0.0,
                'longitude': 0.0,
                'attack_type': self._classify_from_text(text),
                'target_type': 'Unknown',
                'weapon_type': 'Unknown',
                'group_name': 'Unknown',
                'fatalities': 0,
                'injuries': 0,
                'property_damage': 0.0,
                'summary': text[:800],
                'source_dataset': SOURCE_LIVE,
            })

        df = pd.DataFrame(rows)
        if not df.empty and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
        return self._ensure_unified_schema(df)

    def _classify_from_text(self, text: str) -> str:
        """Simple keyword-based attack type classification from news text."""
        t = text.lower()
        if any(k in t for k in ['bomb', 'blast', 'explosion', 'ied']):
            return 'Bombing/Explosion'
        if any(k in t for k in ['shooting', 'gunfire', 'armed assault', 'gunman']):
            return 'Armed Assault'
        if any(k in t for k in ['airstrike', 'air strike', 'drone strike', 'missile']):
            return 'Armed Assault'
        if any(k in t for k in ['kidnap', 'hostage', 'abduct']):
            return 'Hostage Taking (Kidnapping)'
        if any(k in t for k in ['assassin', 'killed', 'murder']):
            return 'Assassination'
        if any(k in t for k in ['riot', 'protest', 'demonstration']):
            return 'Protest/Riot'
        if any(k in t for k in ['battle', 'clash', 'offensive']):
            return 'Armed Conflict/Fight'
        return 'Political Violence'

    # ─────────────────────────────────────────────────────────────
    # Unified Schema Enforcement
    # ─────────────────────────────────────────────────────────────
    def _ensure_unified_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure all required columns exist. Strips extra columns, removes duplicates."""
        unified_columns = {
            'date': None,
            'country': 'Unknown',
            'city': 'Unknown',
            'region': 'Unknown',
            'latitude': 0.0,
            'longitude': 0.0,
            'attack_type': 'Unknown',
            'target_type': 'Unknown',
            'weapon_type': 'Unknown',
            'group_name': 'Unknown',
            'fatalities': 0,
            'injuries': 0,
            'property_damage': 0.0,
            'summary': '',
            'source_dataset': 'Unknown',
        }

        for col, default in unified_columns.items():
            if col not in df.columns:
                df[col] = default

        df = df[list(unified_columns.keys())]
        return df.loc[:, ~df.columns.duplicated()].copy()
