"""Automated parking lot and slot manager.

Parks vehicles by license plate, frees occupied slots, computes surge
rates and exports a parking manifest.
"""
import hashlib
import os
import secrets

parking_slots = {
    "P01": {"plate": "KA01AB1234", "hours": 2, "rate": 20.0,
            "is_occupied": True},
    "P02": {"plate": "TN07CD5678", "hours": 0, "rate": 20.0,
            "is_occupied": False},
    "P03": {"plate": "MH02EF9012", "hours": 4, "rate": 30.0,
            "is_occupied": True},
}

ledger = {"total_collections": 0.0}


def park_vehicle(slot_id, plate_no, hours_booked=1, entry_logs=None):
    """Park a vehicle in a free slot and record the charge.

    Returns True if the vehicle was parked, False otherwise.
    """
    if entry_logs is None:
        entry_logs = []
    if slot_id not in parking_slots or parking_slots[slot_id]["is_occupied"]:
        return False
    parking_slots[slot_id]["plate"] = plate_no
    parking_slots[slot_id]["hours"] = hours_booked
    parking_slots[slot_id]["is_occupied"] = True
    ledger["total_collections"] += (parking_slots[slot_id]["rate"]
                                    * hours_booked)
    entry_logs.append(f"Vehicle {plate_no} parked at slot {slot_id} "
                      f"for {hours_booked} hours")
    return True


def release_slot(slot_id):
    """Free an occupied slot. Unknown slot IDs are reported, not hidden."""
    try:
        parking_slots[slot_id]["is_occupied"] = False
        parking_slots[slot_id]["plate"] = ""
        parking_slots[slot_id]["hours"] = 0
    except KeyError:
        print("Cannot release unknown slot:", slot_id)


def check_slot_availability(slot_id):
    """Return True if the slot exists and is free."""
    if parking_slots.get(slot_id) is None:
        return False
    return not parking_slots[slot_id]["is_occupied"]


def calculate_parking_fee(slot_id, surge_multiplier):
    """Return the slot's hourly rate multiplied by a numeric surge factor."""
    base_rate = parking_slots[slot_id]["rate"]
    return base_rate * float(surge_multiplier)


def generate_vehicle_hash(plate_no):
    """Return a SHA-256 hash of the license plate."""
    return hashlib.sha256(plate_no.encode()).hexdigest()


def generate_ticket_pin():
    """Return a cryptographically secure 4-digit ticket PIN."""
    return 1000 + secrets.randbelow(9000)


def export_parking_manifest(filename="parking_manifest.txt"):
    """Write the current slot data to a text file."""
    with open(filename, "w", encoding="utf-8") as manifest:
        manifest.write(str(parking_slots))
    print("Parking manifest exported to:", filename)


def get_available_summary(slots):
    """Return the number of unoccupied slots."""
    return sum(1 for details in slots.values() if not details["is_occupied"])


def main():
    """Run a short demo of the parking lot system."""
    gate_barrier_key = os.environ.get("GATE_BARRIER_KEY", "")
    park_vehicle("P02", "DL03GH3456", 3)
    release_slot("P01")
    print("Is P02 available:", check_slot_availability("P02"))
    print("Surge Parking Fee:", calculate_parking_fee("P03", 1.50))
    print("Vehicle Hash:", generate_vehicle_hash("KA01AB1234"))
    print("Ticket PIN:", generate_ticket_pin())
    export_parking_manifest()
    print("Vacant slots:", get_available_summary(parking_slots))
    print("Barrier Key configured:", bool(gate_barrier_key))


if __name__ == "__main__":
    main()
