import logging
from app.extensions import db
from app.blueprints.service.schemas import (
    ServiceRequestSchema,
    ServiceResponseSchema,
    ServiceListSchema,
)

from app.models.service import Service

from sqlalchemy import select, and_


class ServiceService:

    @staticmethod
    def service_add(request):
        try:
            service = Service(**request)
            db.session.add(service)
            db.session.commit()
        except Exception as ex:
            db.session.rollback()  # <- Visszaállítja az adatbázis tranzakciót a hiba után
            logging.exception(
                f"Error in service_add: {ex}"
            )  # <- Naplózza a teljes hibát a konzolra
            return False, f"Database error adding service: {str(ex)}"
        return True, ServiceResponseSchema().dump(service)

    @staticmethod
    def service_list_all():
        service = db.session.execute(select(Service)).scalars()
        return True, ServiceListSchema().dump(service, many=True)

    @staticmethod
    def service_by_id(sid):
        service = db.session.execute(
            select(Service).filter(Service.id == sid)
        ).scalar_one_or_none()
        if service is None:
            return False, "Service not found!"
        return True, ServiceListSchema().dump(service)

    @staticmethod
    def service_update(sid, request):
        try:
            service = db.session.get(Service, sid)
            if service:
                service.name = request["name"]
                service.description = request["description"]
                service.price = float(request["price"])
                service.deleted = request["deleted"]
                db.session.commit()

        except Exception as ex:
            return False, "service_update() error!"
        return True, ServiceResponseSchema().dump(service)

    # @staticmethod
    # def service_delete(sid):
    #     try:
    #         service = db.session.get(Service, sid)
    #         if service:
    #             service.deleted = 1
    #             db.session.commit()

    #     except Exception as ex:
    #         return False, "service_delete() error!"
    #     return True, "OK"
