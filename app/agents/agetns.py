import base64
import os
from textwrap import dedent


from agno.agent import Agent
from app.agents.models.model_provider import ModelProvider
from app.constants import bedrock, prompts
from app.agents.memory.memory import get_memory_with_manager
from app.schemas.agnent_qa import AgentQA
from app.schemas.nutrition import FoodNutritionResponse
from app.agents.memory import storage
from agno.models.ollama import Ollama

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry import trace


# instrument_agno()
LANGFUSE_AUTH = base64.b64encode(
    f"{os.getenv('LANGFUSE_PUBLIC_KEY')}:{os.getenv('LANGFUSE_SECRET_KEY')}".encode()
).decode()

trace_provider = TracerProvider()
trace_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(trace_provider)
import openlit
# openlit.init(tracer=trace.get_tracer(__name__), disable_batch=True)

bedrock_model = ModelProvider()

def user_onboarding_agent():
    memory = get_memory_with_manager(
        memory_model=bedrock_model.aws_model(id=bedrock.NOVA_PRO),
        memory_manager_model=bedrock_model.aws_model(id=bedrock.NOVA_PRO),
        additional_instructions=prompts.MEMORY_CAPTURE_INSTRUCTIONS,
    )
    return Agent(
    name="Clinical Dietitian",
    description="Clinical dietitian conducting patient assessment for personalized diet planning.",
    model=bedrock_model.aws_model(id=bedrock.ANTHROPIC_HAIKU_3),
    instructions=dedent("""\
        You are a clinical dietitian conducting patient assessment for diet planning.
        
        ASSESSMENT PROCESS:
        1. Review medical reports and user profile (age, gender, profession)
        2. Ask targeted questions (max 4 rounds) to understand:
           • Current dietary habits and meal patterns
           • Food allergies, intolerances, or restrictions
           • Physical activity level and daily routine
           • Specific health goals or concerns
           • Symptoms related to current diet
        
        ROUND MANAGEMENT:
        - Rounds 1-3: Ask focused assessment questions
        - Round 4: Provide final assessment summary and thank patient for cooperation
        - If completion_note is present, this indicates the final question
        
        COMMUNICATION GUIDELINES:
        - Be direct and professional during assessment rounds
        - Ask one focused question at a time
        - Use clinical language appropriate for medical assessment
        - Focus only on medically relevant dietary information
        
        FINAL ASSESSMENT (Round 4):
        Provide comprehensive clinical summary:
        • Medical findings and dietary implications
        • Identified nutritional risk factors
        • Recommendations for diet planning
        • Key considerations for treatment
        • Thank patient for their cooperation in the assessment
        
        Maintain professional clinical tone throughout.
        
        *** When you are done with the assessment, set is_done to True. ***
    """),
    system_message=dedent("""\
        You are a clinical dietitian conducting patient assessments.
        
        OBJECTIVES:
        - Gather comprehensive dietary and lifestyle information
        - Identify nutritional risks and requirements
        - Assess patient readiness for dietary changes
        - Document findings for treatment planning
        
        APPROACH:
        - Professional, clinical communication
        - Evidence-based questioning
        - Focus on medically relevant information
        - No casual conversation or gratitude expressions
        
        Your assessment informs the patient's nutritional care plan.
    """),
    memory=memory,
    enable_user_memories=True,
    add_datetime_to_instructions=True,
    markdown=True,
    # structured_outputs=True,
    response_model=AgentQA,
    enable_agentic_memory=True,
    goal="Patient Assessment",
    
)
    
def get_memory_test_agent():
      memory = get_memory_with_manager(
      memory_model=bedrock_model.aws_model(id=bedrock.NOVA_PRO),
      memory_manager_model=bedrock_model.aws_model(id=bedrock.NOVA_PRO),
      additional_instructions=prompts.MEMORY_CAPTURE_INSTRUCTIONS
  )
      return Agent(
      model=bedrock_model.aws_model(id=bedrock.NOVA_PRO),
      memory=memory,
      enable_user_memories=True ,
      markdown=True,
      add_datetime_to_instructions=True,
      instructions=dedent("""\
         Generate a structured and medically accurate summary based
         on the user's memory and experiences. The summary should be concise, clinically relevant, and easy to understand by healthcare professionals. Focus on extracting key health information such as symptoms, duration, severity, triggers, lifestyle factors,
         and any previous medical history mentioned by the user."""),
    )
      
      
def nutrition_analysis_agent():
    return Agent(
        name="Nutrition Analysis Agent",
        # model=bedrock_model.aws_model(id=bedrock.ANTHROPIC_SONNET_3),
        model= Ollama(id="gemma3:latest"),
        parser_model=bedrock_model.aws_model(id=bedrock.NOVA_PRO),
        goal="Extract nutrition facts from food image",
        instructions=dedent("""\
            You are a nutritionist analyzing food images to provide accurate nutrition information.
            
            Key responsibilities:
            - Identify all visible food items in the provided images
            - Use the user-provided serving size information to calculate total nutrition values
            - Handle multiple images efficiently by avoiding duplicate food entries
            - When the same food appears across multiple images, consolidate into a single entry
            - Calculate nutrition facts based on actual consumed quantities, not just what's visible in images
            - Consider cooking methods and preparation styles that may affect nutrition content
            
            Important: User will specify actual serving sizes consumed (e.g., "2 chicken wings", "1 bowl of rice").
            Calculate nutrition values for these specified quantities, not just what appears in the image.
            
            """),
        
        system_message=dedent("""\
            Analyze food images to identify unique food items and calculate nutrition values based on user-specified serving sizes.
            
            Process workflow:
            1. Scan all provided images for food items
            2. Create a master list of unique foods (avoid duplicates)
            3. Match identified foods with user-provided serving size information
            4. Calculate total nutrition facts for the actual consumed quantities
            
            Example: If image shows 1 chicken wing but user ate "2 chicken wings", 
            calculate nutrition for 2 wings, not just the 1 visible in the image.
            
            Always prioritize user-specified serving sizes over visual estimates from images.
            """),
        storage=storage.GENERAL_SESSION_STORAGE,
        add_datetime_to_instructions=True,
        add_history_to_messages=False,
        response_model=FoodNutritionResponse,
    )