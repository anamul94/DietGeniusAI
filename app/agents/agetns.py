import os
from textwrap import dedent


from agno.agent import Agent
from app.agents.models.model_provider import ModelProvider
from app.constants import bedrock
from app.agents.memory.memory import get_memory_with_manager
from app.constants.prompts import prompts, daily_summary
from app.schemas.agnent_qa import AgentQA
from app.schemas.nutrition import FoodNutritionResponse
from app.agents.memory import storage
# from agno.models.ollama import Ollama

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry import trace


# instrument_agno()
# LANGFUSE_AUTH is now set directly in .env file as base64 encoded value

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
        model=bedrock_model.aws_model(id=bedrock.ANTHROPIC_SONNET_3),
        parser_model=bedrock_model.aws_model(id=bedrock.NOVA_PRO),
        goal="Extract nutrition facts from foods",
        instructions=prompts.FOOD_NUTRITION_EXTRACTION_INSTRUCTION, 
        storage=storage.GENERAL_SESSION_STORAGE,
        add_history_to_messages=False,
        response_model=FoodNutritionResponse,
    )
    
def assesment_agent():
    memory = get_memory_with_manager(
        memory_model=bedrock_model.aws_model(id=bedrock.NOVA_PRO),
        memory_manager_model=bedrock_model.aws_model(id=bedrock.NOVA_PRO),
        additional_instructions=daily_summary.memory_update_instruction_for_daily_summary
    )
    return Agent(
        name="Nutritionist",
        model=bedrock_model.aws_model(id=bedrock.ANTHROPIC_SONNET_3),
        reasoning=False,
        goal="Assess the user's health and provide recommendations",
        instructions=daily_summary.daily_assessment_instruction,
        storage=storage.USER_DAILY_LOG_SESSION_STORAGE,
        memory=memory,
        system_message=dedent("""\
            You are a licensed nutritionist and dietitian.
            Always review user's prior memory and log to provide insightful analysis.  
            Maintain a professional, human tone — avoid sounding robotic or overly artificial.  
            If no prior data exists, generate a well-tailored initial analysis using available user profile information and offer a sample daily meal plan, hydration tips, and basic activity guidance.
    """), 
        enable_agentic_memory=True,
        add_datetime_to_instructions=True,
        markdown=True,
    )