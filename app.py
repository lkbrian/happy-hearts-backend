from models import  Appointment,Child,Parent,Payment,Provider,Record,User,Vaccine,Medical_info_parent,Medications,Delivery,Discharge_summary,Present_pregnancy,Previous_pregnancy
from config import api, app,scheduler
from routes.appointmentsAPI import appointmentsAPI
from routes.authAPI import Home,Login, Logout
from routes.childrenAPI import ChildrenAPI
from routes.parentsAPI import parentsAPI
from routes.providersAPI import providersAPI
from routes.usersAPI import UserAPI
from routes.vaccinesAPI import vaccinesAPI
from routes.deliveryAPI import DeliveryAPI
from routes.medicationAPI import MedicationsAPI
from routes.resetAPI import ForgotPassword,ResetPassword
from routes.dischargeAPI import DischargeSummaryAPI
from routes.medicalinfoAPI import MedicalInfoParentAPI
from routes.paymentAPI import PaymentAPI
from routes.labtestAPI import LabTestAPI
from routes.recordsAPI import RecordsApi
from routes.presentpregnancyAPI import PresentPregnancyAPI
from utils.customs import update_appointment_statuses

api.add_resource(Home,"/")
api.add_resource(UserAPI,'/users',"/users/<int:id>")
api.add_resource(ChildrenAPI,'/children',"/children/<int:id>")
api.add_resource(parentsAPI,"/parents", "/parents/<int:id>")
api.add_resource(providersAPI,"/providers", "/providers/<int:id>")
api.add_resource(appointmentsAPI,"/appointments","/appointments/<int:id>")
api.add_resource(RecordsApi,"/records","/records/<int:id>")
api.add_resource(vaccinesAPI,"/vaccines","/vaccines/<int:id>")
api.add_resource(DeliveryAPI, "/deliveries", "/deliveries/<int:id>")
api.add_resource(MedicationsAPI, "/medications", "/medications/<int:id>")
api.add_resource(DischargeSummaryAPI,"/discharge_summaries","/discharge_summaries/<int:id>")
api.add_resource(MedicalInfoParentAPI,'/medical_info','/medical_info/<int:id>')
api.add_resource(PresentPregnancyAPI,'/present_pregnancies','/present_pregnancies/<int:id>')
api.add_resource(PaymentAPI,"/payments",'/payments/<int:id>')
api.add_resource(LabTestAPI,"/labtests","/labtests/<int:id>")
api.add_resource(ForgotPassword,"/forgot_password")
api.add_resource(ResetPassword,"/reset_password")
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
scheduler.add_job(update_appointment_statuses, "interval", hours=24)

if __name__ == "__main__":
    scheduler.start()
    app.run(port=5555,debug=True)
