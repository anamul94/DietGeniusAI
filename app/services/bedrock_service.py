import boto3
from botocore.exceptions import ClientError
from typing import List, Tuple
from app.constants.models import (
    ANTHROPIC_HAIKU_3,
    ANTHROPIC_SONNET_3_5,
    ANTHROPIC_SONNET_3,
    ANTHROPIC_SONNET_4,
    NOVA_LITE,NOVA_PRO,
    META_LLMA_3_70B,
)

from app.core.logging import logger
from app.utils.json_parser import extract_json_from_response
import json
import base64



class BedrockService:
    def __init__(self,region_name="ap-south-1"):
        self.client = boto3.client("bedrock-runtime", region_name=region_name)

    async def process_multiple_documents(
        self,
        files: List[Tuple[bytes, str, str]],  # (file_bytes, filename, format)
        prompt: str
    ) -> List[Tuple[str, str]]:
        """
        Sends multiple documents to Claude 3 Haiku and returns responses.

        Args:
            files (List[Tuple[bytes, str, str]]): List of (file_bytes, filename, format),
                                                where format = 'pdf', 'docx', 'txt', etc.
            prompt (str): Prompt/question to ask for each document.

        Returns:
            List[Tuple[str, str]]: List of (filename, Claude response).
        """
        results = []
        

        for file_bytes, filename, file_format in files:
            logger.info(f"Processing document: {filename} with format: {file_format}")
            name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
            
            conversation = [
                {
                    "role": "user",
                    "content": [
                        {"text": prompt},
                        {"text": "Response must be in JSON format "},
                        {
                            "document": {
                                "format": file_format,
                                "name": name_without_ext,
                                "source": {"bytes": file_bytes},
                            }
                        },
                    ],
                }
            ]

            try:
                response = self.client.converse(
                    modelId=ANTHROPIC_SONNET_3,
                    messages=conversation,
                    inferenceConfig={ "temperature": 0.1},
                )
                response_text = response["output"]["message"]["content"][0]["text"]
                logger.info(f"Response from Bedrock: {response_text}")
                # extracted_json = extract_json_from_response(response_text) 
                results.append(dict(filename=filename, report=response_text))
                
                logger.info(f"Successfully processed document: {filename}")

            except (ClientError, Exception) as e:
                logger.error(f"Error processing document {filename}: {str(e)}")
                results.append((filename, f"ERROR: {str(e)}"))
                
          

        return results
    
    async def process_multiple_images(
        self,
        files: List[Tuple[bytes, str]],  # (file_bytes, filename)
        prompt: str
    ) -> List[Tuple[str, str]]:
        """
        Sends multiple images to Claude 3 Sonnet and returns responses.

        Args:
            files (List[Tuple[bytes, str]]): List of (file_bytes, filename)
            prompt (str): Prompt/question to ask for each image.

        Returns:
            List[Tuple[str, str]]: List of (filename, Claude response).
        """
        results = []

        for file_bytes, filename in files:
            logger.info(f"Processing image: {filename}")
            
           
            base64_image = base64.b64encode(file_bytes).decode('utf-8')
            
            # Determine image format from filename
            file_ext = filename.lower().split('.')[-1]
            # Map jpg to jpeg for AWS Bedrock compatibility
            if file_ext == 'jpg':
                file_ext = 'jpeg'
            media_type = f"image/{file_ext}" if file_ext in ['jpeg', 'png', 'webp', 'gif'] else "image/jpeg"

            conversation = [
                {
                    "role": "user",
                    "content": [
                        {"text": prompt},
                        {
                            "image": {
                                "format": file_ext,
                                "source": {"bytes": file_bytes}
                            }
                        },
                    ],
                }
            ]

            try:
                response = self.client.converse(
                    modelId=ANTHROPIC_SONNET_3_5,
                    messages=conversation,
                    inferenceConfig={"temperature": 0.1},
                )
                response_text = response["output"]["message"]["content"][0]["text"]
                logger.info(f"Response from Bedrock: {response}")
                # extracted_json = extract_json_from_response(response_text)
                results.append(dict(filename=filename, report=response_text))
                logger.info(f"Successfully processed image: {filename}")

            except (ClientError, Exception) as e:
                logger.error(f"Error processing image {filename}: {str(e)}")
                results.append((filename,""))

        return results
    
    
    
    async def process_food_images(
    self,
    files: List[Tuple[bytes, str]],  # (file_bytes, filename)
    prompt: str
) -> List[Tuple[str, str]]:
        """
        Sends multiple images to Claude 3 Sonnet in a single request and returns responses.
        """
        if not files:
            logger.warning("No images provided to process.")
            return []

        logger.info(f"Processing {len(files)} images in a single request")
        # print(prompt)
        # Prepare Bedrock content structure
        # Ensure prompt is not None
        content = [{"text": prompt or "Analyze these food images and provide nutritional information"}]

        for file_bytes, filename in files:
            logger.info(f"Adding image to batch: {filename}")

            # Detect format
            file_ext = filename.lower().split('.')[-1]
            # Map jpg to jpeg and ensure valid formats
            if file_ext == 'jpg':
                file_ext = 'jpeg'
            if file_ext not in ['jpeg', 'png', 'webp', 'gif']:
                file_ext = 'jpeg'

            # Bedrock Claude expects this structure - directly use bytes
            content.append({
                "image": {
                    "format": file_ext,
                    "source": {
                        "bytes": file_bytes
                    }
                }
            })

        conversation = [
            {
                "role": "user",
                "content": content
            }
        ]

        try:
            response = self.client.converse(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                messages=conversation,
                inferenceConfig={"temperature": 0.1},
            )

            response_text = response["output"]["message"]["content"][0]["text"]
            # logger.info(f"Response from Bedrock: {response_text}")
            logger.info(f"Successfully processed {len(files)} images")

            results = [(filename, response_text) for _, filename in files]
            return response_text

        except (ClientError, Exception) as e:
            logger.error(f"Error processing images: {str(e)}")
            results = [(filename, f"ERROR: {str(e)}") for _, filename in files]
            return results
