# services/medical_parser.py
import json
import asyncio
from typing import Dict, List, Any, Optional
from fastapi import UploadFile
from typing import List
from app.services.bedrock_service import BedrockService
from app.constants.prompts import MEDICAL_REPORT_PARSER_PROMPT
from app.core.logging import logger
class MedicalReportParserService:
    def __init__(self):
        self.bedrock = BedrockService()
        

    async def process_medical_report(
        self, 
        files: List[UploadFile]
    ) -> Dict[str, Any]:
        """Main processing pipeline for medical reports"""

        try:
            docs_to_process = []
            images_to_process = []

            for file in files:
                content = await file.read()
                filename = file.filename
                file_extension = filename.split(".")[-1].lower()

                if file_extension in ["pdf", "doc", "docx", "txt"]:
                    
                    docs_to_process.append((content, filename, file_extension))
                elif file_extension in ["jpg", "jpeg", "png", "webp"]:
                    images_to_process.append((content, filename))
                else:
                    # Optional: Skip or raise error for unsupported types
                    continue  # or raise HTTPException

            
            all_results = []
            
            if docs_to_process:
                doc_results = await self.bedrock.process_multiple_documents(docs_to_process, MEDICAL_REPORT_PARSER_PROMPT)
                all_results.extend(doc_results)
            
            if images_to_process:
                image_results = await self.bedrock.process_multiple_images(images_to_process, MEDICAL_REPORT_PARSER_PROMPT)
                all_results.extend(image_results)
            
            return {
                "processing_status": "completed",
                "results": all_results,
                "total_files": len(all_results)
            }
            
        except Exception as e:
            logger.error(e)
            return {
                "processing_status": "failed",
                "error": str(e),
                "confidence_score": 0.0
            }

    def _check_file_type(files):
        pass
       

    async def _parse_image_with_bedrock_vision(self, base64_image: str, report_type: str) -> Dict:
        """Parse medical report image directly using Bedrock Vision"""

        prompt = self._create_vision_parsing_prompt(report_type)

        response = self.bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }],
                "temperature": 0.1
            })
        )

        result = json.loads(response['body'].read())
        return json.loads(result['content'][0]['text'])

    async def _parse_with_bedrock(self, text: str, report_type: str) -> Dict:
        """Parse medical report using AWS Bedrock Claude"""

        prompt = self._create_parsing_prompt(text, report_type)

        try:
            response = self.bedrock.invoke_model(
                modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 4000,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1
                })
            )

            result = json.loads(response['body'].read())
            return json.loads(result['content'][0]['text'])

        except Exception as e:
            print(f"Bedrock parsing error: {e}")
            return {}

    def _create_parsing_prompt(self, text: str, report_type: str) -> str:
        """Create specialized parsing prompts"""

        if report_type == "BLOOD_TEST":
            return f"""
            Analyze this blood test report and extract structured data. Focus on nutritionally relevant markers.

            Report Text:
            {text}

            Extract in this JSON format:
            {{
                "report_metadata": {{
                    "report_date": "YYYY-MM-DD or null",
                    "lab_name": "string or null",
                    "patient_name": "string or null",
                    "doctor_name": "string or null",
                    "patient_age": "number or null",
                    "patient_gender": "string or null"
                }},
                "blood_markers": {{
                    "complete_blood_count": {{
                        "hemoglobin": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "hematocrit": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "rbc_count": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "wbc_count": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "platelet_count": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}}
                    }},
                    "lipid_profile": {{
                        "total_cholesterol": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "ldl_cholesterol": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "hdl_cholesterol": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "triglycerides": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}}
                    }},
                    "diabetes_markers": {{
                        "glucose_fasting": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "glucose_random": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "hba1c": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "insulin": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}}
                    }},
                    "liver_function": {{
                        "alt": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "ast": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "bilirubin_total": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "albumin": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}}
                    }},
                    "kidney_function": {{
                        "creatinine": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "bun": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "egfr": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}}
                    }},
                    "thyroid_function": {{
                        "tsh": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "t3": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "t4": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}}
                    }},
                    "vitamins_minerals": {{
                        "vitamin_d": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "vitamin_b12": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "folate": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "iron": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "ferritin": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "calcium": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}},
                        "magnesium": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null", "reference_range": "string or null"}}
                    }}
                }},
                "abnormal_findings": ["list of abnormal findings"],
                "doctor_notes": "string or null",
                "recommendations": ["list of recommendations"]
            }}

            Rules:
            - Use null for missing values
            - Extract only explicitly mentioned values
            - Determine status based on reference ranges if provided
            - Focus on nutritionally relevant markers
            """

        elif report_type == "PRESCRIPTION":
            return f"""
            Analyze this prescription and extract medication information for nutritional assessment.

            Prescription Text:
            {text}

            Extract in this JSON format:
            {{
                "report_metadata": {{
                    "prescription_date": "YYYY-MM-DD or null",
                    "doctor_name": "string or null",
                    "hospital_clinic": "string or null",
                    "patient_name": "string or null",
                    "patient_age": "number or null"
                }},
                "medications": [
                    {{
                        "medication_name": "string",
                        "generic_name": "string or null",
                        "brand_name": "string or null",
                        "dosage": "string",
                        "strength": "string",
                        "frequency": "string",
                        "duration": "string",
                        "instructions": "string",
                        "category": "string or null",
                        "food_interactions": ["list of food interactions if any"],
                        "nutritional_effects": "string or null"
                    }}
                ],
                "supplements": [
                    {{
                        "supplement_name": "string",
                        "dosage": "string",
                        "frequency": "string",
                        "instructions": "string or null"
                    }}
                ],
                "diagnosed_conditions": ["list of conditions mentioned"],
                "allergies": ["list of allergies if mentioned"],
                "dietary_restrictions": ["any dietary restrictions mentioned"],
                "doctor_instructions": "string or null",
                "follow_up_date": "YYYY-MM-DD or null",
                "lab_tests_ordered": ["list of lab tests if any"]
            }}

            Rules:
            - Extract only explicitly mentioned information
            - Use null for missing values
            - Focus on medications that affect nutrition or require dietary considerations
            """

        elif report_type == "ECG":
            return f"""
            Analyze this ECG report for cardiovascular health insights relevant to nutrition.

            ECG Report Text:
            {text}

            Extract in this JSON format:
            {{
                "report_metadata": {{
                    "test_date": "YYYY-MM-DD or null",
                    "doctor_name": "string or null",
                    "hospital_clinic": "string or null",
                    "patient_name": "string or null"
                }},
                "ecg_findings": {{
                    "heart_rate": {{"value": "number or null", "unit": "bpm", "status": "normal/high/low/null"}},
                    "rhythm": "string or null",
                    "pr_interval": {{"value": "number or null", "unit": "ms", "status": "normal/prolonged/short/null"}},
                    "qrs_duration": {{"value": "number or null", "unit": "ms", "status": "normal/prolonged/null"}},
                    "qt_interval": {{"value": "number or null", "unit": "ms", "status": "normal/prolonged/short/null"}}
                }},
                "abnormalities": ["list of any abnormal findings"],
                "cardiovascular_risk_factors": ["list of identified risk factors"],
                "doctor_interpretation": "string or null",
                "recommendations": ["list of recommendations including lifestyle/dietary"]
            }}

            Rules:
            - Focus on findings relevant to cardiovascular health and nutrition
            - Extract specific measurements with units
            - Note any lifestyle recommendations
            """

        elif report_type == "RADIOLOGY":
            return f"""
            Analyze this radiology report for findings relevant to nutritional health.

            Radiology Report Text:
            {text}

            Extract in this JSON format:
            {{
                "report_metadata": {{
                    "exam_date": "YYYY-MM-DD or null",
                    "exam_type": "string", 
                    "radiologist_name": "string or null",
                    "hospital_clinic": "string or null",
                    "patient_name": "string or null"
                }},
                "findings": {{
                    "bone_density": {{"status": "normal/osteopenia/osteoporosis/null", "t_score": "number or null", "z_score": "number or null"}},
                    "liver_findings": ["list of liver-related findings"],
                    "kidney_findings": ["list of kidney-related findings"],
                    "abdominal_findings": ["list of abdominal findings"],
                    "abdominal_findings": ["list of abdominal findings"],
                    "cardiovascular_findings": ["list of heart/vessel findings"],
                    "other_significant_findings": ["other findings relevant to health"]
                }},
                "nutritional_implications": ["dietary considerations based on findings"],
                "follow_up_recommendations": ["recommended follow-up actions"],
                "doctor_impression": "string or null",
                "clinical_correlation": "string or null"
            }}

            Rules:
            - Focus on findings that may impact nutrition or dietary recommendations
            - Extract measurements and grades where available
            - Note any organ function assessments
            """

        elif report_type == "GENERAL_CHECKUP":
            return f"""
            Analyze this general medical checkup report for comprehensive health assessment.

            Medical Report Text:
            {text}

            Extract in this JSON format:
            {{
                "report_metadata": {{
                    "checkup_date": "YYYY-MM-DD or null",
                    "doctor_name": "string or null",
                    "hospital_clinic": "string or null",
                    "patient_name": "string or null",
                    "patient_age": "number or null"
                }},
                "vital_signs": {{
                    "blood_pressure": {{"systolic": "number or null", "diastolic": "number or null", "status": "normal/high/low/null"}},
                    "heart_rate": {{"value": "number or null", "unit": "bpm", "status": "normal/high/low/null"}},
                    "temperature": {{"value": "number or null", "unit": "string", "status": "normal/high/low/null"}},
                    "respiratory_rate": {{"value": "number or null", "unit": "breaths/min", "status": "normal/high/low/null"}},
                    "oxygen_saturation": {{"value": "number or null", "unit": "%", "status": "normal/low/null"}}
                }},
                "physical_measurements": {{
                    "height": {{"value": "number or null", "unit": "cm"}},
                    "weight": {{"value": "number or null", "unit": "kg"}},
                    "bmi": {{"value": "number or null", "status": "underweight/normal/overweight/obese/null"}},
                    "waist_circumference": {{"value": "number or null", "unit": "cm"}}
                }},
                "physical_examination": {{
                    "general_appearance": "string or null",
                    "cardiovascular": "string or null",
                    "respiratory": "string or null",
                    "abdominal": "string or null",
                    "neurological": "string or null"
                }},
                "current_symptoms": ["list of symptoms mentioned"],
                "medical_history": ["list of past medical conditions"],
                "current_medications": ["list of current medications"],
                "lifestyle_factors": {{
                    "smoking": "string or null",
                    "alcohol": "string or null",
                    "exercise": "string or null",
                    "diet": "string or null"
                }},
                "doctor_assessment": "string or null",
                "recommendations": ["list of doctor recommendations"],
                "follow_up_required": "string or null"
            }}

            Rules:
            - Extract all available measurements with units
            - Focus on lifestyle and nutritional aspects
            - Include all doctor recommendations
            """

        else:
            return f"""
            Analyze this medical report and extract relevant information for nutritional assessment.

            Report Text:
            {text}

            Extract key information in JSON format focusing on:
            - Patient demographics
            - Medical findings relevant to nutrition
            - Medications or treatments that affect diet
            - Doctor recommendations related to lifestyle/diet
            - Any nutritional implications

            Use appropriate structure based on the content found.
            """

    def _create_vision_parsing_prompt(self, report_type: str) -> str:
        """Create parsing prompt for image analysis"""

        if report_type == "BLOOD_TEST":
            return """
            Analyze this blood test report image and extract all visible data. Focus on nutritionally relevant markers.

            Look for:
            - Lab values with units and reference ranges
            - Patient information
            - Test dates
            - Doctor/lab information
            - Any abnormal flags or indicators

            Extract in the same JSON format as specified for text parsing, ensuring you capture:
            1. All visible numeric values with their units
            2. Reference ranges where shown
            3. Normal/High/Low status indicators
            4. Any highlighted or flagged abnormal values
            5. Doctor notes or recommendations if visible

            Be very careful to read numbers accurately and preserve exact units and ranges as shown.
            """

        elif report_type == "PRESCRIPTION":
            return """
            Analyze this prescription image and extract all medication details.

            Look for:
            - Medication names (brand and generic)
            - Dosages and strengths
            - Frequency instructions
            - Duration of treatment
            - Doctor and patient information
            - Any special instructions
            - Diagnosed conditions

            Extract in the JSON format specified for prescription parsing.
            Pay special attention to dosage instructions and any dietary recommendations.
            """

        else:
            return f"""
            Analyze this {report_type} medical report image and extract all relevant information.

            Focus on:
            - Patient and doctor information
            - Test results and measurements
            - Medical findings and interpretations
            - Recommendations and instructions
            - Any nutritionally relevant information

            Extract data in appropriate JSON format based on the content visible in the image.
            """

    async def _generate_comprehensive_analysis(self, parsed_data: Dict, report_type: str) -> Dict:
        """Generate comprehensive health and nutrition analysis"""

        analysis_prompt = f"""
        Based on this parsed {report_type} data, provide a comprehensive analysis for a nutrition app user:

        Parsed Data:
        {json.dumps(parsed_data, indent=2)}

        Generate analysis in this JSON format:
        {{
            "summary": "2-3 sentence summary of overall health status from a nutritional perspective",
            "key_findings": [
                "list of 3-5 most important findings that affect nutrition and diet"
            ],
            "nutrition_recommendations": [
                {{
                    "category": "vitamins/minerals/macronutrients/hydration/lifestyle",
                    "recommendation": "specific dietary recommendation",
                    "reason": "why this is recommended based on the data",
                    "priority": "high/medium/low",
                    "foods_to_include": ["list of specific foods"],
                    "foods_to_limit": ["list of foods to avoid/limit"]
                }}
            ],
            "health_insights": [
                {{
                    "insight": "health insight relevant to nutrition",
                    "impact_on_diet": "how this affects dietary choices",
                    "monitoring_needed": "what to track going forward"
                }}
            ],
            "risk_assessment": {{
                "nutritional_risks": ["list of identified nutritional risks"],
                "cardiovascular_risk": "low/moderate/high based on available data",
                "diabetes_risk": "low/moderate/high based on glucose/insulin markers",
                "bone_health_risk": "low/moderate/high based on available markers",
                "liver_health_risk": "low/moderate/high based on liver function tests",
                "kidney_health_risk": "low/moderate/high based on kidney function"
            }},
            "supplement_recommendations": [
                {{
                    "supplement": "supplement name",
                    "reason": "why recommended based on deficiency or risk",
                    "dosage_guidance": "general dosage recommendation",
                    "consult_doctor": true/false
                }}
            ],
            "lifestyle_modifications": [
                {{
                    "area": "exercise/sleep/stress/hydration",
                    "recommendation": "specific lifestyle change",
                    "expected_benefit": "how this helps based on the medical data"
                }}
            ],
            "follow_up_suggestions": [
                "list of suggested follow-up tests or monitoring based on findings"
            ],
            "confidence_score": "number between 0.0 and 1.0 representing confidence in the analysis"
        }}

        Important Guidelines:
        1. Base all recommendations strictly on the parsed medical data
        2. If data is insufficient for certain assessments, note limitations
        3. Always recommend consulting healthcare providers for significant findings
        4. Focus on actionable nutritional and lifestyle recommendations
        5. Prioritize recommendations based on severity of findings
        6. Consider interactions between different health markers
        """

        try:
            response = self.bedrock.invoke_model(
                modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 4000,
                    "messages": [{"role": "user", "content": analysis_prompt}],
                    "temperature": 0.2
                })
            )

            result = json.loads(response['body'].read())
            return json.loads(result['content'][0]['text'])

        except Exception as e:
            print(f"Analysis generation error: {e}")
            return {
                "summary": "Analysis could not be completed due to processing error.",
                "key_findings": [],
                "nutrition_recommendations": [],
                "health_insights": [],
                "risk_assessment": {
                    "nutritional_risks": [],
                    "cardiovascular_risk": "unknown",
                    "diabetes_risk": "unknown",
                    "bone_health_risk": "unknown",
                    "liver_health_risk": "unknown",
                    "kidney_health_risk": "unknown"
                },
                "supplement_recommendations": [],
                "lifestyle_modifications": [],
                "follow_up_suggestions": [],
                "confidence_score": 0.0
            }

    def _calculate_confidence_score(self, structured_data: Dict) -> float:
        """Calculate confidence score based on data completeness and quality"""

        if not structured_data:
            return 0.0

        total_fields = 0
        populated_fields = 0

        def count_fields(data, path=""):
            nonlocal total_fields, populated_fields

            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        count_fields(value, f"{path}.{key}" if path else key)
                    else:
                        total_fields += 1
                        if value is not None and value != "" and value != []:
                            populated_fields += 1
            elif isinstance(data, list):
                for item in data:
                    count_fields(item, path)

        count_fields(structured_data)

        if total_fields == 0:
            return 0.0

        base_score = populated_fields / total_fields

        # Boost score for critical medical markers
        critical_markers = [
            'hemoglobin', 'glucose_fasting', 'hba1c', 'total_cholesterol',
            'creatinine', 'alt', 'tsh'
        ]

        critical_found = 0
        for marker in critical_markers:
            if self._find_nested_value(structured_data, marker):
                critical_found += 1

        critical_bonus = (critical_found / len(critical_markers)) * 0.2

        return min(1.0, base_score + critical_bonus)

    def _find_nested_value(self, data: Dict, key: str) -> Any:
        """Find a value in nested dictionary structure"""

        if isinstance(data, dict):
            if key in data:
                return data[key]
            for value in data.values():
                if isinstance(value, (dict, list)):
                    result = self._find_nested_value(value, key)
                    if result is not None:
                        return result
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    result = self._find_nested_value(item, key)
                    if result is not None:
                        return result

        return None