# symptom_rules.py

# Large symptom list (120+)
SYMPTOMS = [
"fever","cough","fatigue","headache","nausea","vomiting","diarrhea","constipation",
"chest pain","shortness of breath","dizziness","sweating","joint pain","muscle pain",
"back pain","stomach pain","abdominal pain","loss of appetite","weight loss",
"weight gain","skin rash","itching","dry skin","sore throat","runny nose",
"congestion","blurred vision","red eyes","watering eyes","ear pain","hearing loss",
"difficulty swallowing","hoarseness","memory loss","confusion","anxiety",
"depression","insomnia","excessive thirst","frequent urination","night sweats",
"chills","shivering","yellow skin","yellow eyes","swelling","numbness","tingling",
"muscle weakness","burning urination","blood in urine","palpitations",
"rapid heartbeat","slow heartbeat","cold hands","cold feet","hair loss",
"brittle nails","bad breath","gum bleeding","tooth pain","jaw pain",
"neck pain","shoulder pain","hip pain","knee pain","ankle pain","foot pain",
"hand pain","finger pain","eye pain","light sensitivity","double vision",
"loss of balance","difficulty walking","tremors","speech difficulty",
"sleepiness","irritability","dry mouth","excess hunger","bloating",
"gas","heartburn","indigestion","rectal bleeding","black stool",
"pale skin","bruising","nose bleeding","chest tightness","wheezing",
"persistent cough","coughing blood","high blood pressure","low blood pressure",
"fainting","difficulty breathing","cold symptoms","flu symptoms",
"migraine","cluster headache","sinus pressure","sinus pain",
"swollen glands","lump in neck","ear ringing","ear discharge",
"skin redness","skin peeling","skin infection","skin swelling",
"burning sensation","sharp pain","dull pain","pressure in chest",
"throat pain","dry throat","sticky eyes","tearing eyes"
]


# Disease rules (45 diseases)
DISEASE_RULES = {

"Flu": ["fever","cough","fatigue","headache","chills"],
"Common Cold": ["runny nose","cough","sore throat","congestion"],
"COVID‑like Infection": ["fever","cough","shortness of breath","fatigue"],
"Food Poisoning": ["vomiting","diarrhea","abdominal pain","nausea"],
"Gastritis": ["stomach pain","heartburn","indigestion","bloating"],
"Migraine": ["headache","nausea","light sensitivity"],
"Sinusitis": ["sinus pain","headache","congestion","runny nose"],
"Bronchitis": ["persistent cough","chest tightness","fatigue"],
"Pneumonia": ["fever","chest pain","difficulty breathing","cough"],
"Asthma": ["wheezing","shortness of breath","chest tightness"],
"Hypertension": ["high blood pressure","headache","dizziness"],
"Hypotension": ["low blood pressure","dizziness","fainting"],
"Diabetes": ["excessive thirst","frequent urination","fatigue"],
"Anemia": ["fatigue","pale skin","shortness of breath"],
"Kidney Infection": ["burning urination","fever","back pain"],
"Urinary Tract Infection": ["burning urination","frequent urination"],
"Arthritis": ["joint pain","joint swelling","stiffness"],
"Muscle Strain": ["muscle pain","muscle weakness"],
"Back Injury": ["back pain","difficulty walking"],
"Gastroenteritis": ["vomiting","diarrhea","fever"],
"Appendicitis": ["abdominal pain","nausea","fever"],
"Heart Disease": ["chest pain","shortness of breath","palpitations"],
"Stroke Risk": ["speech difficulty","confusion","loss of balance"],
"Allergy": ["itching","runny nose","skin rash"],
"Skin Infection": ["skin redness","skin swelling","skin infection"],
"Eczema": ["dry skin","itching","skin redness"],
"Psoriasis": ["skin peeling","skin rash"],
"Eye Infection": ["red eyes","watering eyes","eye pain"],
"Glaucoma Risk": ["eye pain","blurred vision"],
"Depression": ["depression","insomnia","fatigue"],
"Anxiety Disorder": ["anxiety","palpitations","sweating"],
"Sleep Disorder": ["insomnia","sleepiness"],
"Thyroid Disorder": ["weight gain","weight loss","fatigue"],
"Liver Disease": ["yellow skin","yellow eyes"],
"Gallbladder Disease": ["abdominal pain","nausea"],
"Pancreatitis": ["abdominal pain","vomiting"],
"Cold Exposure": ["cold hands","cold feet","shivering"],
"Dehydration": ["dry mouth","dizziness","fatigue"],
"Malnutrition": ["weight loss","fatigue","hair loss"],
"Dental Infection": ["tooth pain","gum bleeding"],
"Ear Infection": ["ear pain","ear discharge"],
"Vertigo": ["dizziness","loss of balance"],
"Parkinson‑like Symptoms": ["tremors","difficulty walking"],
"Neuropathy": ["tingling","numbness"],
"Heat Exhaustion": ["sweating","dizziness","fatigue"]
}

SYMPTOM_SYNONYMS = {
    "headache": ["head hurts", "head pain", "migraine"],
    "fatigue": ["tired", "very tired", "exhausted"],
    "pale skin": ["skin looks pale", "pale face"],
    "fever": ["high temperature", "burning up"],
    "cough": ["coughing"],
    "nausea": ["feel like vomiting", "queasy"],
    "dizziness": ["lightheaded", "feel dizzy"],
    "depression": ["feel depressed", "very sad"],
    "shortness of breath": ["can't breathe well", "breathing problem"]
}


def check_symptoms(user_input):

    user_input = user_input.lower()

    detected_symptoms = []

    # detect main symptoms
    for symptom in SYMPTOMS:
        if symptom in user_input:
            detected_symptoms.append(symptom)

    # detect synonyms
    for symptom, words in SYMPTOM_SYNONYMS.items():
        for word in words:
            if word in user_input:
                detected_symptoms.append(symptom)

    detected_symptoms = list(set(detected_symptoms))

    matched_diseases = []
    risk_score = 0

    for disease, symptoms in DISEASE_RULES.items():

        matches = len(set(detected_symptoms) & set(symptoms))

        if matches >= 1:
            matched_diseases.append(disease)
            risk_score += matches

    if matched_diseases:
        reply = "Possible conditions:\n• " + "\n• ".join(matched_diseases)
    else:
        reply = "I couldn't clearly identify symptoms. Please describe them in more detail."

    return {
        "reply": reply,
        "risk": risk_score
    }