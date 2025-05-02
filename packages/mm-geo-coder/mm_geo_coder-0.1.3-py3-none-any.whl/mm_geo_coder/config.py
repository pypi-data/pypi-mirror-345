# config.py
import os
import importlib.resources

DB_NAME = "mimu_geo_data_public.db"
HIERARCHY_LEVEL = ["state", "district_saz", "township", "town", "ward", "village_tract", "village"]
THRESHOLD = 75
DB_PATH = os.path.join(os.path.dirname(__file__), "database", DB_NAME)

