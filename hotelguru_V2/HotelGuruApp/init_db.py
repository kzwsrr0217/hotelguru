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
# db.session.add_all([ Room(number=101, floor=1, name="Szoba 101", description="Egy ágyas szoba", price=10000, room_type=db.session.get(RoomType, 1)) ])

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

# # Szobák és szolgáltatások összekapcsolása

# from app.models.room import Room
# from app.models.service import Service

# room101 = db.session.get(Room, 1)
# room102 = db.session.get(Room, 2)
# room201 = db.session.get(Room, 3)
# room202 = db.session.get(Room, 4)

# reggeli = db.session.get(Service, 1)
# parkolas = db.session.get(Service, 2)
# wellness = db.session.get(Service, 3)
# takaritas = db.session.get(Service, 4)

# room101.services.append(reggeli)
# room101.services.append(parkolas)
# room102.services.append(reggeli)
# room201.services.append(wellness)
# room201.services.append(takaritas)
# room202.services.append(reggeli)
# room202.services.append(parkolas)
# room202.services.append(wellness)
# room202.services.append(takaritas)

# db.session.commit()

#Address
#from app.models.address import Address

#db.session.add(Address( city = "Veszprém",  street = "Egyetem u. 1", postalcode=8200))
#db.session.commit()


#User
# from app.models.user import User, UserRole

# user = User(name="Test User", email="test@gmail.com", phone="+3620111111")
# user.address = db.session.get(Address, 2)
# user.set_password("qweasd")

# db.session.add(user)

# u = db.session.get(User, 1)
# u.roles.append(db.session.get(Role,3))
# print(u)

# db.session.commit()
