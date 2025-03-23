from __future__ import annotations

from HotelGuruApp.app import models
from app import db
from app import create_app
from config import Config

app = create_app(config_class=Config)

app.app_context().push()

#Role
from app.models.role import Role

if not Role.query.first():
    db.session.add_all([ Role(name="Administrator"), 
                         Role(name="Receptionist"), 
                         Role(name ="Guest") ])
    db.session.commit()
    print("A roles -ok sikeresen feltöltve!")
else:
    print("A roles -ok már léteznek!")

#RoomType
from app.models.room_type import RoomType

if not RoomType.query.first():
    db.session.add_all([
        RoomType(name="Egy ágyas"),
        RoomType(name="Két ágyas"),
        RoomType(name="Lakosztály"),
        RoomType(name="Apartman")
    ])
    db.session.commit()
    print("Szobatípusok sikeresen feltöltve!")
else:
    print("A szobatípusok már léteznek!")

# # Room hozzáadása
# from app.models.room import Room
# db.session.add_all([ Room(number=101, floor=1, name="Szoba 101", description="Egy ágyas szoba", price=10000, room_type=db.session.get(RoomType, 1)),
#                      Room(number=102, floor=1, name="Szoba 102", description="Két ágyas szoba", price=15000, room_type=db.session.get(RoomType, 2)),
#                      Room(number=201, floor=2, name="Szoba 201", description="Lakosztály", price=20000, room_type=db.session.get(RoomType, 3)),
#                      Room(number=202, floor=2, name="Szoba 202", description="Apartman", price=25000, room_type=db.session.get(RoomType, 4))  ])

# db.session.commit()

# room_type = Room.query.filter_by(room_type_id="1").first()
# print(room_type)

# room = Room.query.filter_by(number="2").first()
# print(room.room_type.name) 

#Service
from app.models.service import Service
if not Service.query.first():
    db.session.add_all([ Service(name="Reggeli", description="Büfé reggeli", price=1500),
                        Service(name="Parkolás", description="Parkoló használat", price=500),
                        Service(name="Wellness", description="Wellness szolgáltatás", price=2000), 
                        Service(name="Takarítás", description="Szobatakítás", price=1000) ])
    db.session.commit()
    print("A Szolgáltatások sikeresen feltöltve!")
else:
    print("A szolgáltatások már léteznek!")



#Address
# from app.models.address import Address

# db.session.add(Address( city = "Veszprém",  street = "Egyetem u. 1", postalcode=8200))
# db.session.commit()


#User
# from app.models.user import User, UserRole

# user = User(name="Test User", email="test@gmail.com", phone="+3620111111")
# user.address = db.session.get(Address, 1)
# user.set_password("qweasd")

# db.session.add(user)

# u = db.session.get(User, 1)
# u.roles.append(db.session.get(Role,3))
# # print(u)
# db.session.commit()



#Reservation
from app.models.reservation import Reservation
from datetime import date
from app.models.invoice import Invoice
if not Reservation.query.first():
    try:
        Reservation.create_reservation(
            user_id=1,
            room_id=1,
            start_date=date(2025, 4, 3),
            end_date=date(2025, 4, 10)
        )
        print("A foglalás sikeresen létrehozva!")
    except ValueError as e:
        print(f"Hiba a foglalás létrehozásakor: {e}")
else:
    print("A foglalás már létezik!")

reservation_id = 1
service_ids_at_booking = [1, 2]  # A foglaláskor igénybe vett szolgáltatások
service_ids_after_booking = [3]  # A foglalás után igénybe vett szolgáltatások

# 1. Foglaláskor létrehozzuk a számlát a foglaláskor igénybe vett szolgáltatásokkal.
# try:
#     invoice = Invoice.create_invoice(reservation_id, service_ids=service_ids_at_booking)
#     print(f"Számla sikeresen létrehozva! Azonosító: {invoice.id}")
#     print(f"Használt szolgáltatások (foglaláskor): {invoice.used_services}")
#     print(f"Végösszeg (foglaláskor): {invoice.amount}")
# except ValueError as e:
#     print(f"Hiba a számla létrehozásakor: {e}")

# 2. Később, amikor a felhasználó a foglalás után vesz igénybe szolgáltatásokat.
try:
    invoice= db.session.get(Invoice, 1)
    invoice.add_services_to_invoice(service_ids=service_ids_after_booking)
    print(f"Szolgáltatások sikeresen hozzáadva a számlához!")
    print(f"Használt szolgáltatások (összesen): {invoice.used_services}")
    print(f"Végösszeg (frissítve): {invoice.amount}")
except ValueError as e:
    print(f"Hiba a szolgáltatások hozzáadásakor: {e}")


