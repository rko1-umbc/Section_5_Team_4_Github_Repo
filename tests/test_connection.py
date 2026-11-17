
from arcgis.gis import GIS
from getpass import getpass

# Asks for ArcGIS login information
username = input("ArcGIS username: ")
password = getpass("ArcGIS password: ")

# Connects to ArcGIS Online
gis = GIS("https://www.arcgis.com", username, password)

# Checks the connection
if gis.users.me:
    print("Connected as:", gis.users.me.username)
else:
    print("Connection failed.")

# Gets the ArcGIS item using its ID
item = gis.content.get("03653a4e8cdd4a30a2dd5050672dd926")

# Displays information about the item
if item:
    print("Item title:", item.title)
    print("Item type:", item.type)
    print("Item owner:", item.owner)
else:
    print("Item not found or access denied.")

# Lists the feature layers in BMP Inspection
for i, layer in enumerate(item.layers):
    print(f"Layer {i}: {layer.properties.name}")

# Lists any standalone tables
for i, table in enumerate(item.tables):
    print(f"Table {i}: {table.properties.name}")
layer = item.layers[0]

for field in layer.properties.fields:
    print(field.name, "-", field.type)
