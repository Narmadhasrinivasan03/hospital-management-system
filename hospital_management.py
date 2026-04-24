import oracledb
import random
from faker import Faker
from datetime import timedelta

oracledb.init_oracle_client(lib_dir=r"C:\oraclexe\app\oracle\product\11.2.0\server\bin")

import os
from dotenv import load_dotenv

load_dotenv("DB_KEYS.env")

conn = oracledb.connect(
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dsn=os.getenv("DB_DSN")
)

cursor = conn.cursor()

print("? Connected to Oracle")


# Fetch appointments INCLUDING reason
cursor.execute("""
    SELECT APPOINTMENT_ID, PATIENT_ID, DOCTOR_ID, APPOINTMENT_DATE, REASON_FOR_VISIT
    FROM APPOINTMENTS
""")

appointments = cursor.fetchall()
print(f"✅ Fetched {len(appointments)} appointments")

fake = Faker()

# Function to generate realistic medical notes
def generate_medical_notes(reason):
    reason = reason.lower()

    if "fever" in reason:
        return "Patient admitted with high-grade fever. Suspected viral infection. IV fluids and antipyretics administered."
    elif "cough" in reason:
        return "Patient reports persistent cough. Chest auscultation performed. Antibiotics prescribed."
    elif "headache" in reason:
        return "Severe headache noted. Neurological exam normal. Pain management initiated."
    elif "diabetes" in reason:
        return "Elevated blood glucose levels. Insulin therapy started. Diet monitored."
    elif "injury" in reason:
        return "Patient treated for physical injury. Wound cleaned and dressed."
    elif "chest pain" in reason:
        return "Patient admitted with chest pain. ECG performed. Under observation."
    else:
        return "Patient under observation. General treatment provided."

# Prepare data
# admissions_data = []

# for i, row in enumerate(appointments[:150], start=1):
#     appointment_id, patient_id, doctor_id, app_date, reason = row

#     admission_date = app_date + timedelta(days=random.randint(1, 5))
#     discharge_date = admission_date + timedelta(days=random.randint(2, 10))

#     notes = generate_medical_notes(reason)

#     admissions_data.append((
#         i,
#         appointment_id,
#         patient_id,
#         doctor_id,
#         admission_date,
#         discharge_date,
#         f"R{random.randint(100,500)}",
#         f"B{random.randint(1,5)}",
#         random.choice(['Emergency', 'Follow up','Consultation']),
#         notes,
#         random.choice(['Admitted', 'Discharged'])
#     ))

# # Create table (since you already dropped it)
# try:
#     cursor.execute("DROP TABLE ADMISSIONS")
# except oracledb.DatabaseError:
#     pass

# cursor.execute("""
# CREATE TABLE ADMISSIONS (
#     ADMISSION_ID NUMBER PRIMARY KEY,
#     APPOINTMENT_ID NUMBER,
#     PATIENT_ID NUMBER,
#     DOCTOR_ID NUMBER,
#     ADMISSION_DATE DATE,
#     DISCHARGE_DATE DATE,
#     ROOM_NUMBER VARCHAR2(10),
#     BED_NUMBER VARCHAR2(10),
#     ADMISSION_TYPE VARCHAR2(50),
#     NOTES VARCHAR2(500),
#     STATUS VARCHAR2(20),
#     CONSTRAINT fk_appointment
#         FOREIGN KEY (APPOINTMENT_ID)
#         REFERENCES APPOINTMENTS(APPOINTMENT_ID)
# )
# """)

# print("✅ ADMISSIONS table created")

# # Insert data
# cursor.executemany("""
# INSERT INTO ADMISSIONS (
#     ADMISSION_ID, APPOINTMENT_ID, PATIENT_ID, DOCTOR_ID,
#     ADMISSION_DATE, DISCHARGE_DATE,
#     ROOM_NUMBER, BED_NUMBER,
#     ADMISSION_TYPE, NOTES, STATUS
# ) VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11)
# """, admissions_data)

# conn.commit()

# print("✅ Admissions inserted successfully")

# -------------------------------
# FETCH ADMISSIONS FOR BILLING
# -------------------------------
cursor.execute("""
    SELECT ADMISSION_ID, ADMISSION_DATE, DISCHARGE_DATE, ADMISSION_TYPE
    FROM ADMISSIONS
""")

admissions = cursor.fetchall()
print(f"✅ Fetched {len(admissions)} admissions for billing")


# -------------------------------
# BILL CALCULATION FUNCTION
# -------------------------------
def calculate_bill(adm_type, days):
    if adm_type == "Emergency":
        room_rate = 3000
        treatment = random.randint(5000, 15000)
    elif adm_type == "Consultation":
        room_rate = 1500
        treatment = random.randint(2000, 8000)
    else:
        room_rate = 1000
        treatment = random.randint(1000, 5000)

    room_cost = room_rate * days
    total = room_cost + treatment

    return room_cost, treatment, total


# -------------------------------
# DROP & CREATE BILLING TABLE
# -------------------------------
try:
    cursor.execute("DROP TABLE BILLING")
    print("⚠️ Old BILLING table dropped")
except oracledb.DatabaseError:
    pass

cursor.execute("""
CREATE TABLE BILLING (
    BILL_ID NUMBER PRIMARY KEY,
    ADMISSION_ID NUMBER,
    ROOM_CHARGES NUMBER,
    TREATMENT_CHARGES NUMBER,
    TOTAL_AMOUNT NUMBER,
    PAYMENT_STATUS VARCHAR2(20),
    CONSTRAINT fk_billing_admission
        FOREIGN KEY (ADMISSION_ID)
        REFERENCES ADMISSIONS(ADMISSION_ID)
)
""")

print("✅ BILLING table created")


# -------------------------------
# PREPARE BILLING DATA
# -------------------------------
billing_data = []

for i, row in enumerate(admissions[:150], start=1):
    admission_id, adm_date, dis_date, adm_type = row

    days = (dis_date - adm_date).days
    days = max(days, 1)

    room_cost, treatment_cost, total = calculate_bill(adm_type, days)

    billing_data.append((
        i + 1000,  # avoids duplicate key issue
        admission_id,
        room_cost,
        treatment_cost,
        total,
        random.choice(['Paid', 'Pending'])
    ))


# -------------------------------
# INSERT INTO BILLING
# -------------------------------
cursor.executemany("""
INSERT INTO BILLING (
    BILL_ID, ADMISSION_ID,
    ROOM_CHARGES, TREATMENT_CHARGES,
    TOTAL_AMOUNT, PAYMENT_STATUS
) VALUES (:1,:2,:3,:4,:5,:6)
""", billing_data)

print("✅ Billing inserted successfully")


# -------------------------------
# FINAL COMMIT
# -------------------------------
conn.commit()

print("✅ ALL DONE SUCCESSFULLY")
# -------------------------------
# DROP & CREATE PRESCRIPTIONS TABLE
# -------------------------------
try:
    cursor.execute("DROP TABLE PRESCRIPTIONS")
    print("⚠️ Old PRESCRIPTIONS table dropped")
except oracledb.DatabaseError:
    pass

cursor.execute("""
CREATE TABLE PRESCRIPTIONS (
    PRESCRIPTION_ID NUMBER PRIMARY KEY,
    ADMISSION_ID NUMBER,
    MEDICINE_NAME VARCHAR2(100),
    DOSAGE VARCHAR2(20),
    DAYS NUMBER,
    COST NUMBER,
    CONSTRAINT fk_prescription_admission
        FOREIGN KEY (ADMISSION_ID)
        REFERENCES ADMISSIONS(ADMISSION_ID)
)
""")

print("✅ PRESCRIPTIONS table created")


# -------------------------------
# SAMPLE MEDICINES LIST
# -------------------------------
medicines_list = [
    ("Paracetamol", 10),
    ("Ibuprofen", 15),
    ("Amoxicillin", 25),
    ("Cough Syrup", 50),
    ("Insulin", 200),
    ("Antacid", 20),
    ("Vitamin D", 30),
    ("Pain Relief Gel", 60)
]


# -------------------------------
# FETCH ADMISSIONS
# -------------------------------
cursor.execute("SELECT ADMISSION_ID FROM ADMISSIONS")
admissions = cursor.fetchall()


# -------------------------------
# GENERATE MEDICINE DATA
# -------------------------------
prescription_data = []
prescription_id = 1

for row in admissions[:150]:
    admission_id = row[0]

    # each patient gets 1–3 medicines
    for _ in range(random.randint(1, 3)):
        med_name, price = random.choice(medicines_list)
        days = random.randint(1, 7)
        dosage = random.choice(["1-0-1", "1-1-1", "0-1-0"])

        cost = price * days

        prescription_data.append((
            prescription_id,
            admission_id,
            med_name,
            dosage,
            days,
            cost
        ))

        prescription_id += 1


# -------------------------------
# INSERT INTO PRESCRIPTIONS
# -------------------------------
cursor.executemany("""
INSERT INTO PRESCRIPTIONS (
    PRESCRIPTION_ID,
    ADMISSION_ID,
    MEDICINE_NAME,
    DOSAGE,
    DAYS,
    COST
) VALUES (:1,:2,:3,:4,:5,:6)
""", prescription_data)

print("✅ Medicines (Prescriptions) inserted")


# -------------------------------
# COMMIT
# -------------------------------
conn.commit()

print("✅ MEDICINE TABLE CREATED & DATA INSERTED SUCCESSFULLY")

# -------------------------------
# DROP & CREATE LAB_TESTS TABLE
# -------------------------------
try:
    cursor.execute("DROP TABLE LAB_TESTS")
    print("⚠️ Old LAB_TESTS table dropped")
except oracledb.DatabaseError:
    pass

cursor.execute("""
CREATE TABLE LAB_TESTS (
    TEST_ID NUMBER PRIMARY KEY,
    ADMISSION_ID NUMBER,
    TEST_NAME VARCHAR2(100),
    TEST_RESULT VARCHAR2(100),
    COST NUMBER,
    CONSTRAINT fk_lab_admission
        FOREIGN KEY (ADMISSION_ID)
        REFERENCES ADMISSIONS(ADMISSION_ID)
)
""")

print("✅ LAB_TESTS table created")


# -------------------------------
# FETCH DATA (REASON + NOTES)
# -------------------------------
cursor.execute("""
SELECT 
    A.ADMISSION_ID, 
    P.REASON_FOR_VISIT,
    A.NOTES
FROM ADMISSIONS A
JOIN APPOINTMENTS P 
ON A.APPOINTMENT_ID = P.APPOINTMENT_ID
""")

records = cursor.fetchall()


# -------------------------------
# SEVERITY DETECTION
# -------------------------------
def detect_severity(text):
    text = text.lower()

    if any(word in text for word in ["high", "severe", "chronic", "critical"]):
        return "severe"
    elif any(word in text for word in ["persistent", "moderate"]):
        return "moderate"
    else:
        return "mild"


# -------------------------------
# LAB TEST LOGIC (REALISTIC)
# -------------------------------
def get_lab_tests(text, severity):
    text = text.lower()

    if severity == "mild":
        return []  # no tests

    if "fever" in text:
        if severity == "moderate":
            return [("CBC", 300)]
        else:
            return [("CBC", 300), ("Blood Culture", 700)]

    elif "cough" in text:
        if severity == "moderate":
            return [("Chest X-ray", 800)]
        else:
            return [("Chest X-ray", 800), ("CT Scan", 2000)]

    elif "diabetes" in text:
        return [("Blood Sugar", 400), ("HbA1c", 900)]

    elif "chest pain" in text:
        return [("ECG", 1000), ("Troponin Test", 1500)]

    elif "injury" in text:
        return [("X-ray", 700)]

    else:
        return []


# -------------------------------
# GENERATE LAB DATA
# -------------------------------
lab_data = []
test_id = 1

for admission_id, reason, notes in records:

    combined_text = (reason + " " + notes)

    severity = detect_severity(combined_text)

    tests = get_lab_tests(combined_text, severity)

    for test_name, cost in tests:
        result = random.choice([
            "Normal",
            "Abnormal",
            "Needs Further Evaluation"
        ])

        lab_data.append((
            test_id,
            admission_id,
            test_name,
            result,
            cost
        ))

        test_id += 1


# -------------------------------
# INSERT INTO LAB_TESTS
# -------------------------------
cursor.executemany("""
INSERT INTO LAB_TESTS (
    TEST_ID, ADMISSION_ID,
    TEST_NAME, TEST_RESULT, COST
) VALUES (:1,:2,:3,:4,:5)
""", lab_data)

print(f"✅ Inserted {len(lab_data)} realistic lab test records")


# -------------------------------
# COMMIT
# -------------------------------
conn.commit()

print("✅ LAB TEST SYSTEM COMPLETED SUCCESSFULLY")

# -------------------------------
# DROP & CREATE LAB_TESTS TABLE
# -------------------------------
try:
    cursor.execute("DROP TABLE LAB_TESTS")
    print("⚠️ Old LAB_TESTS table dropped")
except oracledb.DatabaseError:
    pass

cursor.execute("""
CREATE TABLE LAB_TESTS (
    TEST_ID NUMBER PRIMARY KEY,
    ADMISSION_ID NUMBER,
    TEST_NAME VARCHAR2(100),
    TEST_RESULT VARCHAR2(100),
    COST NUMBER,
    CONSTRAINT fk_lab_admission
        FOREIGN KEY (ADMISSION_ID)
        REFERENCES ADMISSIONS(ADMISSION_ID)
)
""")

print("✅ LAB_TESTS table created")


# -------------------------------
# FETCH DATA (REASON + NOTES)
# -------------------------------
cursor.execute("""
SELECT 
    A.ADMISSION_ID, 
    P.REASON_FOR_VISIT,
    A.NOTES
FROM ADMISSIONS A
JOIN APPOINTMENTS P 
ON A.APPOINTMENT_ID = P.APPOINTMENT_ID
""")

records = cursor.fetchall()


# -------------------------------
# SEVERITY DETECTION
# -------------------------------
def detect_severity(text):
    text = text.lower()

    if any(word in text for word in ["high", "severe", "chronic", "critical"]):
        return "severe"
    elif any(word in text for word in ["persistent", "moderate"]):
        return "moderate"
    else:
        return "mild"


# -------------------------------
# LAB TEST LOGIC (REALISTIC)
# -------------------------------
def get_lab_tests(text, severity):
    text = text.lower()

    if severity == "mild":
        return []  # no tests

    if "fever" in text:
        if severity == "moderate":
            return [("CBC", 300)]
        else:
            return [("CBC", 300), ("Blood Culture", 700)]

    elif "cough" in text:
        if severity == "moderate":
            return [("Chest X-ray", 800)]
        else:
            return [("Chest X-ray", 800), ("CT Scan", 2000)]

    elif "diabetes" in text:
        return [("Blood Sugar", 400), ("HbA1c", 900)]

    elif "chest pain" in text:
        return [("ECG", 1000), ("Troponin Test", 1500)]

    elif "injury" in text:
        return [("X-ray", 700)]

    else:
        return []


# -------------------------------
# GENERATE LAB DATA
# -------------------------------
lab_data = []
test_id = 1

for admission_id, reason, notes in records:

    combined_text = (reason + " " + notes)

    severity = detect_severity(combined_text)

    tests = get_lab_tests(combined_text, severity)

    for test_name, cost in tests:
        result = random.choice([
            "Normal",
            "Abnormal",
            "Needs Further Evaluation"
        ])

        lab_data.append((
            test_id,
            admission_id,
            test_name,
            result,
            cost
        ))

        test_id += 1


# -------------------------------
# INSERT INTO LAB_TESTS
# -------------------------------
cursor.executemany("""
INSERT INTO LAB_TESTS (
    TEST_ID, ADMISSION_ID,
    TEST_NAME, TEST_RESULT, COST
) VALUES (:1,:2,:3,:4,:5)
""", lab_data)

print(f"✅ Inserted {len(lab_data)} realistic lab test records")


# -------------------------------
# COMMIT
# -------------------------------
conn.commit()

print("✅ LAB TEST SYSTEM COMPLETED SUCCESSFULLY")