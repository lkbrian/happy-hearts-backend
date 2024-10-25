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
    )
    serialize_rules = ("-provider.deliveries", "-parent.delivery")

    delivery_id = db.Column(db.Integer, primary_key=True)
    mode_of_delivery = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    duration_of_labour = db.Column(db.String, nullable=False)
    condition_of_mother = db.Column(db.String, nullable=False)
    condition_of_baby = db.Column(db.String, nullable=False)
    weight_at_birth = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey("providers.provider_id"))

    provider = db.relationship("Provider", back_populates="deliveries")

    parent_id = db.Column(db.Integer, db.ForeignKey("parents.parent_id"))
    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)

    parent = db.relationship("Parent", back_populates="delivery")


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
        "parent_id",
        "timestamp",
    )
    serialize_rules = (
        "-provider.medications",
        "-parent.medications",
    )
    medication_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)
    size_in_mg = db.Column(db.Integer, nullable=True)
    dose_in_mg = db.Column(db.Integer, nullable=True)
    route = db.Column(db.String, nullable=True)
    dose_per_day = db.Column(db.String, nullable=True)
    referral = db.Column(db.String, nullable=True)

    provider_id = db.Column(db.Integer, db.ForeignKey("providers.provider_id"))

    provider = db.relationship("Provider", back_populates="medications")

    parent_id = db.Column(db.Integer, db.ForeignKey("parents.parent_id"))
    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)

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
        "parent_id",
        "timestamp",
    )
    serialize_rules = ("-parent.present_pregnacy",)

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

    parent_id = db.Column(db.Integer, db.ForeignKey("parents.parent_id"))
    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)

    parent = db.relationship("Parent", back_populates="present_pregnacy")


class Previous_pregnancy(db.Model, SerializerMixin):
    __tablename__ = "previous_pregnancies"

    pp_id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    maturity = db.Column(db.String, nullable=False)
    duration_of_labour = db.Column(db.String, nullable=False)
    type_of_delivery = db.Column(db.String, nullable=False)
    Weight_in_kg = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=False)
    fate = db.Column(db.String, nullable=False)
    peurperium = db.Column(db.String, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("parents.parent_id"))
    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)

    parent = db.relationship("Parent", back_populates="previous_pregnancy")

    def to_dict(self):
        # Re-arrange the order of fields manually to ensure the parent details come first
        return {
            "parent_id": self.parent_id,
            "name": self.name,
            "email": self.email,
            "phone_number": self.phone_number,
            "address": self.address,
            "national_id": self.national_id,
            "passport": self.passport,
            "occupation": self.occupation,
            "marital_status": self.marital_status,
            "gender": self.gender,
            # Now include other related sections
            "appointments": [a.to_dict() for a in self.appointments],
            "children": [c.to_dict() for c in self.children],
            "medical_info_parent": [m.to_dict() for m in self.medical_info_parent],
            "lab_tests": [lab.to_dict() for lab in self.lab_tests],
            "medications": [med.to_dict() for med in self.medications],
            "payments": [p.to_dict() for p in self.payments],
            "present_pregnancy": [pp.to_dict() for pp in self.present_pregnancy],
            "previous_pregnancy": [
                prevp.to_dict() for prevp in self.previous_pregnancy
            ],
            "vaccination_records": [v.to_dict() for v in self.vaccination_records],
            "delivery": [d.to_dict() for d in self.delivery],
            "discharge_summaries": [ds.to_dict() for ds in self.discharge_summaries],
        }
