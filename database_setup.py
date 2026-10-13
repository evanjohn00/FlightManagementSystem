import sqlite3

conn = sqlite3.connect("flight_management.db")
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Destination (
    destination_id INTEGER PRIMARY KEY,
    airport_code TEXT NOT NULL UNIQUE,
    airport_name TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL
)
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pilot (
    pilot_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    licence_number TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (
        status IN (
        'Active',
        'On Leave',
        'Unavailable'
        )
    )
)
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Flight (
    flight_id INTEGER PRIMARY KEY,
    flight_number TEXT NOT NULL,
    origin_id INTEGER NOT NULL,
    destination_id INTEGER NOT NULL,
    departure_datetime TEXT NOT NULL,
    arrival_datetime TEXT NOT NULL,
    gate TEXT,
    status TEXT NOT NULL CHECK (
        status IN (
        'Scheduled',
        'On-Time',
        'Boarding',
        'Final Call',
        'Gate Closed',
        'Delayed',
        'Cancelled',
        'Completed'
        )
    ),
    FOREIGN KEY (origin_id) REFERENCES Destination(destination_id),
    FOREIGN KEY (destination_id) REFERENCES Destination(destination_id)
)
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS FlightPilot (
    flight_id INTEGER NOT NULL,
    pilot_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK (
        role IN (
        'Captain',
        'First Officer'
        )
    ),

    PRIMARY KEY (flight_id, pilot_id),
    FOREIGN KEY (flight_id) REFERENCES Flight(flight_id),
    FOREIGN KEY (pilot_id) REFERENCES Pilot(pilot_id)
)
""")    

# Sample Destination Data
destinations = [
    (1, 'LHR', 'London Heathrow Airport', 'London', 'United Kingdom'),
    (2, 'LGW', 'London Gatwick Airport', 'London', 'United Kingdom'),
    (3, 'MAN', 'Manchester Airport', 'Manchester', 'United Kingdom'),
    (4, 'EDI', 'Edinburgh Airport', 'Edinburgh', 'United Kingdom'),
    (5, 'CWL', 'Cardiff Airport', 'Cardiff', 'United Kingdom'),
    (6, 'DUB', 'Dublin Airport', 'Dublin', 'Ireland'),
    (7, 'CDG', 'Charles de Gaulle Airport', 'Paris', 'France'),
    (8, 'AMS', 'Amsterdam Airport Schiphol', 'Amsterdam', 'Netherlands'),
    (9, 'MAD', 'Adolfo Suárez Madrid-Barajas Airport', 'Madrid', 'Spain'),
    (10, 'FCO', 'Leonardo Da Vinci-Fiumicino Airport', 'Rome', 'Italy'),
    (11, 'JFK', 'John F. Kennedy International Airport', 'New York', 'United States of America'),
    (12, 'TNR', 'Ivato International Airport', 'Antananarivo', 'Madagascar'),
    (13, 'LIM', 'Jorge Chávez International Airport', 'Lima', 'Peru'),
    (14, 'BKK', 'Suvarnabhumi Airport', 'Bangkok', 'Thailand'),
    (15, 'SYD', 'Sydney Airport', 'Sydney', 'Australia')
]

cursor.executemany("""
INSERT OR IGNORE INTO Destination
(destination_id, airport_code, airport_name, city, country)
VALUES (?, ?, ?, ?, ?)
""", destinations)

# Sample Pilot Data
pilots = [
    (1, 'Amelia', 'Hughes', 'UK-PL-1001', 'Active'),
    (2, 'Geoff', 'Smith', 'UK-PL-1002', 'Active'),
    (3, 'Kessara', 'Jones', 'UK-PL-1003', 'Active'),
    (4, 'Abigail', 'Peters', 'UK-PL-1004', 'Unavailable'),
    (5, 'Mohammed', 'Hasan', 'UK-PL-1005', 'Active'),
    (6, 'Emily', 'Chen', 'UK-PL-1006', 'Active'),
    (7, 'Thomas', 'Singh', 'UK-PL-1007', 'On Leave'),
    (8, 'Clive', 'John', 'UK-PL-1008', 'Active'),
    (9, 'Maya', 'Lewis', 'UK-PL-1009', 'Active'),
    (10, 'Henry', 'Wilson', 'UK-PL-1010', 'Active'),
    (11, 'Oliver', 'Morgan', 'UK-PL-1011', 'Active'),
    (12, 'Noah', 'Evans', 'UK-PL-1012', 'Active'),
    (13, 'Aisha', 'Khan', 'UK-PL-1013', 'Active'),
    (14, 'Yasmin', 'Ling', 'UK-PL-1014', 'On Leave'),
    (15, 'Charlotte', 'Brown', 'UK-PL-1015', 'Active')
]

cursor.executemany("""
INSERT OR IGNORE INTO Pilot
(pilot_id, first_name, last_name, licence_number, status)
VALUES (?, ?, ?, ?, ?)
""", pilots)

# Sample Flights Data
flights = [
    (1, 'EX113', 6, 1, '2026-10-04 16:00', '2026-10-04 17:20', 'A01', 'Completed'),
    (2, 'EX101', 1, 9, '2026-10-05 08:00', '2026-10-05 10:30', 'A12', 'Gate Closed'),
    (3, 'EX102', 1, 7, '2026-10-05 09:15', '2026-10-05 11:30', 'B04', 'Final Call'),
    (4, 'EX103', 2, 8, '2026-10-05 10:00', '2026-10-05 12:20', 'C07', 'Boarding'),
    (5, 'EX104', 3, 6, '2026-10-05 11:20', '2026-10-05 12:30', 'D03', 'On-Time'),
    (6, 'EX105', 4, 5, '2026-10-05 12:45', '2026-10-05 14:10', None, 'Delayed'),
    (7, 'EX106', 5, 1, '2026-10-05 14:00', '2026-10-05 15:10', 'A05', 'Scheduled'),
    (8, 'EX107', 1, 10, '2026-10-06 07:30', '2026-10-06 11:00', 'B11', 'Scheduled'),
    (9, 'EX108', 1, 11, '2026-10-06 09:00', '2026-10-06 17:15', 'C14', 'Scheduled'),
    (10, 'EX109', 1, 12, '2026-10-06 10:30', '2026-10-06 22:00', 'A09', 'Scheduled'),
    (11, 'EX110', 1, 13, '2026-10-07 06:45', '2026-10-07 19:15', 'D08', 'Scheduled'),
    (12, 'EX111', 1, 14, '2026-10-07 12:00', '2026-10-07 23:30', 'B16', 'Scheduled'),
    (13, 'EX112', 1, 15, '2026-10-08 20:00', '2026-10-09 16:30', 'C20', 'Scheduled'),
    (14, 'EX101', 1, 9, '2026-10-08 08:00', '2026-10-08 10:30', 'A12', 'Scheduled'),
    (15, 'EX104', 3, 6, '2026-10-08 11:20', '2026-10-08 12:30', 'D03', 'Scheduled')
]

cursor.executemany("""
INSERT OR IGNORE INTO Flight
(flight_id, flight_number, origin_id, destination_id, departure_datetime, arrival_datetime, gate, status)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", flights)

# Sample Flight Assignments Data
flight_pilots = [
    (1, 1, 'Captain'),
    (1, 2, 'First Officer'),

    (2, 3, 'Captain'),
    (2, 5, 'First Officer'),

    (3, 6, 'Captain'),
    (3, 8, 'First Officer'),

    (4, 9, 'Captain'),
    (4, 10, 'First Officer'),

    (5, 11, 'Captain'),
    (5, 12, 'First Officer'),

    (7, 13, 'Captain'),
    (7, 15, 'First Officer'),

    (9, 1, 'Captain'),
    (12, 3, 'Captain'),
    (14, 5, 'Captain')
]

cursor.executemany("""
INSERT OR IGNORE INTO FlightPilot
(flight_id, pilot_id, role)
VALUES (?, ?, ?)
""", flight_pilots)

conn.commit()
conn.close()

print("Database tables created successfully")