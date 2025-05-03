from datetime import datetime, timezone, timedelta

from isapilib.external.utilities import get_utc_offset
from isapilib.models import Venta


class DateAfterTodayValidator:
    requires_context = False

    def __call__(self, value):
        fecha_requerida = value['fecha_requerida']
        current_date = datetime.now(tz=timezone.utc) + timedelta(minutes=get_utc_offset())
        if fecha_requerida < current_date:
            raise Exception('The date must be after the current date')

        return value


class NoDuplicateAppointmentsValidator:
    requires_context = False

    def __call__(self, value):
        filters = {
            'mov': 'Cita Servicio',
            'agente': value['agente'],
            'fecha_requerida__date': value['fecha_requerida'].date(),
            'hora_recepcion': value['hora_recepcion'],
            'estatus': 'CONFIRMAR'
        }
        if Venta.objects.filter(**filters).exists():
            raise Exception('This appointment has already been scheduled')
