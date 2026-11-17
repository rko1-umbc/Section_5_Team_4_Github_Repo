from arcgis.gis import GIS
from getpass import getpass

# Connects to ArcGIS Online using the user's account
username = input("Enter ArcGIS username: ")
password = getpass("Enter ArcGIS password: ")

gis = GIS("https://www.arcgis.com", username, password)

print("Connected as:", gis.users.me.username)


# Searches for the team's shared ArcGIS group
group_name = "New SWM group for Ko_Tran_Ramirez"
groups = gis.groups.search(query="title:SWM", max_groups=100)

group = None

# Checks for the matching group
for item in groups:
    if item.title == group_name:
        group = item
        break


# Lists the Survey123 forms shared with the group
if group is None:
    print("Group not found.")
else:
    print("\nGroup found:", group.title)

    items = group.content()
    form_count = 0

    for item in items:
        if item.type == "Form":
            print("\nSurvey:", item.title)
            print("Item ID:", item.id)
            form_count += 1

    print("\nTotal forms found:", form_count)
