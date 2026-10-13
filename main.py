import sqlite3


# Database connection

def get_connection():
    conn = sqlite3.connect("flight_management.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# Flight viewing functions

def view_all_flights():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            f.flight_id,
            f.flight_number,
            o.airport_code,
            d.airport_code,
            f.departure_datetime,
            f.arrival_datetime,
            f.gate,
            f.status
        FROM Flight f
        JOIN Destination o
            ON f.origin_id = o.destination_id
        JOIN Destination d
            ON f.destination_id = d.destination_id
        ORDER BY f.departure_datetime
    """)

    flights = cursor.fetchall()
    conn.close()

    display_flights(flights)


def display_flights(flights):
    row_format = "{:<4} {:<8} {:<8} {:<12} {:<18} {:<18} {:<8} {:<12}"

    print("\nFLIGHT SCHEDULE")
    print("-" * 95)

    print(row_format.format(
        "ID",
        "Flight",
        "Origin",
        "Destination",
        "Departure",
        "Arrival",
        "Gate",
        "Status"
    ))

    print("-" * 95)

    for flight in flights:
        flight_id, flight_number, origin, destination, departure, arrival, gate, status = flight

        if gate is None:
            gate = "TBC"

        print(row_format.format(
            flight_id,
            flight_number,
            origin,
            destination,
            departure,
            arrival,
            gate,
            status
        ))


def view_flights_by_status():
    status = input("Enter flight status: ").strip().title()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            f.flight_id,
            f.flight_number,
            o.airport_code,
            d.airport_code,
            f.departure_datetime,
            f.arrival_datetime,
            f.gate,
            f.status
        FROM Flight f
        JOIN Destination o
            ON f.origin_id = o.destination_id
        JOIN Destination d
            ON f.destination_id = d.destination_id
        WHERE f.status = ?
        ORDER BY f.departure_datetime
    """, (status,))

    flights = cursor.fetchall()
    conn.close()

    if flights:
        display_flights(flights)
    else:
        print("\nNo flights found with that status.")


def view_flights_by_destination():
    destination = input("Enter destination airport code: ").strip().upper()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            f.flight_id,
            f.flight_number,
            o.airport_code,
            d.airport_code,
            f.departure_datetime,
            f.arrival_datetime,
            f.gate,
            f.status
        FROM Flight f
        JOIN Destination o
            ON f.origin_id = o.destination_id
        JOIN Destination d
            ON f.destination_id = d.destination_id
        WHERE d.airport_code = ?
        ORDER BY f.departure_datetime
    """, (destination,))

    flights = cursor.fetchall()
    conn.close()

    if flights:
        display_flights(flights)
    else:
        print("\nNo flights found for that destination.")


def view_flights_by_date():
    departure_date = input("Enter departure date (YYYY-MM-DD): ").strip()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            f.flight_id,
            f.flight_number,
            o.airport_code,
            d.airport_code,
            f.departure_datetime,
            f.arrival_datetime,
            f.gate,
            f.status
        FROM Flight f
        JOIN Destination o
            ON f.origin_id = o.destination_id
        JOIN Destination d
            ON f.destination_id = d.destination_id
        WHERE DATE(f.departure_datetime) = ?
        ORDER BY f.departure_datetime
    """, (departure_date,))

    flights = cursor.fetchall()
    conn.close()

    if flights:
        display_flights(flights)
    else:
        print("\nNo flights found for that departure date.")


# Flight management functions

def add_flight():
    print("\nADD NEW FLIGHT")

    flight_number = input("Enter flight number: ").strip().upper()

    try:
        origin_id = int(input("Enter origin destination ID: "))
        destination_id = int(input("Enter destination ID: "))
    except ValueError:
        print("\nInvalid ID. Origin and destination IDs must be numbers.")
        return

    if origin_id == destination_id:
        print("\nOrigin and destination cannot be the same.")
        return

    departure_datetime = input(
        "Enter departure date/time (YYYY-MM-DD HH:MM): "
    ).strip()

    arrival_datetime = input(
        "Enter arrival date/time (YYYY-MM-DD HH:MM): "
    ).strip()

    gate = input("Enter gate (leave blank if not assigned): ").strip().upper()

    if gate == "":
        gate = None

    allowed_statuses = [
        "Scheduled",
        "On-Time",
        "Boarding",
        "Final Call",
        "Gate Closed",
        "Delayed",
        "Cancelled",
        "Completed"
    ]

    status = input("Enter status: ").strip().title()

    if status not in allowed_statuses:
        print("\nInvalid status.")
        print("Valid statuses are:")

        for valid_status in allowed_statuses:
            print("-", valid_status)

        return

    conn = get_connection()
    cursor = conn.cursor()

    # Check that both destination IDs exist
    cursor.execute("""
        SELECT destination_id
        FROM Destination
        WHERE destination_id = ?
    """, (origin_id,))

    if cursor.fetchone() is None:
        print("\nOrigin destination ID does not exist.")
        conn.close()
        return

    cursor.execute("""
        SELECT destination_id
        FROM Destination
        WHERE destination_id = ?
    """, (destination_id,))

    if cursor.fetchone() is None:
        print("\nDestination ID does not exist.")
        conn.close()
        return

    cursor.execute("""
        INSERT INTO Flight (
            flight_number,
            origin_id,
            destination_id,
            departure_datetime,
            arrival_datetime,
            gate,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        flight_number,
        origin_id,
        destination_id,
        departure_datetime,
        arrival_datetime,
        gate,
        status
    ))

    conn.commit()
    conn.close()

    print("\nFlight added successfully.")


def update_flight():
    print("\nUPDATE FLIGHT")

    flight_id = input("Enter Flight ID to update: ").strip()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT flight_number, departure_datetime, arrival_datetime, gate, status
        FROM Flight
        WHERE flight_id = ?
    """, (flight_id,))

    flight = cursor.fetchone()

    if flight is None:
        print("\nFlight not found.")
        conn.close()
        return

    print(f"\nFlight: {flight[0]}")
    print("1. Update Departure Date/Time")
    print("2. Update Arrival Date/Time")
    print("3. Update Gate")
    print("4. Update Status")

    choice = input("\nChoose information to update: ").strip()

    if choice == "1":
        new_value = input(
            "Enter new departure date/time (YYYY-MM-DD HH:MM): "
        ).strip()

        cursor.execute("""
            UPDATE Flight
            SET departure_datetime = ?
            WHERE flight_id = ?
        """, (new_value, flight_id))

    elif choice == "2":
        new_value = input(
            "Enter new arrival date/time (YYYY-MM-DD HH:MM): "
        ).strip()

        cursor.execute("""
            UPDATE Flight
            SET arrival_datetime = ?
            WHERE flight_id = ?
        """, (new_value, flight_id))

    elif choice == "3":
        new_value = input("Enter new gate: ").strip().upper()

        if new_value == "":
            new_value = None

        cursor.execute("""
            UPDATE Flight
            SET gate = ?
            WHERE flight_id = ?
        """, (new_value, flight_id))

    elif choice == "4":
        allowed_statuses = [
            "Scheduled",
            "On-Time",
            "Boarding",
            "Final Call",
            "Gate Closed",
            "Delayed",
            "Cancelled",
            "Completed"
        ]

        new_value = input("Enter new status: ").strip().title()

        if new_value not in allowed_statuses:
            print("\nInvalid status.")
            print("Valid statuses are:")

            for status in allowed_statuses:
                print("-", status)

            conn.close()
            return

        cursor.execute("""
            UPDATE Flight
            SET status = ?
            WHERE flight_id = ?
        """, (new_value, flight_id))

    else:
        print("\nInvalid choice.")
        conn.close()
        return

    conn.commit()
    conn.close()

    print("\nFlight updated successfully.")


def delete_flight():
    print("\nDELETE FLIGHT")

    flight_id = input("Enter Flight ID to delete: ").strip()

    if not flight_id.isdigit():
        print("\nInvalid Flight ID. Please enter a number.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT flight_number
        FROM Flight
        WHERE flight_id = ?
    """, (flight_id,))

    flight = cursor.fetchone()

    if flight is None:
        print("\nFlight not found.")
        conn.close()
        return

    confirmation = input(
        f"Are you sure you want to delete Flight {flight[0]} "
        f"(ID {flight_id})? (Y/N): "
    ).strip().lower()

    if confirmation != "y":
        print("\nDeletion cancelled.")
        conn.close()
        return

    cursor.execute("""
        DELETE FROM FlightPilot
        WHERE flight_id = ?
    """, (flight_id,))

    cursor.execute("""
        DELETE FROM Flight
        WHERE flight_id = ?
    """, (flight_id,))

    conn.commit()
    conn.close()

    print("\nFlight deleted successfully.")


# Pilot functions

def assign_pilot():
    print("\nASSIGN PILOT TO FLIGHT")

    flight_id = input("Enter Flight ID: ").strip()
    pilot_id = input("Enter Pilot ID: ").strip()

    if not flight_id.isdigit() or not pilot_id.isdigit():
        print("\nFlight ID and Pilot ID must be numbers.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    # Check that the flight exists
    cursor.execute("""
        SELECT flight_number
        FROM Flight
        WHERE flight_id = ?
    """, (flight_id,))

    flight = cursor.fetchone()

    if flight is None:
        print("\nFlight not found.")
        conn.close()
        return

    # Check that the pilot exists and retrieve their status
    cursor.execute("""
        SELECT first_name, last_name, status
        FROM Pilot
        WHERE pilot_id = ?
    """, (pilot_id,))

    pilot = cursor.fetchone()

    if pilot is None:
        print("\nPilot not found.")
        conn.close()
        return

    if pilot[2] != "Active":
        print(
            f"\nPilot {pilot[0]} {pilot[1]} cannot be assigned "
            f"because their status is '{pilot[2]}'."
        )
        conn.close()
        return

    # Check whether the pilot is already assigned to this flight
    cursor.execute("""
        SELECT *
        FROM FlightPilot
        WHERE flight_id = ? AND pilot_id = ?
    """, (flight_id, pilot_id))

    if cursor.fetchone() is not None:
        print("\nThis pilot is already assigned to that flight.")
        conn.close()
        return

    role = input("Enter role (Captain/First Officer): ").strip().title()

    if role not in ["Captain", "First Officer"]:
        print("\nInvalid role. Please enter Captain or First Officer.")
        conn.close()
        return

    cursor.execute("""
        INSERT INTO FlightPilot (flight_id, pilot_id, role)
        VALUES (?, ?, ?)
    """, (flight_id, pilot_id, role))

    conn.commit()
    conn.close()

    print(
        f"\n{pilot[0]} {pilot[1]} successfully assigned "
        f"to Flight {flight[0]} as {role}."
    )


def view_pilot_schedule():
    print("\nVIEW PILOT SCHEDULE")

    pilot_id = input("Enter Pilot ID: ").strip()

    if not pilot_id.isdigit():
        print("\nInvalid Pilot ID. Please enter a number.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT first_name, last_name
        FROM Pilot
        WHERE pilot_id = ?
    """, (pilot_id,))

    pilot = cursor.fetchone()

    if pilot is None:
        print("\nPilot not found.")
        conn.close()
        return

    cursor.execute("""
        SELECT
            f.flight_id,
            f.flight_number,
            o.airport_code,
            d.airport_code,
            f.departure_datetime,
            f.arrival_datetime,
            fp.role,
            f.status
        FROM FlightPilot fp
        JOIN Flight f
            ON fp.flight_id = f.flight_id
        JOIN Destination o
            ON f.origin_id = o.destination_id
        JOIN Destination d
            ON f.destination_id = d.destination_id
        WHERE fp.pilot_id = ?
        ORDER BY f.departure_datetime
    """, (pilot_id,))

    schedule = cursor.fetchall()
    conn.close()

    print(f"\nSchedule for {pilot[0]} {pilot[1]}")

    if not schedule:
        print("No flights currently assigned.")
        return

    row_format = "{:<4} {:<8} {:<8} {:<12} {:<18} {:<18} {:<15} {:<12}"

    print("-" * 105)

    print(row_format.format(
        "ID",
        "Flight",
        "Origin",
        "Destination",
        "Departure",
        "Arrival",
        "Role",
        "Status"
    ))

    print("-" * 105)

    for flight in schedule:
        print(row_format.format(*flight))


# Destination functions

def view_destinations():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            destination_id,
            airport_code,
            airport_name,
            city,
            country
        FROM Destination
        ORDER BY airport_code
    """)

    destinations = cursor.fetchall()
    conn.close()

    row_format = "{:<4} {:<8} {:<40} {:<18} {:<25}"

    print("\nDESTINATIONS")
    print("-" * 100)

    print(row_format.format(
        "ID",
        "Code",
        "Airport",
        "City",
        "Country"
    ))

    print("-" * 100)

    for destination in destinations:
        print(row_format.format(*destination))


def update_destination():
    print("\nUPDATE DESTINATION")

    destination_id = input("Enter Destination ID to update: ").strip()

    if not destination_id.isdigit():
        print("\nInvalid Destination ID. Please enter a number.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT airport_code, airport_name, city, country
        FROM Destination
        WHERE destination_id = ?
    """, (destination_id,))

    destination = cursor.fetchone()

    if destination is None:
        print("\nDestination not found.")
        conn.close()
        return

    print(f"\nDestination: {destination[0]} - {destination[1]}")
    print("1. Update Airport Name")
    print("2. Update City")
    print("3. Update Country")

    choice = input("\nChoose information to update: ").strip()

    if choice == "1":
        new_value = input("Enter new airport name: ").strip()

        cursor.execute("""
            UPDATE Destination
            SET airport_name = ?
            WHERE destination_id = ?
        """, (new_value, destination_id))

    elif choice == "2":
        new_value = input("Enter new city: ").strip()

        cursor.execute("""
            UPDATE Destination
            SET city = ?
            WHERE destination_id = ?
        """, (new_value, destination_id))

    elif choice == "3":
        new_value = input("Enter new country: ").strip()

        cursor.execute("""
            UPDATE Destination
            SET country = ?
            WHERE destination_id = ?
        """, (new_value, destination_id))

    else:
        print("\nInvalid choice.")
        conn.close()
        return

    conn.commit()
    conn.close()

    print("\nDestination updated successfully.")


# Statistics

def show_statistics():
    print("\nFLIGHT STATISTICS")
    print("1. Number of Flights to Each Destination")
    print("2. Number of Flights Assigned to Each Pilot")

    choice = input("\nChoose a statistic to view: ").strip()

    conn = get_connection()
    cursor = conn.cursor()

    if choice == "1":
        cursor.execute("""
            SELECT
                d.airport_code,
                d.city,
                COUNT(f.flight_id) AS flight_count
            FROM Destination d
            LEFT JOIN Flight f
                ON d.destination_id = f.destination_id
            GROUP BY d.destination_id, d.airport_code, d.city
            ORDER BY flight_count DESC, d.airport_code
        """)

        results = cursor.fetchall()

        print("\nFLIGHTS BY DESTINATION")
        print("-" * 45)

        print("{:<10} {:<20} {:<10}".format(
            "Code",
            "City",
            "Flights"
        ))

        print("-" * 45)

        for airport_code, city, flight_count in results:
            print("{:<10} {:<20} {:<10}".format(
                airport_code,
                city,
                flight_count
            ))

    elif choice == "2":
        cursor.execute("""
            SELECT
                p.pilot_id,
                p.first_name,
                p.last_name,
                COUNT(fp.flight_id) AS flight_count
            FROM Pilot p
            LEFT JOIN FlightPilot fp
                ON p.pilot_id = fp.pilot_id
            GROUP BY p.pilot_id, p.first_name, p.last_name
            ORDER BY flight_count DESC, p.last_name
        """)

        results = cursor.fetchall()

        print("\nFLIGHTS ASSIGNED TO PILOTS")
        print("-" * 55)

        print("{:<4} {:<15} {:<15} {:<10}".format(
            "ID",
            "First Name",
            "Last Name",
            "Flights"
        ))

        print("-" * 55)

        for pilot_id, first_name, last_name, flight_count in results:
            print("{:<4} {:<15} {:<15} {:<10}".format(
                pilot_id,
                first_name,
                last_name,
                flight_count
            ))

    else:
        print("\nInvalid choice.")

    conn.close()


def pause():
    input("\nPress Enter to return to the main menu...")


# Main menu

def main_menu():
    while True:
        print("\n===================================")
        print("      FLIGHT MANAGEMENT SYSTEM")
        print("===================================")
        print("1. View All Flights")
        print("2. View Flights by Status")
        print("3. View Flights by Destination")
        print("4. View Flights by Departure Date")
        print("5. Add New Flight")
        print("6. Update Flight")
        print("7. Delete Flight")
        print("8. Assign Pilot to Flight")
        print("9. View Pilot Schedule")
        print("10. View Destinations")
        print("11. Update Destination")
        print("12. Show Statistics")
        print("13. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            view_all_flights()
            pause()

        elif choice == "2":
            view_flights_by_status()
            pause()

        elif choice == "3":
            view_flights_by_destination()
            pause()

        elif choice == "4":
            view_flights_by_date()
            pause()

        elif choice == "5":
            add_flight()
            pause()

        elif choice == "6":
            update_flight()
            pause()

        elif choice == "7":
            delete_flight()
            pause()

        elif choice == "8":
            assign_pilot()
            pause()

        elif choice == "9":
            view_pilot_schedule()
            pause()

        elif choice == "10":
            view_destinations()
            pause()

        elif choice == "11":
            update_destination()
            pause()

        elif choice == "12":
            show_statistics()
            pause()

        elif choice == "13":
            print("\nExiting Flight Management System.")
            break

        else:
            print("\nInvalid choice. Please enter a number from 1 to 13.")


main_menu()