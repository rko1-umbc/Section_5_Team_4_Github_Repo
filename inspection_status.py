from arcgis.gis import GIS
from getpass import getpass

# Take the user's username and password pair
username = input("ArcGIS Username:")
password = getpass("ArcGIS Password:")

# Connect using the arcGIS credentials
gis = GIS("https://arcgis.com", username, password)

# Get the BMP inspection layer
item = gis.content.get("03653a4e8cdd4a30a2dd5050672dd926")

if item is None or not item.layers:
    raise RuntimeError("BMP Inspection layer not accessible.")

layer = item.layers[0]

# Retrive a small sample of records
features = layer.query(where="1=1", out_fields="*", return_geometry=False, result_record_count=5)

# Display the available inspecton information
for i, feature in enumerate(features.features, start=1):
    print(f"\n---- Facility {i} ---")

    for field, value in feature.attributes.item():
        print(f"{field}: {value}")