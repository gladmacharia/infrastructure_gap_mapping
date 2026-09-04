import os
import logging
import geopandas as gpd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from infrastructure_gap.config import schema_map,database_url

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

def create_db_engine():
    db_url = database_url
    engine = create_engine(db_url)
    return engine


def enable_postgis_extension(connection):
    sql = text("CREATE EXTENSION IF NOT EXISTS postgis;")
    connection.execute(sql)
    logger.info("PostGIS extension enabled.")

def create_schema(connection, schema):
    sql = text(f"CREATE SCHEMA IF NOT EXISTS {schema};")
    connection.execute(sql)


def create_spatial_index(connection, schema, table_name):
    sql = text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_geom ON {schema}.{table_name} USING GIST (geometry);")
    connection.execute(sql)



def analyze_table(connection, schema, table_name):
    sql = text(f"ANALYZE {schema}.{table_name};")
    connection.execute(sql)




def load_all_layers(projected_datasets):
    successful_tables = []
    failed_tables = []

    engine = create_db_engine()

    with engine.begin() as connection:
        enable_postgis_extension(connection)

    logger.info("Loading datasets...")


    for table_name, gdf in projected_datasets.items():

        logger.info(f"Loading {table_name} into the database...")

        schema = schema_map.get(table_name)

        if schema is None:
            logger.info(f"Schema for {table_name} not found in schema_map. Skipping...")
            continue

        try:
            with engine.begin() as connection:

                create_schema(connection, schema)

                gdf.to_postgis(
                    name = table_name, 
                    con= connection, 
                    schema = schema,
                    if_exists='replace', 
                    index=False,
                    chunksize = 1000)


                create_spatial_index(connection, schema, table_name)

                analyze_table(connection, schema, table_name)

                successful_tables.append(table_name)

                logger.info(f"{table_name} loaded successfully.")

        except Exception as e:
            failed_tables.append({"table": table_name, "error": str(e)})
            logger.error(f"Failed to load {table_name}: {e}")

    if failed_tables:
        logger.info("\nThe following tables failed to load:")
        for table in failed_tables:
            logger.info(f"- {table['table']}: {table['error']}")
