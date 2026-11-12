from datetime import datetime
import uuid


class Bus:
    def __init__(self, bus_id, operator, source, destination,
                 departure, fare, total_seats):
        self.bus_id = bus_id
        self.operator = operator
        self.source = source
        self.destination = destination
        self.departure = departure
        self.fare = fare
        self.total_seats = total_seats
        self.booked_seats = set()


class BusReservationSystem:

    def __init__(self):
        self.buses = [
            Bus("B101", "North Star Travels", "Delhi",
                "Jaipur", "08:00 AM", 550, 5),

            Bus("B102", "CityLink Express", "Delhi",
                "Jaipur", "10:30 AM", 650, 5),

            Bus("B201", "Himalayan Roadways", "Delhi",
                "Dehradun", "07:15 AM", 480, 5),

            Bus("B202", "Valley Express", "Delhi",
                "Dehradun", "09:45 AM", 520, 5)
        ]

        self.bookings = {}

    def search_buses(self):
        source = input("Enter source city: ").strip().lower()
        destination = input("Enter destination city: ").strip().lower()

        results = [
            bus for bus in self.buses
            if bus.source.lower() == source
            and bus.destination.lower() == destination
        ]

        if not results:
            print("\nNo buses available for this route.")
            return

        print("\n========== AVAILABLE BUSES ==========")

        for bus in results:
            available = bus.total_seats - len(bus.booked_seats)

            print(f"\nBus ID       : {bus.bus_id}")
            print(f"Operator     : {bus.operator}")
            print(f"Route        : {bus.source} to {bus.destination}")
            print(f"Departure    : {bus.departure}")
            print(f"Ticket Price : Rs. {bus.fare}")
            print(f"Available    : {available} seats")

    def book_ticket(self):
        self.search_buses()

        bus_id = input("\nEnter Bus ID: ").strip().upper()

        bus = next(
            (b for b in self.buses if b.bus_id == bus_id),
            None
        )

        if bus is None:
            print("Invalid Bus ID.")
            return

        seat = input(
            f"Select seat (1-{bus.total_seats}): "
        ).strip()

        if not seat.isdigit() or not (
            1 <= int(seat) <= bus.total_seats
        ):
            print("Invalid seat number.")
            return

        if seat in bus.booked_seats:
            print("Sorry! This seat is already booked.")
            return

        passenger = input("Enter passenger name: ").strip()

        if not passenger:
            print("Passenger name cannot be empty.")
            return

        booking_id = "CB" + uuid.uuid4().hex[:8].upper()

        bus.booked_seats.add(seat)

        booking = {
            "booking_id": booking_id,
            "passenger": passenger,
            "bus_id": bus.bus_id,
            "operator": bus.operator,
            "route": f"{bus.source} to {bus.destination}",
            "seat": seat,
            "fare": bus.fare,
            "status": "CONFIRMED",
            "booking_date": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        self.bookings[booking_id] = booking

        print("\n========== BOOKING SUCCESSFUL ==========")
        print(f"Booking ID : {booking_id}")
        print(f"Passenger  : {passenger}")
        print(f"Bus        : {bus.operator}")
        print(f"Seat       : {seat}")
        print(f"Fare       : Rs. {bus.fare}")
        print("Status     : CONFIRMED")

    def cancel_ticket(self):
        booking_id = input(
            "Enter Booking ID: "
        ).strip().upper()

        booking = self.bookings.get(booking_id)

        if not booking:
            print("Booking not found.")
            return

        if booking["status"] == "CANCELLED":
            print("Booking is already cancelled.")
            return

        bus = next(
            b for b in self.buses
            if b.bus_id == booking["bus_id"]
        )

        bus.booked_seats.discard(booking["seat"])
        booking["status"] = "CANCELLED"

        print("\nTicket cancelled successfully.")
        print("Booking ID:", booking_id)

    def view_bookings(self):
        if not self.bookings:
            print("\nNo booking records found.")
            return

        print("\n========== BOOKING RECORDS ==========")

        for booking in self.bookings.values():
            print("\n------------------------------")

            for key, value in booking.items():
                print(f"{key.upper():15}: {value}")

    def menu(self):
        while True:
            print("\n" + "=" * 45)
            print(" CLOUD BUS TICKET RESERVATION SYSTEM")
            print("=" * 45)

            print("1. Search Available Buses")
            print("2. Book Bus Ticket")
            print("3. Cancel Ticket")
            print("4. View Booking Records")
            print("5. Exit")

            choice = input("\nEnter your choice (1-5): ").strip()

            if choice == "1":
                self.search_buses()

            elif choice == "2":
                self.book_ticket()

            elif choice == "3":
                self.cancel_ticket()

            elif choice == "4":
                self.view_bookings()

            elif choice == "5":
                print("\nThank you for using our system!")
                break

            else:
                print("\nInvalid choice. Try again.")


if __name__ == "__main__":
    system = BusReservationSystem()
    system.menu()
