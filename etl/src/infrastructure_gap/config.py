from pathlib import Path
import os
from dotenv import load_dotenv

base_dir = Path(__file__).resolve().parents[3]


geopackage_path = base_dir/"data"/"kenyan_data.gpkg"


columns_to_keep = {
    "counties":["COUNTRY","NAME_1", "TYPE_1","CC_1","pop_sum", "geometry"],
    "constituencies":["COUNTRY","NAME_1", "NAME_2", "CC_2", "TYPE_2","pop_sum","geometry"],
    "wards":["COUNTRY","NAME_1", "NAME_2", "NAME_3", "CC_3", "TYPE_3","pop_sum","geometry"],
    "schools_points":["id","name", "amenity","operator_type","capacity_persons", "source","geometry"],
    "schools_polygons":["id","name", "amenity","operator_type","capacity_persons", "source","geometry"],
    "health_points": ["id","name","amenity", "healthcare", "name_latin", "geometry"],
    "health_polygons": ["id","name","amenity", "healthcare", "name_latin", "geometry"],
    "police_points": ["id","name", "amenity","operator", "operator:type", "operational_status", "addr:county","addr:city", "phone","source","geometry"],
    "police_polygons": ["id","name", "amenity","operator", "operator:type", "operational_status", "addr:county","addr:city", "phone","source","geometry"],
    "roads": ["id","name","name_en","highway","surface","smoothness","width","lanes","oneway","bridge","layer","geometry"],
    "fiber": ["operator","Shape_Leng","geometry"],
    "electricity": ["COUNTRY","CNTRY_NAME","VOLTAGE_KV","FROM_NM","TO_NM","STATUS","SOURCES","geometry"]
}

rename_columns = {
    "counties": {
        "COUNTRY": "country",
        "NAME_1": "county_name",
        "TYPE_1": "type",
        "CC_1": "county_code"
    },
    "constituencies": {
        "COUNTRY": "country",
        "NAME_1": "county_name",
        "NAME_2": "constituency_name",
        "CC_2": "constituency_code",
        "TYPE_2": "constituency_type"
    },
    "wards": {
        "COUNTRY": "country",
        "NAME_1": "county_name",
        "NAME_2": "constituency_name",
        "NAME_3": "ward_name",
        "CC_3": "ward_code",
        "TYPE_3": "ward_type"
    },
    "schools_facilities":{
        "id" : "school_id",
    },

    "health_facilities":{
        "id" : "hospital_id",
    },
    "police_facilities":{
        "id" : "police_id",
    },

    "fiber": {
        "fid" : "fiber_id",
        "Shape_Leng" : "shape_length"
    },

    "electricity":{
        "COUNTRY": "country",
        "CNTRY_NAME": "country_name",
        "VOLTAGE_KV": "voltage_kv",
        "FROM_NM": "from",
        "TO_NM": "to",
        "STATUS": "status",
        "SOURCES": "source"
    }

}


load_dotenv(base_dir/".env")

HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
NAME = os.getenv("DB_NAME")
SSL_MODE = os.getenv("DB_SSLMODE", "require")

database_url = (f"postgresql+psycopg://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}?sslmode={SSL_MODE}")



target_crs = 32737

schema_map = {
    "counties": "boundaries",
    "constituencies": "boundaries",
    "wards": "boundaries",
    "roads": "transport",
    "health_facilities": "health",
    "police_facilities": "interior_security",
    "schools_facilities": "education",
    "fiber": "utilities",
    "electricity": "utilities"

}

