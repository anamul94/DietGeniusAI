from fastapi import UploadFile, HTTPException, status, File
from app.core.logging import logger
from app.schemas.nutrition import FoodNutritionResponse
from typing import List
from app.utils import image
from app.agents.agetns import nutrition_analysis_agent
from typing import Optional
from agno.media import Image
from app.utils.image import save_as_webp 




async def parse_nutrition(
    serving_size: str,
    user_id: int,
    session_id: str,
    files: Optional[List[UploadFile]] = File(default=None)):
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
            logger.info("No files provided for parsing nutrition")
            logger.info(f"serving size: {serving_size}")
            response = nutrition_parser_agent.run(message=serving_size, session_id=session_id)
            return response
        images = []
        for file in files:
            filename = file.filename
            logger.info(f"Processing file: {filename}")
            file_bytes = await file.read()
            saved_filepath = save_as_webp(file_bytes)
            with open(saved_filepath, "rb") as img_file:
                image_bytes = img_file.read()
                image_value = Image(content=image_bytes, format="webp")
            images.append(image_value)
            logger.info(f"saved_filepath: {saved_filepath}")
            # base_64_image = image.convert_bytes_image_to_base64(file_bytes)
            file_ext = filename.lower().split('.')[-1]
            # image_value = {
            #     "format": file_ext,
            #     "source": {"bytes": file_bytes}
            # }
            
        
        message = f"""serving size {serving_size}
                       
                            """
        response = nutrition_parser_agent.run(message=message,
                                              images=images,
                                              user_id=user_id,session_id=session_id)
        logger.info(f"Response from Nutrition Parser agent received {type(response.content)}")
        # json_response = FoodNutritionResponse.model_dump_json(indent=4)
        
        # return FoodNutritionResponse.model_validate_json(response.content)
        return response.content
                        
       
    except Exception as e:
        logger.error(f"Error parsing nutrition data: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
            
        