# init_db.py

import os
from datetime import date, timedelta
import sys

# Add the project root to the Python path to allow importing 'app'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app, db
from config import Config

# Import models AFTER adding project root to path
from app.models.role import Role
from app.models.room_type import RoomType
from app.models.service import Service
from app.models.address import Address
from app.models.user import User
from app.models.room import Room
from app.models.reservation import Reservation, StatusEnum as ReservationStatusEnum
from app.models.invoice import Invoice, StatusEnum as InvoiceStatusEnum

# --- App Context Setup ---
app = create_app(config_class=Config)
app.app_context().push()
print("App context pushed.")

# --- Seeding Functions ---


def seed_roles():
    print("Seeding Roles...")
    if not Role.query.first():
        try:
            roles_to_add = [
                Role(name="Administrator"),
                Role(name="Receptionist"),
                Role(name="Guest"),
            ]
            db.session.add_all(roles_to_add)
            db.session.commit()
            print("SUCCESS: Roles seeded.")
        except Exception as e:
            db.session.rollback()
            print(f"ERROR seeding Roles: {e}")
    else:
        print("INFO: Roles already exist.")


def seed_room_types():
    print("Seeding Room Types...")
    if not RoomType.query.first():
        try:
            types_to_add = [
                RoomType(name="Egy ágyas"),
                RoomType(name="Két ágyas"),
                RoomType(name="Lakosztály"),
                RoomType(name="Apartman"),
            ]
            db.session.add_all(types_to_add)
            db.session.commit()
            print("SUCCESS: Room Types seeded.")
        except Exception as e:
            db.session.rollback()
            print(f"ERROR seeding Room Types: {e}")
    else:
        print("INFO: Room Types already exist.")


def seed_services():
    print("Seeding Services...")
    if not Service.query.first():
        try:
            services_to_add = [
                Service(name="Reggeli", description="Büfé reggeli", price=3000),
                Service(name="Parkolás", description="Parkoló használat", price=1500),
                Service(
                    name="Wellness", description="Wellness szolgáltatás", price=5000
                ),
                Service(name="Takarítás", description="Napi takarítás", price=1000),
            ]
            db.session.add_all(services_to_add)
            db.session.commit()
            print("SUCCESS: Services seeded.")
        except Exception as e:
            db.session.rollback()
            print(f"ERROR seeding Services: {e}")
    else:
        print("INFO: Services already exist.")


def seed_addresses_users():
    print("Seeding Addresses and Users...")
    if not User.query.first():
        try:
            # Retrieve roles (assuming they exist now)
            admin_role = db.session.execute(
                db.select(Role).filter_by(name="Administrator")
            ).scalar_one_or_none()
            receptionist_role = db.session.execute(
                db.select(Role).filter_by(name="Receptionist")
            ).scalar_one_or_none()
            guest_role = db.session.execute(
                db.select(Role).filter_by(name="Guest")
            ).scalar_one_or_none()

            if not all([admin_role, receptionist_role, guest_role]):
                print("ERROR: Roles not found. Seed roles first.")
                return

            # Addresses
            address1 = Address(
                city="Veszprém", street="Egyetem u. 10.", postalcode=8200
            )
            address2 = Address(city="Budapest", street="Fő utca 1.", postalcode=1011)
            address3 = Address(city="Szeged", street="Móka tér 5.", postalcode=6720)
            db.session.add_all([address1, address2, address3])
            # Commit addresses first to get IDs if needed, or let SQLAlchemy handle it
            # db.session.commit() # Let's try without committing here first

            # Users
            user_admin = User(
                name="Admin Béla",
                email="admin@hotel.test",
                phone="+36101111111",
                address=address1,
            )
            user_admin.set_password("adminpass")
            user_admin.roles.append(admin_role)

            user_receptionist = User(
                name="Recepciós Rita",
                email="recepcio@hotel.test",
                phone="+36102222222",
                address=address1,
            )  # Same address as admin
            user_receptionist.set_password("recepciopass")
            user_receptionist.roles.append(receptionist_role)

            user_guest1 = User(
                name="Vendég Vince",
                email="guest1@example.com",
                phone="+36201234567",
                address=address2,
            )
            user_guest1.set_password("guest1pass")
            user_guest1.roles.append(guest_role)

            user_guest2 = User(
                name="Vendég Viola",
                email="guest2@example.com",
                phone="+36309876543",
                address=address3,
            )
            user_guest2.set_password("guest2pass")
            user_guest2.roles.append(guest_role)

            db.session.add_all(
                [user_admin, user_receptionist, user_guest1, user_guest2]
            )
            db.session.commit()
            print("SUCCESS: Addresses and Users seeded.")

        except Exception as e:
            db.session.rollback()
            print(f"ERROR seeding Addresses/Users: {e}")
    else:
        print("INFO: Users already exist.")


def seed_rooms():
    print("Seeding Rooms...")
    if not Room.query.first():
        try:
            # Retrieve room types
            rt_egy = db.session.execute(
                db.select(RoomType).filter_by(name="Egy ágyas")
            ).scalar_one_or_none()
            rt_ket = db.session.execute(
                db.select(RoomType).filter_by(name="Két ágyas")
            ).scalar_one_or_none()
            rt_lak = db.session.execute(
                db.select(RoomType).filter_by(name="Lakosztály")
            ).scalar_one_or_none()
            rt_apt = db.session.execute(
                db.select(RoomType).filter_by(name="Apartman")
            ).scalar_one_or_none()

            if not all([rt_egy, rt_ket, rt_lak, rt_apt]):
                print("ERROR: Room types not found. Seed room types first.")
                return

            rooms_to_add = [
                Room(
                    number=101,
                    floor=1,
                    name="Standard Egyágyas",
                    description="Kilátás a parkolóra",
                    price=15000,
                    room_type=rt_egy,
                    is_available=True,
                ),
                Room(
                    number=102,
                    floor=1,
                    name="Standard Kétágyas",
                    description="Kilátás az utcára",
                    price=22000,
                    room_type=rt_ket,
                    is_available=True,
                ),
                Room(
                    number=201,
                    floor=2,
                    name="Superior Kétágyas",
                    description="Erkélyes, kilátás a parkra",
                    price=28000,
                    room_type=rt_ket,
                    is_available=True,
                ),
                Room(
                    number=202,
                    floor=2,
                    name="Lakosztály Mini",
                    description="Kis nappali résszel",
                    price=35000,
                    room_type=rt_lak,
                    is_available=True,
                ),
                Room(
                    number=301,
                    floor=3,
                    name="Apartman Terasz",
                    description="Nagy terasszal",
                    price=45000,
                    room_type=rt_apt,
                    is_available=False,
                ),  # Not available
            ]
            db.session.add_all(rooms_to_add)
            db.session.commit()
            print("SUCCESS: Rooms seeded.")
        except Exception as e:
            db.session.rollback()
            print(f"ERROR seeding Rooms: {e}")
    else:
        print("INFO: Rooms already exist.")


def seed_reservations_invoices():
    print("Seeding Reservations and Invoices...")
    if not Reservation.query.first():
        try:
            # Get users and rooms
            guest1 = db.session.execute(
                db.select(User).filter_by(email="guest1@example.com")
            ).scalar_one_or_none()
            guest2 = db.session.execute(
                db.select(User).filter_by(email="guest2@example.com")
            ).scalar_one_or_none()
            room101 = db.session.execute(
                db.select(Room).filter_by(number=101)
            ).scalar_one_or_none()
            room102 = db.session.execute(
                db.select(Room).filter_by(number=102)
            ).scalar_one_or_none()
            room201 = db.session.execute(
                db.select(Room).filter_by(number=201)
            ).scalar_one_or_none()

            # Get services
            service_reggeli = db.session.execute(
                db.select(Service).filter_by(name="Reggeli")
            ).scalar_one_or_none()
            service_parkolas = db.session.execute(
                db.select(Service).filter_by(name="Parkolás")
            ).scalar_one_or_none()
            service_wellness = db.session.execute(
                db.select(Service).filter_by(name="Wellness")
            ).scalar_one_or_none()

            if not all(
                [
                    guest1,
                    guest2,
                    room101,
                    room102,
                    room201,
                    service_reggeli,
                    service_parkolas,
                    service_wellness,
                ]
            ):
                print(
                    "ERROR: Missing prerequisites (users, rooms, services). Seed them first."
                )
                return

            # Reservation 1: Guest 1, Room 101
            today = date.today()
            start1 = today + timedelta(days=10)
            end1 = today + timedelta(days=15)
            res1 = Reservation(
                user=guest1,
                start_date=start1,
                end_date=end1,
                reservation_date=today,
                status=ReservationStatusEnum.Success,  # Use Enum member
            )
            res1.rooms.append(room101)
            room101.is_available = False  # Mark room as unavailable
            db.session.add(res1)

            # Reservation 2: Guest 2, Room 102 & Room 201
            start2 = today + timedelta(days=20)
            end2 = today + timedelta(days=23)
            res2 = Reservation(
                user=guest2,
                start_date=start2,
                end_date=end2,
                reservation_date=today,
                status=ReservationStatusEnum.Depending,  # Use Enum member
            )
            res2.rooms.append(room102)
            res2.rooms.append(room201)
            room102.is_available = False
            room201.is_available = False
            db.session.add(res2)

            # Commit reservations to get IDs for invoices
            db.session.commit()
            print("INFO: Reservations created.")

            # --- Invoices ---
            # Invoice for Reservation 1 (Assume res1 got ID=1)
            inv1 = Invoice(
                reservation_id=res1.id,  # Use the actual ID
                issue_date=today,
                status=InvoiceStatusEnum.Live,
            )
            # Add services
            inv1.services.append(service_reggeli)
            inv1.services.append(service_parkolas)
            # Calculate amount (simple example)
            num_days1 = (end1 - start1).days
            inv1.amount = (
                (room101.price * num_days1)
                + service_reggeli.price
                + service_parkolas.price
            )
            inv1.used_services = f"{service_reggeli.id},{service_parkolas.id}"  # Update used_services string
            db.session.add(inv1)

            # Invoice for Reservation 2 (Assume res2 got ID=2)
            inv2 = Invoice(
                reservation_id=res2.id,  # Use the actual ID
                issue_date=today,
                status=InvoiceStatusEnum.Live,
            )
            # Add services
            inv2.services.append(service_wellness)
            # Calculate amount
            num_days2 = (end2 - start2).days
            inv2.amount = (
                (room102.price * num_days2)
                + (room201.price * num_days2)
                + service_wellness.price
            )
            inv2.used_services = f"{service_wellness.id}"  # Update used_services string
            db.session.add(inv2)

            db.session.commit()
            print("SUCCESS: Reservations and Invoices seeded.")

        except Exception as e:
            db.session.rollback()
            print(f"ERROR seeding Reservations/Invoices: {e}")
    else:
        print("INFO: Reservations already exist.")


# --- Main Execution ---
if __name__ == "__main__":
    print("--- Starting Database Seeding ---")
    seed_roles()
    seed_room_types()
    seed_services()
    seed_addresses_users()
    seed_rooms()
    seed_reservations_invoices()
    print("--- Database Seeding Finished ---")
