# Feature columns expected for ML Model
NUMERIC_FEATURES = ['fatalities', 'injuries', 'property_damage', 'severity_score']
CATEGORICAL_FEATURES = ['attack_type', 'target_type', 'weapon_type', 'region', 'country']

THREAT_LEVELS = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3
}

RISK_LEVELS = {
    "LOW": "Routine monitoring. Maintain standard operational posture.",
    "ELEVATED": "Increased surveillance recommended. Review area intelligence.",
    "HIGH": "Immediate strategic review required. Escalate to command.",
    "CRITICAL": "Imminent threat — active response required. Deploy countermeasures."
}

# GTD column mapping (raw → normalized)
GTD_COLUMN_MAP = {
    'iyear': 'year',
    'imonth': 'month',
    'iday': 'day',
    'country_txt': 'country',
    'region_txt': 'region',
    'city': 'city',
    'latitude': 'latitude',
    'longitude': 'longitude',
    'attacktype1_txt': 'attack_type',
    'targtype1_txt': 'target_type',
    'weaptype1_txt': 'weapon_type',
    'gname': 'group_name',
    'nkill': 'fatalities',
    'nwound': 'injuries',
    'propvalue': 'property_damage',
    'summary': 'summary',
}

# ACLED column mapping (raw → normalized)
ACLED_COLUMN_MAP = {
    'event_date': 'date',
    'country': 'country',
    'region': 'region',
    'location': 'city',
    'latitude': 'latitude',
    'longitude': 'longitude',
    'event_type': 'attack_type',
    'sub_event_type': 'target_type',
    'actor1': 'group_name',
    'fatalities': 'fatalities',
    'notes': 'summary',
    'source': 'source',
}

# Attack type classifications for risk scoring
HIGH_RISK_ATTACKS = [
    'Bombing/Explosion', 'Armed Assault', 'Assassination',
    'Explosions/Remote violence', 'Battles'
]

ATTACK_RISK_WEIGHTS = {
    'Bombing/Explosion': 3.0,
    'Explosions/Remote violence': 3.0,
    'Armed Assault': 2.5,
    'Battles': 2.5,
    'Assassination': 2.0,
    'Hostage Taking (Kidnapping)': 2.0,
    'Hostage Taking (Barricade Incident)': 1.5,
    'Facility/Infrastructure Attack': 1.5,
    'Riots': 1.0,
    'Protests': 0.5,
    'Unknown': 1.0,
}

# High-risk regions for monitoring priority boost
HIGH_RISK_REGIONS = [
    'Middle East & North Africa',
    'South Asia',
    'Sub-Saharan Africa',
    'Eastern Europe',
]

# Source dataset identifiers
SOURCE_GTD = "GTD"
SOURCE_ACLED = "ACLED"
SOURCE_LIVE = "LIVE_INTELLIGENCE"
