from fastapi import UploadFile, HTTPException, status, File
from app.core.logging import logger
from app.schemas.nutrition import FoodNutritionResponse
from typing import List
from app.utils import image
from app.agents.agetns import nutrition_analysis_agent
from typing import Optional
from agno.media import Image
from app.utils.image import save_as_webp 
from app.services.bedrock_service import BedrockService
from app.constants.prompts.prompts import FOOD_NAME_EXTRACTION_INSTRUCTION



async def parse_nutrition(
    serving_size: str,
    user_id: int,
    session_id: str,
    files: Optional[List[UploadFile]] = File(default=None)) -> Optional[FoodNutritionResponse]:
    """
    Parse nutrition data from uploaded files.

    Args:
        files: List of uploaded files
        Returns:
        FoodNutritionList with parsed data or None if error
    """
    logger.info(f"Total images  {len(files)}")
    bedrock_service = BedrockService()
    try:
        # Placeholder logic for parsing nutrition data
        # This should be replaced with actual parsing logic
        nutrition_parser_agent = nutrition_analysis_agent()
        if files is None or len(files) == 0:
            logger.info("No files provided for parsing nutrition")
            logger.info(f"serving size: {serving_size}")
            response = nutrition_parser_agent.run(message=serving_size, session_id=session_id)
            return response
        images = []
        image_to_process = []
        for file in files:
            filename = file.filename
            logger.info(f"Processing file: {filename}")
            file_bytes = await file.read()
            image_to_process.append((file_bytes, filename))
            # saved_filepath = save_as_webp(file_bytes)
            # with open(saved_filepath, "rb") as img_file:
            #     image_bytes = img_file.read()
            #     image_value = Image(content=image_bytes, format="webp")
            # images.append(image_value)
            # logger.info(f"saved_filepath: {saved_filepath}")
            # base_64_image = image.convert_bytes_image_to_base64(file_bytes)
            # file_ext = filename.lower().split('.')[-1]
            # image_value = {
            #     "format": file_ext,
            #     "source": {"bytes": file_bytes}
            # }
            
        
        
        data = await bedrock_service.process_multiple_images(files=image_to_process,
                                                           prompt=FOOD_NAME_EXTRACTION_INSTRUCTION)
        
        logger.info(f"Data received from bedrock service: {type(data)} - {data}")
        
        # Handle different data structures returned by bedrock service
        food_items = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    # Handle dict structure
                    if "report" in item:
                        food_items.append(item["report"])
                    elif "filename" in item and "report" in item:
                        food_items.append(item["report"])
                    else:
                        # If it's a dict but not the expected structure, use the whole item
                        food_items.append(str(item))
                elif isinstance(item, tuple) and len(item) >= 2:
                    # Handle tuple structure (filename, report)
                    food_items.append(str(item[1]))
                else:
                    # Fallback for any other structure
                    food_items.append(str(item))
        else:
            # If data is not a list, treat it as a single item
            logger.warning(f"Unexpected data structure from bedrock: {type(data)}")
            food_items.append(str(data))
        message = f"""
                    Food items: {food_items}  
                    Serving size: {serving_size}
                    """
        logger.info(f"Message to Nutrition Parser agent: {message}")
        response =  nutrition_parser_agent.run(message=message,
                                              images=images,
                                              user_id=str(user_id),session_id=str(user_id))
        logger.info(f"Response from Nutrition Parser agent received {type(response)}")
        
        # The agent is returning a list of food items, but our schema expects a single FoodNutrition object
        # Let's convert the response to match our schema
        # try:
        #     import json
        #     from pydantic import ValidationError
        #     from app.schemas.nutrition import FoodNutritionResponse
            
        #     # Try to parse the response content as JSON
        #     if isinstance(response.content, str):
        #         parsed_data = json.loads(response.content)
        #     else:
        #         parsed_data = response.content
                
        #     # Use our new helper method to create a properly formatted response
        #     if isinstance(parsed_data, list) or isinstance(parsed_data, dict):
        #         formatted_response = FoodNutritionResponse.from_list(
        #             parsed_data,
        #             message="Successfully parsed nutrition information"
        #         )
        #         return formatted_response.model_dump()
        #     else:
        #         # If it's already in the correct format, return as is
        #         return response.content
                
        # except (json.JSONDecodeError, ValidationError) as e:
        #     logger.warning(f"Error formatting nutrition response: {str(e)}")
        #     # Return original content if we can't format it
        return response.content
                        
       
    except Exception as e:
        logger.error(f"Error parsing nutrition data: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
            
        