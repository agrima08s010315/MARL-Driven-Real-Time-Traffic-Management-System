import xml.etree.ElementTree as ET
import csv

# Load the tripinfo.xml file
xml_file = "D:\\SUMO\\Test\\tripinfo.xml"
tree = ET.parse(xml_file)
root = tree.getroot()

# Define CSV file name
csv_file = "PPO_timing_results.csv"

# Open CSV file for writing
with open(csv_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    
    # Write headers
    writer.writerow(["Vehicle ID", "Departure Time", "Arrival Time", "Travel Time", "Waiting Time", "Route Length"])
    
    # Extract relevant data from tripinfo.xml
    for trip in root.findall("tripinfo"):
        vehicle_id = trip.get("id")
        depart_time = float(trip.get("depart"))
        arrival_time = float(trip.get("arrival"))
        travel_time = float(trip.get("duration"))
        waiting_time = float(trip.get("waitingTime"))
        route_length = float(trip.get("routeLength"))

        # Write row to CSV
        writer.writerow([vehicle_id, depart_time, arrival_time, travel_time, waiting_time, route_length])

print(f"Data extraction complete! Results saved in {csv_file}")
