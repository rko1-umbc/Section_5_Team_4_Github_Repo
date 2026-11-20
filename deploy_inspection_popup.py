
from arcgis.gis import GIS
from getpass import getpass
from pathlib import Path
import json
import sys

# Connect to ArcGIS Online
username = input("ArcGIS username: ")
password = getpass("ArcGIS password: ")

gis = GIS("https://www.arcgis.com", username, password)

# Only update our team-owned map
MAP_ID = "c6ebc0e432ca4f569b250899700d1105"
LAYER_ID = "BMP_Inspection_6395"

webmap = gis.content.get(MAP_ID)

if webmap is None:
    raise ValueError("Team Map not found")

if webmap.owner != "rko1_umbc" or webmap.type != "Web Map":
    raise ValueError("Unexpected map owner or item type. Stopping.")

print("Map:", webmap.title)
print("Owner:", webmap.owner)

# Read the Arcade expression from our repository
arcade_path = (
    Path(__file__).resolve().parent
    / "arcade"
    / "inspection_form_link.arcade"
)

new_expression = arcade_path.read_text(encoding="utf-8")

# Read the current web map configuration
data = webmap.get_data()

layer = next(
    layer for layer in data["operationalLayers"]
    if layer.get("id") == LAYER_ID
)

popup = layer["popupInfo"]

# Find our existing inspection routing expression
matches = [
    element for element in popup["popupElements"]
    if element.get("type") == "expression"
    and "Inspection Form:" in
    element.get("expressionInfo", {}).get("expression", "")
]

if len(matches) != 1:
    raise ValueError("Expected exactly one inspection routing expression")

if not new_expression.strip() or "Inspection Form:" not in new_expression:
    raise ValueError("Arcade file is empty or missing the inspection link")

expression_element = matches[0]

# Back up the original map configuration
backup_path = (
    Path(__file__).resolve().parent
    / "team_map_backup.json"
)

backup_path.write_text(
    json.dumps(data, indent=2),
    encoding="utf-8"
)

print("Backup saved:", backup_path.name)

old_expression = expression_element["expressionInfo"]["expression"]

if old_expression == new_expression:
    print("No changes detected. Map already matches repository.")
    sys.exit(0)

# Update only the Arcade expression
expression_element["expressionInfo"]["expression"] = new_expression

print("New Arcade expression loaded successfully.")

# Preview changes unless explicitly deploying
if "--apply" not in sys.argv:
    print("Preview only. No changes sent to ArcGIS.")
    print("Run with --apply to deploy.")
    sys.exit(0)

# Deploy updated web map JSON to ArcGIS Online
success = webmap.update(
    item_properties={
        "text": json.dumps(data)
    }
)

# Verify the saved expression
saved_data = gis.content.get(MAP_ID).get_data()
saved_layer = next(
    item for item in saved_data["operationalLayers"]
    if item.get("id") == LAYER_ID
)
saved_expressions = [
    element["expressionInfo"]["expression"]
    for element in saved_layer["popupInfo"]["popupElements"]
    if element.get("type") == "expression"
]

if new_expression not in saved_expressions:
    raise RuntimeError("Deployment could not be verified")

print("Deployment successful!")
print("Inspection form routing updated in Team Map.")
