# ETL

ETL pipeline for preparing Kenya infrastructure and administrative spatial datasets.

## Data Flow
Extract → Validate → Clean → Transform → Load → Aiven PostGIS

## Data and Schemas
- Counties - Boundaries
- Constituencies - Boundaries
- Wards - Boundaries
- School_facilities - Education
- Health_facilities - Health
- Police_facilities - interior_security
- Roads - transport
- Fiber - utilities
- Electricity - utilities

## CRS
From: EPSG:4326
To: EPSG:32737