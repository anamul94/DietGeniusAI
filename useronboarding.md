# services/medical_parser.py
import boto3
import json
import asyncio
from typing import Dict, List, Any, Optional
from fastapi import UploadFile
import fitz  # PyMuPDF
from PIL import Image
import io
import base64

class MedicalReportParserService:
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.textract = boto3.client('textract', region_name='us-east-1')
        self.comprehend_medical = boto3.client('comprehendmedical', region_name='us-east-1')

    async def process_medical_report(
        self, 
        file: UploadFile, 
        report_type: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Main processing pipeline for medical reports"""

        try:
            # Read file content
            file_content = await file.read()

            # Extract text based on file type
            if file.content_type == 'application/pdf':
                extracted_text = await self._extract_text_from_pdf(file_content)
            elif file.content_type.startswith('image/'):
                extracted_text = await self._extract_text_from_image(file_content)
            else:
                raise ValueError(f"Unsupported file type: {file.content_type}")

            # Parse with AWS Bedrock
            structured_data = await self._parse_with_bedrock(extracted_text, report_type)

            # Extract medical entities
            medical_entities = await self._extract_medical_entities(extracted_text)

            # Generate AI summary
            ai_summary = await self._generate_summary(structured_data, medical_entities)

            # Generate nutritional recommendations
            nutrition_recommendations = await self._generate_nutrition_recommendations(
                structured_data, report_type
            )

            return {
                "raw_text": extracted_text,
                "structured_data": structured_data,
                "medical_entities": medical_entities,
                "ai_summary": ai_summary,
                "nutrition_recommendations": nutrition_recommendations,
                "processing_status": "completed",
                "confidence_score": self._calculate_confidence_score(structured_data)
            }

        except Exception as e:
            return {
                "processing_status": "failed",
                "error": str(e),
                "confidence_score": 0.0
            }

    async def _extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF using PyMuPDF"""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""

        for page in doc:
            text += page.get_text()

        doc.close()
        return text

    async def _extract_text_from_image(self, image_bytes: bytes) -> str:
        """Extract text from image using AWS Textract"""
        response = self.textract.detect_document_text(
            Document={'Bytes': image_bytes}
        )

        text = ""
        for item in response['Blocks']:
            if item['BlockType'] == 'LINE':
                text += item['Text'] + "\n"

        return text

    async def _parse_with_bedrock(self, text: str, report_type: str) -> Dict:
        """Parse medical report using AWS Bedrock Claude"""

        prompt = self._create_parsing_prompt(text, report_type)

        try:
            response = self.bedrock.invoke_model(
                modelId='anthropic.claude-3-sonnet-20240229-v1:0',
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
                    "patient_name": "string or null"
                }},
                "blood_markers": {{
                    "hemoglobin": {{"value": number, "unit": "string", "status": "normal/high/low", "reference_range": "string"}},
                    "total_cholesterol": {{"value": number, "unit": "string", "status": "normal/high/low"}},
                    "ldl_cholesterol": {{"value": number, "unit": "string", "status": "normal/high/low"}},
                    "hdl_cholesterol": {{"value": number, "unit": "string", "status": "normal/high/low"}},
                    "triglycerides": {{"value": number, "unit": "string", "status": "normal/high/low"}},
                    "glucose_fasting": {{"value": number, "unit": "string", "status": "normal/high/low"}},
                    "hba1c": {{"value": number, "unit": "string", "status": "normal/high/low"}},
                    "vitamin_d": {{"value": number, "unit": "string", "status": "normal/high/low"}},
                    "vitamin_b12": {{"value": number, "unit": "string", "status": "normal/high/low"}},
                    "iron": {{"value": number, "unit": "string", "status": "normal/high/low"}},
                    "creatinine": {{"value": number, "unit": "string", "status": "normal/high/low"}},
                    "alt": {{"value": number, "unit": "string", "status": "normal/high/low"}},
                    "tsh": {{"value": number, "unit": "string", "status": "normal/high/low"}}
                }},
                "key_findings": [
                    "list of abnormal or notable findings"
                ],
                "nutritional_implications": [
                    "dietary recommendations based on results"
                ]
            }}

            Rules:
            - Use null for missing values
            - Extract only explicitly mentioned values
            - Determine status based on reference ranges if provided
            - Focus on nutritionally relevant markers
            """

        elif report_type