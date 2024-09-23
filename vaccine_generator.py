from models import Vaccine
from config import db,app
data = [
    {
        "name": "Hepatitis B (HepB)",
        "composition": "Hepatitis B surface antigen (HBsAg) adsorbed onto aluminum hydroxide.",
        "schedule": ["At birth", "1-2 months", "6-18 months"],
        "indication": "Prevents hepatitis B virus (HBV) infection.",
        "side_effects": ["Soreness at the injection site", "mild fever", "fatigue"],
        "additional_information": "HepB vaccination is recommended for all infants to prevent chronic HBV infection. It is highly effective and part of routine childhood immunization schedules.",
    },
    {
        "name": "DTaP (Diphtheria, Tetanus, and acellular Pertussis)",
        "composition": "Diphtheria and tetanus toxoids and acellular pertussis vaccine adsorbed onto aluminum phosphate.",
        "schedule": ["2 months", "4 months", "6 months", "15-18 months", "4-6 years"],
        "indication": "Prevents diphtheria, tetanus, and pertussis.",
        "side_effects": [
            "Fever",
            "swelling at the injection site",
            "mild fussiness or drowsiness",
        ],
        "additional_information": "DTaP vaccination is crucial for protection against these serious bacterial infections. Boosters are recommended every 10 years to maintain immunity.",
    },
    {
        "name": "IPV (Inactivated Poliovirus)",
        "composition": "Poliovirus types 1, 2, and 3.",
        "schedule": ["2 months", "4 months", "6-18 months", "4-6 years"],
        "indication": "Prevents poliomyelitis.",
        "side_effects": ["Injection site reactions", "fever"],
        "additional_information": "IPV is highly effective in preventing poliovirus infections and is administered as an injection. It's an essential part of global efforts to eradicate polio.",
    },
    {
        "name": "Hib (Haemophilus influenzae type b)",
        "composition": "Hib capsular polysaccharide conjugated to a carrier protein.",
        "schedule": ["2 months", "4 months", "6 months", "12-15 months"],
        "indication": "Prevents Hib infections (meningitis, pneumonia, epiglottitis).",
        "side_effects": ["Injection site reactions", "low-grade fever"],
        "additional_information": "Hib vaccination has dramatically reduced the incidence of Hib-related diseases since its introduction. It's safe and recommended as part of routine childhood immunizations.",
    },
    {
        "name": "PCV13 (Pneumococcal Conjugate)",
        "composition": "Polysaccharide capsular antigens of Streptococcus pneumoniae conjugated to a carrier protein.",
        "schedule": ["2 months", "4 months", "6 months", "12-15 months"],
        "indication": "Prevents pneumococcal diseases (pneumonia, meningitis).",
        "side_effects": ["Fever", "irritability", "injection site reactions"],
        "additional_information": "PCV13 protects against 13 strains of S. pneumoniae and is highly effective in reducing severe pneumococcal infections in children.",
    },
    {
        "name": "RV (Rotavirus)",
        "composition": "Live attenuated strains of rotavirus.",
        "schedule": ["2 months", "4 months"],
        "indication": "Prevents rotavirus gastroenteritis.",
        "side_effects": ["Temporary diarrhea or vomiting"],
        "additional_information": "RV vaccine is given orally and is highly effective in preventing severe diarrhea and dehydration caused by rotavirus infections.",
    },
    {
        "name": "Influenza (Flu)",
        "composition": "Inactivated or live attenuated influenza virus.",
        "schedule": ["Annually starting at 6 months"],
        "indication": "Prevents seasonal influenza.",
        "side_effects": ["Soreness at the injection site", "mild fever"],
        "additional_information": "Influenza vaccination is recommended annually, especially for high-risk groups, to protect against circulating flu viruses.",
    },
    {
        "name": "Varicella (Chickenpox)",
        "composition": "Live attenuated varicella virus.",
        "schedule": ["12-15 months", "4-6 years"],
        "indication": "Prevents chickenpox.",
        "side_effects": ["Soreness at the injection site", "mild rash"],
        "additional_information": "Varicella vaccine is highly effective in preventing chickenpox and its complications, including severe skin infections.",
    },
    {
        "name": "Tdap (Tetanus, Diphtheria, and acellular Pertussis)",
        "composition": "Tetanus toxoid, diphtheria toxoid, and acellular pertussis vaccine adsorbed onto aluminum phosphate.",
        "schedule": ["11-12 years"],
        "indication": "Booster for tetanus, diphtheria, and pertussis immunity.",
        "side_effects": ["Pain at the injection site", "mild fever"],
        "additional_information": "Tdap boosters are recommended every 10 years to maintain protection against these bacterial infections.",
    },
    {
        "name": "HPV (Human Papillomavirus)",
        "composition": "Virus-like particles (VLPs) composed of L1 capsid proteins from HPV types 6, 11, 16, and 18.",
        "schedule": [
            "11-12 years",
            "second dose 1-2 months later (if age 9-14 years)",
            "third dose 6 months after first dose (if age 9-14 years)",
        ],
        "indication": "Prevents HPV infection (causes cervical cancer, genital warts).",
        "side_effects": ["Pain at the injection site", "mild fever"],
        "additional_information": "HPV vaccination is most effective when started before sexual activity begins, offering protection against HPV-related cancers and diseases.",
    },
    {
        "name": "Meningococcal",
        "composition": "Purified polysaccharide of Neisseria meningitidis serogroups A, C, Y, and W-135 conjugated to diphtheria toxoid or protein.",
        "schedule": ["11-12 years (first dose)", "16 years (second dose)"],
        "indication": "Prevents meningococcal diseases (meningitis, septicemia).",
        "side_effects": ["Pain at the injection site", "mild fever"],
        "additional_information": "Meningococcal vaccination is recommended for adolescents to protect against these potentially deadly bacterial infections.",
    },
]

def vaccine_generator():
    for dataitems in data:
        vaccine = Vaccine(
            name=dataitems["name"],
            composition=dataitems["composition"],
            schedule=dataitems["schedule"],
            indication=dataitems["indication"],
            side_effects=dataitems["side_effects"],
            info=dataitems["additional_information"],
        )
        db.session.add(vaccine)
    db.session.commit()

with app.app_context():
    vaccine_generator()
