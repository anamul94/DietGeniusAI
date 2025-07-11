import boto3
from botocore.exceptions import ClientError
from typing import List, Tuple
from app.constants.bedrock import (
    ANTHROPIC_HAIKU_3,
    ANTHROPIC_SONNET_3_5,
    ANTHROPIC_SONNET_3,
    ANTHROPIC_SONNET_4,
    NOVA_LITE,NOVA_PRO
)
import json
import re
from app.core.logging import logger

class BedrockService:
    def __init__(self,region_name="ap-south-1"):
        self.client = boto3.client("bedrock-runtime", region_name=region_name)

    async def process_multiple_medical_documents(
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
                json_str = re.sub(r"^```json\n|```$", "", response_text.strip())
                results.append((filename, json.loads(json_str)))
                logger.info(f"Successfully processed document: {filename}")

            except (ClientError, Exception) as e:
                logger.error(f"Error processing document {filename}: {str(e)}")
                results.append((filename, f"ERROR: {str(e)}"))

        return results
