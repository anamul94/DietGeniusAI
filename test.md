# Medical Report Categories
MEDICAL_REPORT_TYPES = {
    "BLOOD_TEST": {
        "subcategories": [
            "complete_blood_count",
            "lipid_profile", 
            "liver_function",
            "kidney_function",
            "thyroid_function",
            "diabetes_markers",
            "vitamin_deficiency",
            "mineral_levels",
            "inflammatory_markers"
        ]
    },
    "PRESCRIPTION": {
        "subcategories": [
            "current_medications",
            "supplements",
            "dosages",
            "frequency",
            "medical_conditions"
        ]
    },
    "ECG": {
        "subcategories": [
            "heart_rate",
            "rhythm_analysis", 
            "abnormalities",
            "cardiovascular_risk"
        ]
    },
    "RADIOLOGY": {
        "subcategories": [
            "x_ray",
            "ct_scan",
            "mri",
            "ultrasound",
            "bone_density"
        ]
    },
    "GENERAL_CHECKUP": {
        "subcategories": [
            "vital_signs",
            "physical_examination",
            "bmi_measurements",
            "doctor_recommendations"
        ]
    }
}


# Blood Test Data Points
BLOOD_TEST_MARKERS = {
    # Complete Blood Count
    "cbc_markers": {
        "hemoglobin": {"unit": "g/dL", "normal_range": {"male": [13.8, 17.2], "female": [12.1, 15.1]}},
        "hematocrit": {"unit": "%", "normal_range": {"male": [40.7, 50.3], "female": [36.1, 44.3]}},
        "rbc_count": {"unit": "million/μL", "normal_range": {"male": [4.7, 6.1], "female": [4.2, 5.4]}},
        "wbc_count": {"unit": "thousand/μL", "normal_range": [4.5, 11.0]},
        "platelet_count": {"unit": "thousand/μL", "normal_range": [150, 450]}
    },

    # Lipid Profile
    "lipid_markers": {
        "total_cholesterol": {"unit": "mg/dL", "normal_range": [0, 200]},
        "ldl_cholesterol": {"unit": "mg/dL", "normal_range": [0, 100]},
        "hdl_cholesterol": {"unit": "mg/dL", "normal_range": {"male": [40, 999], "female": [50, 999]}},
        "triglycerides": {"unit": "mg/dL", "normal_range": [0, 150]}
    },

    # Liver Function
    "liver_markers": {
        "alt": {"unit": "U/L", "normal_range": [7, 56]},
        "ast": {"unit": "U/L", "normal_range": [10, 40]},
        "bilirubin_total": {"unit": "mg/dL", "normal_range": [0.1, 1.2]},
        "albumin": {"unit": "g/dL", "normal_range": [3.5, 5.0]}
    },

    # Kidney Function
    "kidney_markers": {
        "creatinine": {"unit": "mg/dL", "normal_range": {"male": [0.7, 1.3], "female": [0.6, 1.1]}},
        "bun": {"unit": "mg/dL", "normal_range": [6, 24]},
        "egfr": {"unit": "mL/min/1.73m²", "normal_range": [90, 999]}
    },

    # Diabetes Markers
    "diabetes_markers": {
        "glucose_fasting": {"unit": "mg/dL", "normal_range": [70, 99]},
        "glucose_random": {"unit": "mg/dL", "normal_range": [70, 140]},
        "hba1c": {"unit": "%", "normal_range": [4.0, 5.6]},
        "insulin": {"unit": "μU/mL", "normal_range": [2.6, 24.9]}
    },

    # Thyroid Function
    "thyroid_markers": {
        "tsh": {"unit": "mIU/L", "normal_range": [0.4, 4.0]},
        "t3": {"unit": "pg/mL", "normal_range": [2.3, 4.2]},
        "t4": {"unit": "ng/dL", "normal_range": [5.0, 12.0]}
    },

    # Vitamins & Minerals
    "vitamin_markers": {
        "vitamin_d": {"unit": "ng/mL", "normal_range": [30, 100]},
        "vitamin_b12": {"unit": "pg/mL", "normal_range": [300, 900]},
        "folate": {"unit": "ng/mL", "normal_range": [2.7, 17.0]},
        "iron": {"unit": "μg/dL", "normal_range": {"male": [65, 175], "female": [50, 170]}},
        "ferritin": {"unit": "ng/mL", "normal_range": {"male": [12, 300], "female": [12, 150]}}
    }
}


####
import boto3
import json
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

class MedicalReportParser:
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime')
        self.textract = boto3.client('textract')
        self.comprehend_medical = boto3.client('comprehendmedical')

    async def parse_medical_document(self, document_bytes: bytes, document_type: str) -> Dict:
        """Main parsing function that orchestrates the entire process"""

        # Step 1: Extract text from document
        extracted_text = await self.extract_text_from_document(document_bytes)

        # Step 2: Use AWS Bedrock for intelligent parsing
        structured_data = await self.parse_with_bedrock(extracted_text, document_type)

        # Step 3: Use Comprehend Medical for additional medical entity extraction
        medical_entities = await self.extract_medical_entities(extracted_text)

        # Step 4: Combine and validate data
        final_report = await self.combine_and_validate(structured_data, medical_entities)

        return final_report

    async def extract_text_from_document(self, document_bytes: bytes) -> str:
        """Extract text using AWS Textract"""
        response = self.textract.analyze_document(
            Document={'Bytes': document_bytes},
            FeatureTypes=['TABLES', 'FORMS']
        )

        # Extract text, tables, and form data
        text_content = self.process_textract_response(response)
        return text_content

    async def parse_with_bedrock(self, text: str, report_type: str) -> Dict:
        """Use AWS Bedrock Claude for intelligent parsing"""

        prompt = self.create_bedrock_prompt(text, report_type)

        response = self.bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )

        result = json.loads(response['body'].read())
        return json.loads(result['content'][0]['text'])

    def create_bedrock_prompt(self, text: str, report_type: str) -> str:
        """Create specialized prompts based on report type"""

        base_prompt = f"""
        You are a medical AI assistant specialized in parsing medical reports. 
        Analyze the following {report_type} report and extract structured data.

        Medical Report Text:
        {text}

        Extract the following information in JSON format:
        """

        if report_type == "BLOOD_TEST":
            return base_prompt + """
            {
                "report_metadata": {
                    "report_date": "YYYY-MM-DD",
                    "lab_name": "string",
                    "doctor_name": "string",
                    "patient_info": {
                        "name": "string",
                        "age": "number",
                        "gender": "string"
                    }
                },
                "blood_markers": {
                    "cbc": {
                        "hemoglobin": {"value": number, "unit": "string", "status": "normal/high/low"},
                        "hematocrit": {"value": number, "unit": "string", "status": "normal/high/low"},
                        "rbc_count": {"value": number, "unit": "string", "status": "normal/high/low"},
                        "wbc_count": {"value": number, "unit": "string", "status": "normal/high/low"},
                        "platelet_count": {"value": number, "unit": "string", "status": "normal/high/low"}
                    },
                    "lipid_profile": {
                        "total_cholesterol": {"value": number, "unit": "string", "status": "normal/high/low"},
                        "ldl_cholesterol": {"value": number, "unit": "string", "status": "normal/high/low"},
                        "hdl_cholesterol": {"value": number, "unit": "string", "status": "normal/high/low"},
                        "triglycerides": {"value": number, "unit": "string", "status": "normal/high/low"}
                    },
                    "liver_function": {
                        "alt": {"value": number, "unit": "string", "status": "normal/high/low"},
                        "ast": {"value": number, "unit": "string", "status": "normal/high/low"},
                        "bilirubin": {"value": number, "unit": "string", "status": "normal/high/low"}
                    },
                    "kidney_function": {
                        "creatinine": {"value": number, "unit": "string", "status": "normal/high/low"},
                        "bun": {"value": number, "unit": "string", "status": "normal/high/low"},
                        "egfr": {"value": number, "unit": "string", "status": "normal/high/low"}
                    },
                    "diabetes_markers": {
                        "glucose_fasting": {"value": number, "unit": "string", "status": "normal/high/low"},
                        "hba1c": {"value": number, "unit": "string", "status": "normal/high/low"}
                    },
                    "vitamins_minerals": {
                        "vitamin_d": {"value": number, "unit": "string", "status": "normal/high/low"},
                        "vitamin_b12": {"value": number, "unit": "string", "status": "normal/high/low"},
                        "iron": {"value": number, "unit": "string", "status": "normal/high/low"},
                        "ferritin": {"value": number, "unit": "string", "status": "normal/high/low"}
                    }
                },
                "abnormal_findings": ["list of abnormal findings"],
                "doctor_notes": "string",
                "recommendations": ["list of recommendations"]
            }

            Important: 
            1. Extract only values that are explicitly mentioned in the report
            2. Use null for missing values
            3. Determine status (normal/high/low) based on reference ranges if provided
            4. Include units exactly as mentioned in the report
            """

        elif report_type == "PRESCRIPTION":
            return base_prompt + """
            {
                "report_metadata": {
                    "prescription_date": "YYYY-MM-DD",
                    "doctor_name": "string",
                    "hospital_clinic": "string",
                    "patient_info": {
                        "name": "string",
                        "age": "number"
                    }
                },
                "medications": [
                    {
                        "medication_name": "string",
                        "generic_name": "string",
                        "dosage": "string",
                        "frequency": "string",
                        "duration": "string",
                        "instructions": "string",
                        "category": "string"
                    }
                ],
                "supplements": [
                    {
                        "supplement_name": "string",
                        "dosage": "string",
                        "frequency": "string",
                        "instructions": "string"
                    }
                ],
                "medical_conditions": ["list of diagnosed conditions"],
                "allergies": ["list of allergies if mentioned"],
                "doctor_instructions": "string",
                "follow_up_date": "YYYY-MM-DD or null"
            }
            """

    async def extract_medical_entities(self, text: str) -> Dict:
        """Use AWS Comprehend Medical for additional entity extraction"""

        response = self.comprehend_medical.detect_entities_v2(Text=text)

        entities = {
            "medications": [],
            "medical_conditions": [],
            "anatomy": [],
            "test_procedures": [],
            "treatment_procedures": []
        }

        for entity in response['Entities']:
            category_map = {
                'MEDICATION': 'medications',
                'MEDICAL_CONDITION': 'medical_conditions', 
                'ANATOMY': 'anatomy',
                'TEST_TREATMENT_PROCEDURE': 'test_procedures'
            }

            category = category_map.get(entity['Category'])
            if category:
                entities[category].append({
                    'text': entity['Text'],
                    'confidence': entity['Score'],
                    'type': entity['Type']
                })

        return entities









-- Medical Reports Storage Schema
CREATE TABLE user_medical_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Basic Medical Info
    blood_type VARCHAR(5),
    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    bmi DECIMAL(4,2),

    -- Medical History
    chronic_conditions JSONB,
    allergies JSONB,
    family_history JSONB,

    -- Current Health Status
    overall_health_score INTEGER CHECK (overall_health_score >= 0 AND overall_health_score <= 100),
    risk_factors JSONB,

    -- Metadata
    last_checkup_date DATE,
    next_checkup_due DATE
);

-- Blood Test Results
CREATE TABLE blood_test_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(i