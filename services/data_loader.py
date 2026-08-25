"""
Data Loader — Sentinel AI V2.0
Orchestrates the full data ingestion process:
  1. Run unified data pipeline (GTD + ACLED)
  2. Load into SQLite database
  3. Rebuild FAISS vector index
"""
import pandas as pd
from loguru import logger
from database.sqlite_db import SessionLocal
import database.crud as crud
from services.data_pipeline import DataPipeline


def load_and_process_data(force_rebuild: bool = False) -> bool:
    """
    Load real datasets through the unified pipeline and persist to DB.
    Returns True on success.
    """
    logger.info("Starting Sentinel AI V2.0 data ingestion...")

    pipeline = DataPipeline()
    df = pipeline.run(force_rebuild=force_rebuild)

    if df is None or df.empty:
        logger.error("Data pipeline returned no data.")
        return False

    logger.info(f"Pipeline complete. Ingesting {len(df)} records into database...")

    db = SessionLocal()
    try:
        logger.info("Clearing existing records...")
        crud.delete_all_incidents(db)

        records = df.to_dict(orient='records')
        count = 0
        batch = []
        BATCH_SIZE = 2000

        for record in records:
            incident_data = {
                'date': str(record.get('date', '')),
                'country': str(record.get('country', 'Unknown')),
                'city': str(record.get('city', 'Unknown')),
                'region': str(record.get('region', 'Unknown')),
                'latitude': float(record.get('latitude', 0.0)),
                'longitude': float(record.get('longitude', 0.0)),
                'attack_type': str(record.get('attack_type', 'Unknown')),
                'target_type': str(record.get('target_type', 'Unknown')),
                'weapon_type': str(record.get('weapon_type', 'Unknown')),
                'group_name': str(record.get('group_name', 'Unknown')),
                'fatalities': int(record.get('fatalities', 0)),
                'injuries': int(record.get('injuries', 0)),
                'property_damage': float(record.get('property_damage', 0.0)),
                'summary': str(record.get('summary', 'No summary available.')),
                'source': str(record.get('source_dataset', 'Unknown')),
                'severity_score': float(record.get('severity_score', 0.0)),
            }
            batch.append(incident_data)
            count += 1

            # Batch commit for performance
            if len(batch) >= BATCH_SIZE:
                for item in batch:
                    crud.create_incident(db, item)
                db.commit()
                logger.info(f"Committed {count} records...")
                batch = []

        # Final batch
        if batch:
            for item in batch:
                crud.create_incident(db, item)
            db.commit()

        logger.success(f"Successfully loaded {count} records into the database.")
        return True

    except Exception as e:
        logger.error(f"Database error during load: {e}")
        db.rollback()
        return False
    finally:
        db.close()
