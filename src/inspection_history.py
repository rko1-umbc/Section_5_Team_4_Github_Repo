
from arcgis.gis import GIS
from getpass import getpass
from pathlib import Path
from datetime import datetime, timezone
import csv
import json


# Connects to ArcGIS Online
username = input("Enter ArcGIS username: ")
password = getpass("Enter ArcGIS password: ")

gis = GIS("https://www.arcgis.com", username, password)
print("Connected as:", gis.users.me.username)


# Finds the team's shared group
group_name = "New SWM group for Ko_Tran_Ramirez"
groups = gis.groups.search(query="title:SWM", max_groups=100)

group = None

for item in groups:
    if item.title == group_name:
        group = item
        break

if group is None:
    raise SystemExit("Shared group not found.")

print("\nGroup found:", group.title)


# Lists the four forms required for inspection history
form_names = [
    "Permeable Pavement",
    "Rainwater Harvesting Form",
    "Vegetated Practices (Micro-bioretention)",
    "Vegetated Roofs (Green Roofs)"
]

forms = []

for item in group.content():
    if item.type == "Form" and item.title in form_names:
        forms.append(item)

# Checks that all four forms are accessible
found_names = [form.title for form in forms]

for name in form_names:
    if name not in found_names:
        raise SystemExit("Missing form: " + name)


# Finds a field value using possible field names
def get_value(attributes, possible_names):
    for name in possible_names:
        for field in attributes:
            if field.lower() == name.lower():
                return attributes[field]
    return ""


# Converts ArcGIS date values into readable dates
def format_date(value):
    if isinstance(value, (int, float)) and value > 100000000000:
        date = datetime.fromtimestamp(
            value / 1000, tz=timezone.utc
        )
        return date.strftime("%Y-%m-%d")

    if value is None:
        return ""

    return str(value)


# Creates a list for all inspection records
inspection_history = []
errors = []


# Retrieves submitted records from each survey
for form in forms:
    print("\nReading:", form.title)

    try:
        # Finds the feature service linked to the form
        services = form.related_items(
            "Survey2Service", "forward"
        )

        if not services:
            raise ValueError("No results service found")

        service = services[0]

        # Finds the main layer containing survey responses
        layers = list(service.layers)

        if not layers:
            layers = list(service.tables)

        if not layers:
            raise ValueError("No readable layer found")

        layer = layers[0]

        # Retrieves all available inspection records
        results = layer.query(
            where="1=1",
            out_fields="*",
            return_geometry=False,
            return_all_records=True,
            as_df=False
        )

        print("Records found:", len(results.features))

        # Displays field names for checking the mappings
        fields = [field["name"] for field in layer.properties.fields]
        print("Available fields:", fields)

        for feature in results.features:
            attributes = feature.attributes

            # Gets values shared across different survey forms
            record_id = get_value(
                attributes, ["GlobalID", "OBJECTID"]
            )

            tracking_no = get_value(
                attributes, ["SWM_Tracking_No"]
            )

            bmp_name = get_value(
                attributes, ["BMP_Name", "BMPName"]
            )

            inspection_date = get_value(
                attributes,
                ["Inspection_Date", "InspectionDate",
                 "CreationDate", "created_date"]
            )

            status = get_value(
                attributes,
                ["Inspection_Status", "Status"]
            )

            # Creates a consistent record for inspection history
            record = {
                "record_key": form.id + ":" + str(record_id),
                "form_type": form.title,
                "tracking_no": tracking_no,
                "bmp_name": bmp_name,
                "inspection_date": format_date(inspection_date),
                "status": status,
                "source_form_id": form.id,
                "answers": attributes
            }

            inspection_history.append(record)

    except Exception as error:
        errors.append(form.title + ": " + str(error))
        print("Error:", error)


# Checks that every form was processed successfully
if errors:
    print("\nSome surveys could not be read:")

    for error in errors:
        print(error)

    raise SystemExit("Inspection history was not exported.")


# Creates a local folder for the combined inspection data
output_folder = Path(__file__).resolve().parent.parent / "data"
output_folder.mkdir(exist_ok=True)


# Creates a CSV file for reviewing the combined records
csv_path = output_folder / "inspection_history.csv"

columns = [
    "record_key",
    "form_type",
    "tracking_no",
    "bmp_name",
    "inspection_date",
    "status",
    "source_form_id"
]

with open(csv_path, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()

    for record in inspection_history:
        row = {column: record[column] for column in columns}
        writer.writerow(row)


# Creates a JSON file preserving all survey answers
json_path = output_folder / "inspection_history.json"

with open(json_path, "w", encoding="utf-8") as file:
    json.dump(inspection_history, file, indent=4, default=str)


# Displays the completed export information
print("\nInspection history export complete!")
print("Total records:", len(inspection_history))
print("CSV file:", csv_path)
print("JSON file:", json_path)
