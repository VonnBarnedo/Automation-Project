import json
import socket
import sys
from datetime import datetime

INVENTORY_FILE = "inventory.json"
OUTPUT_FILE = "output.json"

def load_inventory(path):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("ERROR:", path, "not found.")
    except json.JSONDecodeError:
        print("ERROR:", path, "has invalid JSON.")
    return None

def live_check(ip):
    try:
        connection = socket.create_connection((ip, 22), timeout=2)
        connection.close()
        return "UP"
    except OSError:
        return "DOWN"

def check_device(device, live):
    try:
        if live:
            return live_check(device["ip"])
        return device["simulated_status"].upper()
    except KeyError:
        print("WARNING: A device entry is missing a field.")
        return "DOWN"

def main():
    live = "--live" in sys.argv

    devices = load_inventory(INVENTORY_FILE)
    if devices is None:
        return

    if live:
        print("=== Network Check (LIVE) ===")
    else:
        print("=== Network Check (SIMULATED) ===")

    print("Hostname        IP Address       Status")
    print("-" * 40)

    results = []
    for device in devices:
        status = check_device(device, live)
        print(device["hostname"].ljust(15), device["ip"].ljust(16), status)

        results.append({
            "hostname": device["hostname"],
            "ip": device["ip"],
            "status": status,
            "checked_at": datetime.now().isoformat(timespec="seconds"),
        })

    up_count = 0
    for result in results:
        if result["status"] == "UP":
            up_count = up_count + 1
    print("\n", up_count, "of", len(results), "devices are UP.")

    try:
        with open(OUTPUT_FILE, "w") as file:
            json.dump(results, file, indent=2)
        print("Results saved to", OUTPUT_FILE)
    except OSError as error:
        print("ERROR: Could not save results:", error)

main()
