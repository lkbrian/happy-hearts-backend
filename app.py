from config import api, app, scheduler
from models import (
    Appointment,
    Child,
    Delivery,
    Discharge_summary,
    Medical_info_parent,
    Medications,
    Medicine,
    Parent,
    Payment,
    Prescription,
    Present_pregnancy,
    Previous_pregnancy,
    Provider,
    Record,
    User,
    Vaccine,
)
from routes.admissionAPI import AdmissionAPI, AdmissionForParent, AdmissionForProvider
from routes.appointmentsAPI import (
    AppointmentForParent,
    AppointmentForProvider,
    appointmentsAPI,
)
from routes.authAPI import Home, Login, Logout
from routes.BedAPI import AvailableBedsForRoom, BedAPI
from routes.birthAPI import BirthAPI, BirthForParent, BirthForProvider
from routes.childrenAPI import ChildByParentIdAPI, ChildrenAPI
from routes.deliveryAPI import DeliveryAPI, DeliveryForParent, DeliveryForProvider
from routes.dischargeAPI import (
    DischargeForParent,
    DischargeForProvider,
    DischargeSummaryAPI,
)
from routes.DocumentAPI import (
    DocumentAPI,
    DocumentByParent,
    DocumentByParentOnly,
    DocumentByProvider,
    DocumentsByParentAndChild,
)
from routes.labtestAPI import (
    LabTestAPI,
    LabTestsForChild,
    LabTestsForParents,
    LabTestsForProviders,
)
from routes.medicalinfoAPI import MedicalInfoForParent, MedicalInfoParentAPI
from routes.medicationAPI import (
    MedicationForChild,
    MedicationForParents,
    MedicationForProviders,
    MedicationsAPI,
)
from routes.MedicineAPI import MedicineAPI
from routes.parentsAPI import parentsAPI
from routes.paymentAPI import PaymentAPI
from routes.PrescriptionAPI import (
    PrescriptionAPI,
    PrescriptionForChild,
    PrescriptionForParent,
    PrescriptionForProvider,
)
from routes.presentpregnancyAPI import (
    PresentPregnancyAPI,
    PresentPregnancyForParent,
    PresentPregnancyForProvider,
)
from routes.previouspregnancyAPI import (
    PreviousPregnancyAPI,
    PreviousPregnancyForParent,
    PreviousPregnancyForProvider,
)
from routes.providersAPI import providersAPI
from routes.recordsAPI import (
    RecordsApi,
    VaccinationRecordsForParent,
    VaccinationRecordsForProvider,
)
from routes.resetAPI import EmailChange, ForgotPassword, ResetPassword
from routes.RoomAPI import AvailableRooms, RoomAPI
from routes.usersAPI import UserAPI
from routes.MesseagesAPI import MessageAPI
from routes.vaccinesAPI import vaccinesAPI
from utils.customs import update_appointment_statuses

api.add_resource(Home, "/")
api.add_resource(UserAPI, "/users", "/users/<int:id>")
api.add_resource(ChildrenAPI, "/children", "/children/<int:id>", endpoint="get")
api.add_resource(ChildByParentIdAPI, "/children/parent/<int:id>", methods=["GET"])
api.add_resource(parentsAPI, "/parents", "/parents/<int:id>")
api.add_resource(providersAPI, "/providers", "/providers/<int:id>")

api.add_resource(appointmentsAPI, "/appointments", "/appointments/<int:id>")
api.add_resource(AppointmentForParent, "/appointments/parent/<int:id>")
api.add_resource(AppointmentForProvider, "/appointments/provider/<int:id>")

api.add_resource(BirthAPI, "/births", "/births/<int:id>")
api.add_resource(BirthForParent, "/births/parent/<int:id>")
api.add_resource(BirthForProvider, "/births/provider/<int:id>")

api.add_resource(RecordsApi, "/records", "/records/<int:id>")
api.add_resource(VaccinationRecordsForProvider, "/records/provider/<int:id>")
api.add_resource(VaccinationRecordsForParent, "/records/parent/<int:id>")

api.add_resource(vaccinesAPI, "/vaccines", "/vaccines/<int:id>")

api.add_resource(DeliveryAPI, "/deliveries", "/deliveries/<int:id>")
api.add_resource(DeliveryForProvider, "/deliveries/provider/<int:id>")
api.add_resource(DeliveryForParent, "/deliveries/parent/<int:id>")

api.add_resource(MedicationsAPI, "/medications", "/medications/<int:id>")
api.add_resource(MedicationForChild, "/medications/child/<int:id>")
api.add_resource(MedicationForParents, "/medications/parent/<int:id>")
api.add_resource(MedicationForProviders, "/medications/provider/<int:id>")

api.add_resource(
    DischargeSummaryAPI, "/discharge_summaries", "/discharge_summaries/<int:id>"
)
api.add_resource(DischargeForParent, "/discharge_summaries/parent/<int:id>")
api.add_resource(DischargeForProvider, "/discharge_summaries/provider/<int:id>")

api.add_resource(AdmissionAPI, "/admissions", "/admissions/<int:id>")
api.add_resource(AdmissionForProvider, "/admissions/provider/<int:id>")
api.add_resource(AdmissionForParent, "/admissions/parent/<int:id>")
api.add_resource(MedicalInfoParentAPI, "/medical_info", "/medical_info/<int:id>")
api.add_resource(MedicalInfoForParent, "/medical_info/parent/<int:id>")


api.add_resource(
    PresentPregnancyAPI, "/present_pregnancies", "/present_pregnancies/<int:id>"
)
api.add_resource(PresentPregnancyForParent, "/present_pregnancies/parent/<int:id>")
api.add_resource(PresentPregnancyForProvider, "/present_pregnancies/provider/<int:id>")

api.add_resource(
    PreviousPregnancyAPI, "/previous_pregnancies", "/previous_pregnancies/<int:id>"
)
api.add_resource(
    PreviousPregnancyForProvider, "/previous_pregnancies/provider/<int:id>"
)
api.add_resource(PreviousPregnancyForParent, "/previous_pregnancies/parent/<int:id>")


api.add_resource(PaymentAPI, "/payments", "/payments/<int:id>")

api.add_resource(LabTestAPI, "/labtests", "/labtests/<int:id>")
api.add_resource(LabTestsForChild, "/labtests/child/<int:id>")
api.add_resource(LabTestsForParents, "/labtests/parent/<int:id>")
api.add_resource(LabTestsForProviders, "/labtests/provider/<int:id>")

api.add_resource(PrescriptionAPI, "/prescriptions", "/prescriptions/<int:id>")
api.add_resource(PrescriptionForChild, "/prescriptions/child/<int:id>")
api.add_resource(PrescriptionForParent, "/prescriptions/parent/<int:id>")
api.add_resource(PrescriptionForProvider, "/prescriptions/provider/<int:id>")

api.add_resource(MedicineAPI, "/medicines", "/medicines/<int:id>")

api.add_resource(ForgotPassword, "/forgot_password")
api.add_resource(ResetPassword, "/reset_password")
api.add_resource(
    EmailChange, "/changeemail", "/verifyemail/<string:email>/<string:token>"
)

api.add_resource(DocumentAPI, "/documents", "/documents/<int:id>")
api.add_resource(DocumentByProvider, "/documents/provider/<int:id>")
api.add_resource(DocumentByParent, "/documents/parent/<int:id>")
api.add_resource(DocumentsByParentAndChild, "/documents/parent/child/<int:id>")
api.add_resource(DocumentByParentOnly, "/documents/only/parent/<int:id>")
api.add_resource(RoomAPI, "/rooms", "/rooms/<int:id>")
api.add_resource(AvailableRooms, "/available_rooms")
api.add_resource(BedAPI, "/beds", "/beds/<int:id>")
api.add_resource(AvailableBedsForRoom, "/availableroom/beds/<int:id>")
api.add_resource(MessageAPI, "/messages", "/messages/<int:id>")

api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
scheduler.add_job(
    update_appointment_statuses,
    "interval",
    hours=1,
)
scheduler.add_job(
    update_appointment_statuses,
    "cron",
    hour="8,17",
)

if __name__ == "__main__":
    scheduler.start()
    app.run(port=5555, debug=True)
    # scheduler.start()
