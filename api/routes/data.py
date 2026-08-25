"""
Data & Analytics Routes — Sentinel AI V2.0
Provides dataset statistics, analytics, and live data access endpoints.
"""
import os
import pandas as pd
from fastapi import APIRouter, HTTPException
from api.schemas import DataStatsResponse, AnalyticsRequest
from services.data_pipeline import DataPipeline
from utils.config import settings
from loguru import logger

router = APIRouter()

# ── Lazy-loaded dataset ────────────────────────────────────────────────────────
_df_cache = None


def _get_df() -> pd.DataFrame:
    global _df_cache
    if _df_cache is not None:
        return _df_cache

    # Try unified parquet first
    if os.path.exists(settings.UNIFIED_DATASET_PATH):
        try:
            _df_cache = pd.read_parquet(settings.UNIFIED_DATASET_PATH)
            logger.info(f"Data API: Loaded {len(_df_cache)} records from unified dataset")
            return _df_cache
        except Exception as e:
            logger.warning(f"Failed to load parquet: {e}")

    # Fallback to sample CSV
    for path in [
        os.path.join(settings.DATASETS_DIR, "sample_dataset.csv"),
        os.path.join(settings.DATASETS_DIR, "sample_data.csv"),
    ]:
        if os.path.exists(path):
            _df_cache = pd.read_csv(path)
            logger.info(f"Data API: Loaded fallback sample data from {path}")
            return _df_cache

    logger.error("No dataset available for data API")
    return pd.DataFrame()


@router.get("/stats", response_model=DataStatsResponse)
def get_dataset_stats():
    """Return high-level statistics about the loaded intelligence dataset."""
    try:
        df = _get_df()
        if df.empty:
            raise HTTPException(status_code=404, detail="No dataset available")

        pipeline = DataPipeline()
        stats = pipeline.get_stats(df)

        # Ensure all required fields have defaults
        return DataStatsResponse(
            total_incidents=stats.get("total_incidents", 0),
            total_fatalities=stats.get("total_fatalities", 0),
            total_injuries=stats.get("total_injuries", 0),
            countries_covered=stats.get("countries_covered", 0),
            regions_covered=stats.get("regions_covered", 0),
            date_range_start=stats.get("date_range_start", "Unknown"),
            date_range_end=stats.get("date_range_end", "Unknown"),
            source_datasets=stats.get("source_datasets", {}),
            top_countries=stats.get("top_countries", {}),
            top_attack_types=stats.get("top_attack_types", {}),
            high_threat_areas=stats.get("high_threat_areas", {}),
            last_updated=stats.get("last_updated", "Unknown"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analytics")
def get_analytics(request: AnalyticsRequest):
    """
    Return analytics data for a specified chart type.
    Used by the Analytics and Dashboard pages.
    """
    try:
        df = _get_df()
        if df.empty:
            raise HTTPException(status_code=404, detail="No dataset available")

        # Apply filters
        if request.country:
            df = df[df['country'].str.lower() == request.country.lower()]
        if request.region:
            df = df[df['region'].str.lower() == request.region.lower()]
        if request.year_from and 'year' in df.columns:
            df = df[df['year'] >= request.year_from]
        if request.year_to and 'year' in df.columns:
            df = df[df['year'] <= request.year_to]

        chart_type = request.chart_type
        top_n = request.top_n

        if chart_type == "country_ranking":
            data = df['country'].value_counts().head(top_n)
            return {"labels": data.index.tolist(), "values": data.values.tolist()}

        elif chart_type == "fatality_trend":
            if 'year' not in df.columns:
                df['year'] = pd.to_datetime(df['date'], errors='coerce').dt.year
            data = df.groupby('year')['fatalities'].sum().dropna()
            return {"labels": [str(int(y)) for y in data.index.tolist()], "values": data.values.tolist()}

        elif chart_type == "attack_distribution":
            data = df['attack_type'].value_counts().head(top_n)
            return {"labels": data.index.tolist(), "values": data.values.tolist()}

        elif chart_type == "weapon_distribution":
            data = df['weapon_type'].value_counts().head(top_n)
            return {"labels": data.index.tolist(), "values": data.values.tolist()}

        elif chart_type == "target_distribution":
            data = df['target_type'].value_counts().head(top_n)
            return {"labels": data.index.tolist(), "values": data.values.tolist()}

        elif chart_type == "regional_comparison":
            data = df.groupby('region').agg(
                incidents=('date', 'count'),
                fatalities=('fatalities', 'sum'),
                injuries=('injuries', 'sum')
            ).sort_values('incidents', ascending=False).head(top_n)
            return {
                "regions": data.index.tolist(),
                "incidents": data['incidents'].tolist(),
                "fatalities": data['fatalities'].tolist(),
                "injuries": data['injuries'].tolist(),
            }

        elif chart_type == "monthly_trend":
            if 'month' not in df.columns:
                df['month'] = pd.to_datetime(df['date'], errors='coerce').dt.month
            data = df.groupby('month')['fatalities'].sum()
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            return {
                "labels": [months[int(m)-1] for m in data.index if 1 <= int(m) <= 12],
                "values": data.values.tolist()
            }

        elif chart_type == "heatmap_data":
            # For global geographic heatmap — filter to only records with real coordinates
            sample = df[
                df['latitude'].between(-90, 90) &
                df['longitude'].between(-180, 180) &
                (df['latitude'] != 0.0) &   # exclude 0,0 null-island artifacts
                (df['longitude'] != 0.0)
            ]
            sample = sample[['latitude', 'longitude', 'fatalities', 'country', 'attack_type', 'date']].dropna(subset=['latitude', 'longitude'])
            sample = sample.head(10000)  # cap for browser performance
            return {
                "points": sample.to_dict(orient='records')
            }

        elif chart_type == "incident_timeline":
            df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
            df['year_month'] = df['date_parsed'].dt.to_period('M').astype(str)
            data = df.groupby('year_month').size().tail(60)  # last 60 months
            return {"labels": data.index.tolist(), "values": data.values.tolist()}

        else:
            raise HTTPException(status_code=400, detail=f"Unknown chart_type: {chart_type}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reload")
def reload_dataset():
    """Force reload the dataset cache."""
    global _df_cache
    _df_cache = None
    df = _get_df()
    return {"status": "reloaded", "records": len(df)}
