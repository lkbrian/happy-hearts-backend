from models import Medicine
from config import db, app

data = [
    {
        "name": "Paracetamol",
        "composition": "Acetaminophen 500mg",
        "indication": "Relief of mild to moderate pain and fever.",
        "side_effects": ["Nausea", "rash", "liver toxicity (in overdose)"],
        "dosage": "500mg every 4-6 hours (max 4g per day)",
    },
    {
        "name": "Ibuprofen",
        "composition": "Ibuprofen 200mg",
        "indication": "Pain relief, anti-inflammatory, fever reducer.",
        "side_effects": ["Stomach pain", "heartburn", "nausea"],
        "dosage": "200-400mg every 4-6 hours (max 1200mg per day)",
    },
    {
        "name": "Amoxicillin",
        "composition": "Amoxicillin 500mg",
        "indication": "Treats bacterial infections.",
        "side_effects": ["Diarrhea", "nausea", "rash"],
        "dosage": "500mg every 8 hours for 7-10 days",
    },
    {
        "name": "Cetirizine",
        "composition": "Cetirizine 10mg",
        "indication": "Relief of allergy symptoms (hay fever, itching, hives).",
        "side_effects": ["Drowsiness", "dry mouth", "headache"],
        "dosage": "10mg once daily",
    },
    {
        "name": "Metformin",
        "composition": "Metformin 500mg",
        "indication": "Management of type 2 diabetes.",
        "side_effects": ["Diarrhea", "nausea", "stomach upset"],
        "dosage": "500mg twice daily with meals",
    },
    {
        "name": "Aspirin",
        "composition": "Aspirin 81mg",
        "indication": "Prevention of heart attacks, stroke, blood clots.",
        "side_effects": ["Stomach pain", "bleeding", "nausea"],
        "dosage": "81mg once daily",
    },
    {
        "name": "Lisinopril",
        "composition": "Lisinopril 10mg",
        "indication": "Treatment of high blood pressure and heart failure.",
        "side_effects": ["Dizziness", "cough", "low blood pressure"],
        "dosage": "10mg once daily",
    },
    {
        "name": "Atorvastatin",
        "composition": "Atorvastatin 20mg",
        "indication": "Management of high cholesterol.",
        "side_effects": ["Muscle pain", "diarrhea", "nausea"],
        "dosage": "20mg once daily",
    },
    {
        "name": "Omeprazole",
        "composition": "Omeprazole 20mg",
        "indication": "Treatment of acid reflux, ulcers.",
        "side_effects": ["Headache", "nausea", "gas"],
        "dosage": "20mg once daily before a meal",
    },
    {
        "name": "Levothyroxine",
        "composition": "Levothyroxine 50mcg",
        "indication": "Treatment of hypothyroidism.",
        "side_effects": ["Hair loss", "insomnia", "weight changes"],
        "dosage": "50mcg once daily before breakfast",
    },
    {
        "name": "Salbutamol",
        "composition": "Salbutamol 100mcg per inhalation",
        "indication": "Relief of bronchospasm in asthma.",
        "side_effects": ["Tremors", "nervousness", "rapid heart rate"],
        "dosage": "1-2 puffs every 4-6 hours as needed",
    },
    {
        "name": "Ranitidine",
        "composition": "Ranitidine 150mg",
        "indication": "Treatment of ulcers, acid reflux.",
        "side_effects": ["Headache", "constipation", "diarrhea"],
        "dosage": "150mg twice daily",
    },
    {
        "name": "Amlodipine",
        "composition": "Amlodipine 5mg",
        "indication": "Treatment of high blood pressure.",
        "side_effects": ["Swelling", "fatigue", "dizziness"],
        "dosage": "5mg once daily",
    },
    {
        "name": "Prednisolone",
        "composition": "Prednisolone 5mg",
        "indication": "Treatment of inflammation, allergies, asthma.",
        "side_effects": ["Weight gain", "increased blood sugar", "mood changes"],
        "dosage": "5mg daily as directed by a doctor",
    },
    {
        "name": "Ciprofloxacin",
        "composition": "Ciprofloxacin 500mg",
        "indication": "Treatment of bacterial infections.",
        "side_effects": ["Diarrhea", "nausea", "dizziness"],
        "dosage": "500mg twice daily for 7-14 days",
    },
    {
        "name": "Clopidogrel",
        "composition": "Clopidogrel 75mg",
        "indication": "Prevention of blood clots in heart disease.",
        "side_effects": ["Bleeding", "bruising", "stomach pain"],
        "dosage": "75mg once daily",
    },
    {
        "name": "Simvastatin",
        "composition": "Simvastatin 20mg",
        "indication": "Management of high cholesterol.",
        "side_effects": ["Muscle pain", "constipation", "nausea"],
        "dosage": "20mg once daily in the evening",
    },
    {
        "name": "Gabapentin",
        "composition": "Gabapentin 300mg",
        "indication": "Treatment of nerve pain and seizures.",
        "side_effects": ["Dizziness", "drowsiness", "fatigue"],
        "dosage": "300mg three times daily",
    },
    {
        "name": "Hydrochlorothiazide",
        "composition": "Hydrochlorothiazide 25mg",
        "indication": "Treatment of high blood pressure.",
        "side_effects": ["Dizziness", "electrolyte imbalance", "dehydration"],
        "dosage": "25mg once daily",
    },
    {
        "name": "Losartan",
        "composition": "Losartan 50mg",
        "indication": "Treatment of high blood pressure.",
        "side_effects": ["Dizziness", "cough", "high potassium levels"],
        "dosage": "50mg once daily",
    },
]


def medicine_generator():
    for data_item in data:
        medicine = Medicine(
            name=data_item["name"],
            composition=data_item["composition"],
            indication=data_item["indication"],
            side_effects=", ".join(data_item["side_effects"]),
            dosage=data_item["dosage"],
        )
        db.session.add(medicine)
    db.session.commit()


with app.app_context():
    medicine_generator()
