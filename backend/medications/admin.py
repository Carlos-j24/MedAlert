from django.contrib import admin

from .models import CaregiverProfile
from .models import Patient
from .models import Medication
from .models import Reminder
from .models import MedicationHistory
from .models import MedicalAppointment

admin.site.register(CaregiverProfile)
admin.site.register(Patient)
admin.site.register(Medication)
admin.site.register(Reminder)
admin.site.register(MedicationHistory)
admin.site.register(MedicalAppointment)