# Hospital Management System (Python + Oracle)

## Project Overview

This project is a complete Hospital Management Database System built using **Python** and **Oracle Database**.
It simulates real-world hospital operations including patient management, appointments, admissions, billing, medicines, and lab tests.

---

## Features

*  Data cleaning and import from CSV (Patients, Doctors, Appointments)
*  Automated **Admissions generation**
*  Realistic **Medicine prescriptions with cost**
*  Intelligent **Lab test assignment based on diagnosis**
*  Dynamic **Billing system (Room + Treatment)**
*  Fully relational database with foreign key constraints

---

## Database Tables

* **Patients**
* **Doctors**
* **Appointments**
* **Admissions**
* **Billing**
* **Medicines / Prescriptions**
* **Lab Tests**

---

## Technologies Used

* Python
* Oracle Database (oracledb)
* Faker (for realistic data generation)
* SQL

---

## Key Logic Implemented

* Medical notes generated based on **reason for visit**
* Lab tests assigned only when medically relevant
* Billing calculated based on:

  * Admission type
  * Duration of stay
* Separate tracking of:

  * Room charges
  * Treatment cost
  * Medicine cost
  * Lab cost

---

## Security Practice

* Database credentials stored securely using `.env` file
* `.env` excluded using `.gitignore`

---

## 📊 Sample Query (Total Billing)

```sql
SELECT 
    B.ADMISSION_ID,
    B.ROOM_CHARGES,
    B.TREATMENT_CHARGES,
    NVL(SUM(P.COST),0) AS MEDICINE_COST,
    NVL(SUM(L.COST),0) AS LAB_COST,
    (B.ROOM_CHARGES + B.TREATMENT_CHARGES 
     + NVL(SUM(P.COST),0) + NVL(SUM(L.COST),0)) AS FINAL_TOTAL
FROM BILLING B
LEFT JOIN PRESCRIPTIONS P 
    ON B.ADMISSION_ID = P.ADMISSION_ID
LEFT JOIN LAB_TESTS L 
    ON B.ADMISSION_ID = L.ADMISSION_ID
GROUP BY 
    B.ADMISSION_ID,
    B.ROOM_CHARGES,
    B.TREATMENT_CHARGES;
```

---

## Future Improvements

* Web UI using Flask / Django
* Dashboard visualization
* API integration

---

## Author

Developed as a beginner-to-intermediate level project to demonstrate **Database Design + Python Automation skills**
