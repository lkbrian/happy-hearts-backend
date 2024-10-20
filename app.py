from models import (
    Appointment,
    Child,
    Parent,
    Payment,
    Provider,
    Record,
    User,
    Vaccine,
    Medical_info_parent,
    Medications,
    Delivery,
    Discharge_summary,
    Present_pregnancy,
    Previous_pregnancy,
    Prescription,
    Medicine,
)
from config import api, app, scheduler
from routes.appointmentsAPI import (
    appointmentsAPI,
    AppointmentForParent,
    AppointmentForProvider,
)
from routes.authAPI import Home, Login, Logout
from routes.childrenAPI import ChildrenAPI, ChildByParentIdAPI
from routes.parentsAPI import parentsAPI
from routes.providersAPI import providersAPI
from routes.usersAPI import UserAPI
from routes.vaccinesAPI import vaccinesAPI
from routes.deliveryAPI import DeliveryAPI, DeliveryForProvider, DeliveryForParent
from routes.medicationAPI import MedicationsAPI
from routes.resetAPI import ForgotPassword, ResetPassword
from routes.dischargeAPI import DischargeSummaryAPI
from routes.medicalinfoAPI import MedicalInfoParentAPI
from routes.paymentAPI import PaymentAPI
from routes.labtestAPI import (
    LabTestAPI,
    LabTestsForChild,
    LabTestsForParents,
    LabTestsForProviders,
)
from routes.recordsAPI import RecordsApi
from routes.presentpregnancyAPI import PresentPregnancyAPI
from routes.PrescriptionAPI import PrescriptionAPI
from routes.MedicineAPI import MedicineAPI
from routes.DocumentAPI import DocumentAPI, GetDocumentForChildByParent
from routes.admissionAPI import AdmissionAPI
from routes.RoomApi import RoomAPI, AvailableRooms
from routes.BedAPI import BedAPI, AvailableBedsForRoom
from utils.customs import update_appointment_statuses

api.add_resource(Home, "/")
api.add_resource(UserAPI, "/users", "/users/<int:id>")
api.add_resource(ChildrenAPI, "/children", "/children/<int:id>", endpoint="get")
api.add_resource(
    ChildByParentIdAPI, "/children/getbyparentid/<int:id>", methods=["GET"]
)
api.add_resource(parentsAPI, "/parents", "/parents/<int:id>")
api.add_resource(providersAPI, "/providers", "/providers/<int:id>")
api.add_resource(appointmentsAPI, "/appointments", "/appointments/<int:id>")
api.add_resource(AppointmentForParent, "/appointments_for_parent/<int:id>")
api.add_resource(AppointmentForProvider, "/appointments_for_provider/<int:id>")
api.add_resource(RecordsApi, "/records", "/records/<int:id>")
api.add_resource(vaccinesAPI, "/vaccines", "/vaccines/<int:id>")
api.add_resource(DeliveryAPI, "/deliveries", "/deliveries/<int:id>")
api.add_resource(DeliveryForProvider, "/deliveries_for_provider/<int:id>")
api.add_resource(DeliveryForParent, "/deliveries_for_parent/<int:id>")
api.add_resource(MedicationsAPI, "/medications", "/medications/<int:id>")
api.add_resource(
    DischargeSummaryAPI, "/discharge_summaries", "/discharge_summaries/<int:id>"
)
api.add_resource(AdmissionAPI, "/admissions", "/admissions/<int:id>")
api.add_resource(MedicalInfoParentAPI, "/medical_info", "/medical_info/<int:id>")
api.add_resource(
    PresentPregnancyAPI, "/present_pregnancies", "/present_pregnancies/<int:id>"
)
api.add_resource(PaymentAPI, "/payments", "/payments/<int:id>")
api.add_resource(LabTestAPI, "/labtests", "/labtests/<int:id>")
api.add_resource(LabTestsForChild, "/labtests_for_child/<int:id>")
api.add_resource(LabTestsForParents, "/labtests_for_parent/<int:id>")
api.add_resource(LabTestsForProviders, "/labtests_for_provider/<int:id>")
api.add_resource(PrescriptionAPI, "/prescriptions", "/prescriptions/<int:id>")
api.add_resource(MedicineAPI, "/medicines", "/medicines/<int:id>")
api.add_resource(ForgotPassword, "/forgot_password")
api.add_resource(ResetPassword, "/reset_password")
api.add_resource(
    GetDocumentForChildByParent,
    "/documents/<int:parent_id>/<int:child_id>",
)
api.add_resource(DocumentAPI, "/documents", "/documents/<int:id>")
api.add_resource(RoomAPI, "/rooms", "/rooms/<int:id>")
api.add_resource(AvailableRooms, "/available_rooms")
api.add_resource(BedAPI, "/beds", "/beds/<int:id>")
api.add_resource(AvailableBedsForRoom, "/available_beds/<int:id>")
# Adding routes for fetching by filename and user ID
api.add_resource(
    DocumentAPI, "/documents/name/<string:filename>", endpoint="get_by_filename"
)
api.add_resource(DocumentAPI, "/documents/user/<int:user_id>", endpoint="get_by_parent")
api.add_resource(
    DocumentAPI, "/documents/user/<int:user_id>", endpoint="get_by_provider"
)

api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
scheduler.add_job(
    update_appointment_statuses,
    # "cron", hour="8,17",
    "interval",
    minutes=1200,
)

if __name__ == "__main__":
    scheduler.start()
    app.run(port=5555, debug=True)
    # scheduler.start()
