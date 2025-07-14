from fastapi import UploadFile, HTTPException, status
from app.core.logging import logger
from app.schemas.nutrition import FoodNutritionList
from typing import List
from app.utils import image
from app.agents.agetns import nutrition_analysis_agent
from agno.media import Image



async def parse_nutrition(
    serving_size: str,
    session_id: str,
    files: List[UploadFile]) -> FoodNutritionList:
    """
    Parse nutrition data from uploaded files.

    Args:
        files: List of uploaded files
        Returns:
        FoodNutritionList with parsed data or None if error
    """
    
    try:
        # Placeholder logic for parsing nutrition data
        # This should be replaced with actual parsing logic
        nutrition_parser_agent = nutrition_analysis_agent()
        if files is None or len(files) == 0:
            response = nutrition_parser_agent.run(session_id=session_id)
            return response.content
        images = []
        for file in files:
            filename = file.filename
            logger.info(f"Processing file: {filename}")
            file_bytes = await file.read()
            base_64_image = image.convert_bytes_image_to_base64(file_bytes)
            file_ext = filename.lower().split('.')[-1]
            image_value = {
                "format": file_ext,
                "source": {"bytes": file_bytes}
            }
            images.append(image_value)
        
        message = f"""serving size {serving_size}
                        images: {images}
                            """
        response = nutrition_parser_agent.run(message=message, session_id=session_id)
        logger.info(f"Response Nutrition Parser agent: {response}")
        nutrition_data = response.content
        return nutrition_data
    
    except Exception as e:
        logger.error(f"Error parsing nutrition data: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
            
        