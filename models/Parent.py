from datetime import datetime

from config import db
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import check_password_hash, generate_password_hash

import pytz

EAT = pytz.timezone("Africa/Nairobi")


# Function to return the current time in EAT
def current_eat_time():
    return datetime.now(EAT)


class Parent(db.Model, SerializerMixin):
    __tablename__ = "parents"
    serialize_only = (
        "parent_id",
        "name",
        "email",
        "role",
        "national_id",
        "phone_number",
        "gender",
        "marital_status",
        "address",
        "occupation",
        "passport",
        "next_of_kin",
        "kin_phone_number",
        "kin_email",
        "kin_occupation",
        "timestamp",
        # "vaccination_records",
        # "appointments",
        # "children",
        # "present_pregnacy",
        # "previous_pregnancy",
        # "payments",
        # "medications",
        # "medical_info_parent",
        # "delivery",
        # "discharge_summaries",
        # "lab_tests",
        # "prescriptions",
    )
    serialize_rules = (
        "-password_hash",
        "-children.parent_info",
        "-vaccination_records.parent",
        "-appointments.parent",
        "-present_pregnacy.parent",
        "-previous_pregnancy.parent",
        "-payments.parent",
        "-medications.parent",
        "-medical_info_parent.parent",
        "-delivery.parent",
        "-discharge_summaries.parent",
        "-reset_tokens.parent",
        "-lab_tests.parent",
        "-prescriptions.parent",
        "-documents.parent",
        "-admissions.parent",
        "-births.parent",
        "-prescriptions.parent",
    )

    parent_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(70), nullable=False, unique=True)
    role = db.Column(db.String, default="parent", nullable=False)
    national_id = db.Column(db.Integer, unique=True, nullable=False)
    phone_number = db.Column(db.Integer, nullable=False, unique=True)
    gender = db.Column(db.String, nullable=False)
    marital_status = db.Column(db.String, nullable=True, default="")
    address = db.Column(db.String, nullable=True, default="")
    occupation = db.Column(db.String, nullable=True, default="")
    next_of_kin = db.Column(db.String, nullable=True)
    kin_phone_number = db.Column(db.Integer, nullable=True)
    kin_email = db.Column(db.String, nullable=True)
    kin_occupation = db.Column(db.String, nullable=True)

    passport = db.Column(
        db.String,
        nullable=False,
        default="https://res.cloudinary.com/dg6digtc4/image/upload/w_1000,c_fill,ar_1:1,g_auto,r_max,bo_5px_solid_red,b_rgb:262c35/v1722952459/profile_xkjsxh.jpg",
    )
    password_hash = db.Column(db.String, nullable=False)

    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)

    vaccination_records = db.relationship(
        "Record", back_populates="parent", cascade="all, delete-orphan"
    )

    appointments = db.relationship(
        "Appointment", back_populates="parent", cascade="all, delete-orphan"
    )

    children = db.relationship(
        "Child", back_populates="parent", cascade="all, delete-orphan"
    )
    present_pregnacy = db.relationship(
        "Present_pregnancy", back_populates="parent", cascade="all,delete-orphan"
    )
    previous_pregnancy = db.relationship(
        "Previous_pregnancy", back_populates="parent", cascade="all,delete-orphan"
    )

    payments = db.relationship(
        "Payment", back_populates="parent", cascade="all, delete-orphan"
    )
    medications = db.relationship("Medications", back_populates="parent")

    medical_info_parent = db.relationship(
        "Medical_info_parent", back_populates="parent", cascade="all,delete-orphan"
    )

    delivery = db.relationship(
        "Delivery", back_populates="parent", cascade="all, delete-orphan"
    )
    documents = db.relationship("Document", back_populates="parent", lazy=True)

    admissions = db.relationship(
        "Admission", back_populates="parent", cascade="all, delete-orphan"
    )
    discharge_summaries = db.relationship(
        "Discharge_summary", back_populates="parent", cascade="all, delete-orphan"
    )
    reset_tokens = db.relationship("ResetToken", back_populates="parent")
    lab_tests = db.relationship("LabTest", back_populates="parent", lazy=True)
    prescriptions = db.relationship("Prescription", back_populates="parent", lazy=True)
    births = db.relationship("Birth", back_populates="parent")
    messages = db.relationship("Message", back_populates="parent")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Delivery(db.Model, SerializerMixin):
    __tablename__ = "deliveries"
    serialize_only = (
        "delivery_id",
        "mode_of_delivery",
        "date",
        "duration_of_labour",
        "condition_of_mother",
        "condition_of_baby",
        "weight_at_birth",
        "gender",
        "provider_id",
        "parent_id",
        "parent.national_id",
        "parent.name",
        "parent.email",
        "parent.marital_status",
        "provider.name",
    )
    serialize_rules = (
        "-provider.deliveries",
        "-parent.delivery",
        "-present_pregnancy.delivery",
    )

    delivery_id = db.Column(db.Integer, primary_key=True)
    mode_of_delivery = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    duration_of_labour = db.Column(db.String, nullable=False)
    condition_of_mother = db.Column(db.String, nullable=False)
    condition_of_baby = db.Column(db.String, nullable=False)
    weight_at_birth = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)
    fate = db.Column(db.String, nullable=False)
    remarks = db.Column(db.String, nullable=True)
    type_of_birth = db.Column(db.Integer, nullable=False)

    provider_id = db.Column(db.Integer, db.ForeignKey("providers.provider_id"))
    parent_id = db.Column(db.Integer, db.ForeignKey("parents.parent_id"))
    present_pregnancy_id = db.Column(
        db.Integer, db.ForeignKey("present_pregnancies.pp_id")
    )
    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)

    provider = db.relationship("Provider", back_populates="deliveries")
    parent = db.relationship("Parent", back_populates="delivery")
    present_pregnancy = db.relationship("Present_pregnancy", back_populates="delivery")
    previous_pregnancy = db.relationship(
        "Previous_pregnancy", back_populates="delivery", uselist=False
    )
    births = db.relationship("Birth", back_populates="delivery")


class Admission(db.Model, SerializerMixin):
    __tablename__ = "admissions"

    serialize_only = (
        "admission_id",
        "admission_date",
        "parent_id",
        "parent.national_id",
        "child_id",
        "child.certificate_No",
        "reason_for_admission",
        "general_assessment",
        "initial_treatment_plan",
        "room_id",
        "room.room_number",
        "bed_id",
        "bed.bed_number",
        "insurance_details",
        "provider.name",
        "timestamp",
    )
    serialize_rules = (
        "-parent.admissions",
        "-child.admissions",
    )

    admission_id = db.Column(db.Integer, primary_key=True)
    admission_date = db.Column(db.DateTime, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("parents.parent_id"))
    provider_id = db.Column(db.Integer, db.ForeignKey("providers.provider_id"))
    child_id = db.Column(db.Integer, db.ForeignKey("children.child_id"), nullable=True)
    reason_for_admission = db.Column(db.String, nullable=False)
    general_assessment = db.Column(db.String, nullable=True)
    initial_treatment_plan = db.Column(db.String, nullable=True)
    insurance_details = db.Column(db.String, nullable=True)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.room_id"), nullable=False)
    bed_id = db.Column(db.Integer, db.ForeignKey("beds.bed_id"), nullable=False)
    is_discharged = db.Column(db.Boolean, nullable=False, default=False)
    # Existing relationships...

    bed = db.relationship("Bed", back_populates="admission")
    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)

    room = db.relationship("Room", back_populates="admissions")
    parent = db.relationship("Parent", back_populates="admissions")
    provider = db.relationship("Provider", back_populates="admissions")
    child = db.relationship("Child", back_populates="admissions")


class Discharge_summary(db.Model, SerializerMixin):
    __tablename__ = "discharge_summaries"

    serialize_only = (
        "discharge_id",
        "admission_id",  # Added to link to Admission
        "admission_date",
        "discharge_date",
        "discharge_diagnosis",
        "procedure",
        "parent_id",
        "child_id",
        "provider_id",
        "provider.name" "timestamp",
    )
    serialize_rules = (
        "-provider.discharge_summaries",
        "-parent.discharge_summaries",
        "-child.discharge_summaries",
    )

    discharge_id = db.Column(db.Integer, primary_key=True)
    admission_id = db.Column(
        db.Integer, db.ForeignKey("admissions.admission_id"), nullable=False
    )  # Link to Admission
    admission_date = db.Column(db.DateTime, nullable=False)
    discharge_date = db.Column(db.DateTime, nullable=False)
    discharge_diagnosis = db.Column(db.String, nullable=False)
    procedure = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)

    provider_id = db.Column(db.Integer, db.ForeignKey("providers.provider_id"))
    provider = db.relationship("Provider", back_populates="discharge_summaries")

    parent_id = db.Column(db.Integer, db.ForeignKey("parents.parent_id"))
    parent = db.relationship("Parent", back_populates="discharge_summaries")

    child_id = db.Column(db.Integer, db.ForeignKey("children.child_id"), nullable=True)
    child = db.relationship("Child", back_populates="discharge_summaries")


class Medical_info_parent(db.Model, SerializerMixin):
    __tablename__ = "parents_medical_info"
    serialize_only = (
        "history_id",
        "blood_transfusion",
        "family_history",
        "twins",
        "tuberclosis",
        "diabetes",
        "hypertension",
        "parent_id",
    )
    serialize_rules = ("-parent.medical_info_parent",)
    history_id = db.Column(db.Integer, primary_key=True)
    blood_transfusion = db.Column(db.String, nullable=True)
    family_history = db.Column(db.String, nullable=True)
    twins = db.Column(db.String, nullable=True)
    tuberclosis = db.Column(db.String, nullable=True)
    diabetes = db.Column(db.String, nullable=True)
    hypertension = db.Column(db.String, nullable=True)

    parent_id = db.Column(db.Integer, db.ForeignKey("parents.parent_id"))

    parent = db.relationship("Parent", back_populates="medical_info_parent")


class Medications(db.Model, SerializerMixin):
    __tablename__ = "discharge_medications"
    serialize_only = (
        "medication_id",
        "name",
        "size_in_mg",
        "dose_in_mg",
        "route",
        "dose_per_day",
        "referral",
        "provider_id",
        "child_id",
        "parent_id",
        "timestamp",
    )
    serialize_rules = (
        "-provider.medications",
        "-parent.medications",
        "-child.medications",
        "-prescription.medications",
    )
    medication_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)
    size_in_mg = db.Column(db.Integer, nullable=True)
    dose_in_mg = db.Column(db.Integer, nullable=True)
    route = db.Column(db.String, nullable=True)
    dose_per_day = db.Column(db.String, nullable=True)
    referral = db.Column(db.String, nullable=True)
    provider_id = db.Column(db.Integer, db.ForeignKey("providers.provider_id"))
    parent_id = db.Column(db.Integer, db.ForeignKey("parents.parent_id"), nullable=True)
    child_id = db.Column(db.Integer, db.ForeignKey("children.child_id"), nullable=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey("medicines.medicine_id"))
    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)
    prescription_id = db.Column(
        db.Integer, db.ForeignKey("prescriptions.prescription_id"), nullable=True
    )

    prescription = db.relationship(
        "Prescription", back_populates="medications", lazy=True
    )
    medicine = db.relationship("Medicine", back_populates="medications")

    child = db.relationship("Child", back_populates="medications")
    provider = db.relationship("Provider", back_populates="medications")
    parent = db.relationship("Parent", back_populates="medications")


class Present_pregnancy(db.Model, SerializerMixin):
    __tablename__ = "present_pregnancies"
    serialize_only = (
        "pp_id",
        "date",
        "weight_in_kg",
        "urinalysis",
        "blood_pressure",
        "pollar",
        "maturity_in_weeks",
        "fundal_height",
        "comments",
        "clinical_notes",
        "is_delivered",
        "parent_id",
        "parent.national_id",
        "provider_id",
        "provider.name",
        "timestamp",
    )
    serialize_rules = (
        "-parent.present_pregnacy",
        "-provider.present_pregnancies",
        "-delivery.present_pregnancies",
    )

    pp_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    weight_in_kg = db.Column(db.Integer, nullable=False)
    urinalysis = db.Column(db.String, nullable=False)
    blood_pressure = db.Column(db.String, nullable=False)
    pollar = db.Column(db.String, nullable=False)
    maturity_in_weeks = db.Column(db.Integer, nullable=False)
    fundal_height = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.String, nullable=False)
    clinical_notes = db.Column(db.String, nullable=False)
    is_delivered = db.Column(db.Boolean, nullable=False, default=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("parents.parent_id"))
    provider_id = db.Column(db.Integer, db.ForeignKey("providers.provider_id"))
    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)

    parent = db.relationship("Parent", back_populates="present_pregnacy")
    provider = db.relationship("Provider", back_populates="present_pregnancies")
    delivery = db.relationship(
        "Delivery", back_populates="present_pregnancy", uselist=False
    )


class Previous_pregnancy(db.Model, SerializerMixin):
    __tablename__ = "previous_pregnancies"
    serialize_only = (
        "pp_id",
        "year",
        "maturity",
        "duration_of_labour",
        "type_of_delivery",
        "weight_in_kg",
        "gender",
        "fate",
        "puerperium",
        "parent_id",
        "provider_id",
        "timestamp",
        "delivery_id",
    )
    serialize_rules = (
        "-delivery.previous_pregnancy",
        "-parent.previous_pregnancy",
        "-provider.previous_pregnancy",
    )

    pp_id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    maturity = db.Column(db.String, nullable=False)
    duration_of_labour = db.Column(db.String, nullable=False)
    type_of_delivery = db.Column(db.String, nullable=False)
    weight_in_kg = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=False)
    fate = db.Column(db.String, nullable=False)
    puerperium = db.Column(db.String, nullable=False)

    parent_id = db.Column(db.Integer, db.ForeignKey("parents.parent_id"))
    provider_id = db.Column(db.Integer, db.ForeignKey("providers.provider_id"))
    delivery_id = db.Column(db.Integer, db.ForeignKey("deliveries.delivery_id"))
    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)

    parent = db.relationship("Parent", back_populates="previous_pregnancy")
    provider = db.relationship("Provider", back_populates="previous_pregnancies")
    delivery = db.relationship("Delivery", back_populates="previous_pregnancy")


class Birth(db.Model, SerializerMixin):
    __tablename__ = "births"

    # Attributes for serialization
    serialize_only = (
        "birth_id",
        "delivery_id",
        "baby_name",
        "date_of_birth",
        "date_of_notification",
        "place_of_birth",
        "weight",
        "serial_number",
        "sub_county",
        "gender",
        "fate",
        "mother_full_name",
        "mother_national_id",
        "father_full_name",
        "father_national_id",
        "type_of_birth",
        "is_registered",
        "parent_id",
        "provider_id",
    )
    serialize_rules = ("-provider.births", "-parent.births", "-delivery.births")

    birth_id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(
        db.Integer, db.ForeignKey("deliveries.delivery_id"), nullable=False
    )
    baby_name = db.Column(db.String, nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    place_of_birth = db.Column(db.String, nullable=False)
    sub_county = db.Column(db.String, nullable=False)
    serial_number = db.Column(db.Integer, nullable=False, unique=True)
    weight = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)
    fate = db.Column(db.String, nullable=False)
    mother_full_name = db.Column(db.String, nullable=False)
    mother_national_id = db.Column(db.String, nullable=False)
    father_full_name = db.Column(db.String, nullable=True)
    father_national_id = db.Column(db.String, nullable=True)
    type_of_birth = db.Column(db.String, nullable=False)

    is_registered = db.Column(db.Boolean, nullable=False, default=False)
    date_of_notification = db.Column(
        db.DateTime, nullable=False, default=current_eat_time
    )

    provider_id = db.Column(db.Integer, db.ForeignKey("providers.provider_id"))
    parent_id = db.Column(db.Integer, db.ForeignKey("parents.parent_id"))

    # Relationships
    provider = db.relationship("Provider", back_populates="births")
    parent = db.relationship("Parent", back_populates="births")
    delivery = db.relationship("Delivery", back_populates="births")
