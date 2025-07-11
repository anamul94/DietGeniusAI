

MEDICAL_REPORT_PARSER_PROMPT = """
Extract relevant medical information from the provided documents and structure it in standardized EHR (Electronic Health Record) format.

Include key details such as:
- Patient demographics (name, age, gender, etc.)
- Chief complaints and medical history
- Diagnoses and conditions
- Medications (including dosage and frequency)
- Lab results and vital signs
- Treatment plans and clinical notes
- Doctor's observations and recommendations

Output should be clear, structured, and suitable for integration into an EHR system.
"""
