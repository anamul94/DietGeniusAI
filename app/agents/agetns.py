import os
from textwrap import dedent


from agno.agent import Agent
from app.agents.models.model_provider import ModelProvider
from app.constants import models
from app.agents.memory.memory import get_memory_with_manager
from app.constants.prompts import prompts, daily_summary
from app.schemas.NutritionistQA import NutritionistQA
from app.schemas.nutrition import FoodNutritionResponse
from app.agents.memory import storage as agent_storage
# from agno.models.ollama import Ollama

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry import trace
import datetime
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.thinking import ThinkingTools
from agno.tools.reasoning import ReasoningTools


# instrument_agno()
# LANGFUSE_AUTH is now set directly in .env file as base64 encoded value

trace_provider = TracerProvider()
trace_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(trace_provider)
import openlit
# openlit.init(tracer=trace.get_tracer(__name__), disable_batch=True)

model = ModelProvider()

def user_onboarding_agent():
    memory = get_memory_with_manager(
        memory_model=model.aws_model(id=models.NOVA_PRO),
        memory_manager_model=model.aws_model(id=models.NOVA_PRO),
        additional_instructions=prompts.MEMORY_CAPTURE_INSTRUCTIONS,
    )
    return Agent(
    name="Clinical Dietitian",
    model=model.aws_model(id=models.ANTHROPIC_SONNET_3),
    # parser_model=model.aws_model(id=models.NOVA_PRO),
    goal=dedent("""\"Comprehensive health and nutrition assessment
                of patients to create personalized dietary plans 
                based on clinical best practices and evidence-based guidelines"""),
    instructions=dedent("""\
            ## Primary Objective
            Conduct a thorough yet comfortable health and nutrition assessment to gather essential information 
            for creating a personalized nutrition plan.

            ## Assessment Protocol
            1. **Review Available Data First**
               - Carefully examine any existing patient profile information
               - Review previous responses to avoid repetitive questions
               - Note any lab test results or medical documentation provided

            2. **Strategic Questioning Approach**
               - Ask 1-3 focused, easy-to-understand questions per interaction
               - Prioritize the most critical missing information
               - Use a warm, conversational tone that puts patients at ease
               - Avoid medical jargon - explain terms when necessary

            3. **Key Information Areas to Cover**
               - **Medical History**: Current conditions, medications, supplements, allergies
               - **Physical Profile**: Height, weight, age, activity level, sleep patterns
               - **Dietary Patterns**: Current eating habits, meal timing, food preferences
               - **Lifestyle Factors**: Work schedule, stress levels, cooking abilities
               - **Cultural/Religious Considerations**: Dietary restrictions, food traditions
               - **Goals & Challenges**: Weight management, health improvements, barriers to healthy eating

            4. **Question Format Guidelines**
               - Use radio buttons/checkboxes for multiple choice options
               - Use text input for open-ended responses
               - Use scales (1-10) for subjective assessments (energy levels, stress, etc.)
               - Frame questions positively and non-judgmentally

            5. **Completion Criteria**
               - When sufficient information is gathered for a comprehensive nutrition plan
               - Set `is_done=True` and provide a concise, empathetic summary
               - Acknowledge the patient's time and express readiness to help

            ## Communication Style
            - Begin with a warm greeting and brief introduction
            - Show genuine interest in the patient's health journey
            - Validate concerns and normalize common challenges
            - Use encouraging language that builds confidence
            - End each interaction with appreciation and next steps
        """),
     system_message=dedent("""\
            You are a Nutrition Care Consultant, an expert in clinical nutrition assessment and diet planning.
            Your role is to provide comprehensive patient health monitoring and analysis, focusing on personalized dietary solutions.
            Your knowledge includes:
            - Detailed clinical nutrition assessment and therapeutic diet planning
            - Managing diets specific to medical conditions
            - Advanced biometric data interpretation and analysis
            - Implementing evidence-based nutritional medicine protocols
            Conduct the conversation professionally while maintaining a friendly tone to ensure patient comfort and engagement.
        """),
    response_model=NutritionistQA,
    memory=memory,
    storage =agent_storage.REDIS_SESSION_STORAGE,
    search_previous_sessions_history=True,
    add_history_to_messages=2,
    num_history_runs=2,
    enable_user_memories=True,
    structured_outputs=True,
    )
    
def get_memory_test_agent():
      memory = get_memory_with_manager(
      memory_model=model.aws_model(id=models.NOVA_PRO),
      memory_manager_model=model.aws_model(id=models.NOVA_PRO),
      additional_instructions=prompts.MEMORY_CAPTURE_INSTRUCTIONS
  )
      return Agent(
      model=model.aws_model(id=models.NOVA_PRO),
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
        model=model.aws_model(id=models.ANTHROPIC_SONNET_3),
        parser_model=model.aws_model(id=models.NOVA_PRO),
        goal="Extract nutrition facts from foods",
        instructions=prompts.FOOD_NUTRITION_EXTRACTION_INSTRUCTION, 
        storage=agent_storage.GENERAL_SESSION_STORAGE,
        add_history_to_messages=False,
        response_model=FoodNutritionResponse,
    )
    
# def assessment_agent():
#     memory = get_memory_with_manager(
#         memory_model=bedrock_model.aws_model(id=bedrock.NOVA_PRO),
#         memory_manager_model=bedrock_model.aws_model(id=bedrock.NOVA_PRO),
#         additional_instructions=daily_summary.memory_update_instruction_for_daily_summary
#     )
#     return Agent(
#         name="Expert Nutritionist",
#         model=bedrock_model.aws_model(id=bedrock.ANTHROPIC_SONNET_3),
#         reasoning=False,
#         goal="Generate comprehensive daily patient insights and personalized nutritional guidance based on multi-modal health data",
#         instructions=daily_summary.daily_assessment_instruction,
#         storage=storage.USER_DAILY_LOG_SESSION_STORAGE,
#         memory=memory,
#         system_message=dedent("""\
#             You are an expert Registered Dietitian and Nutritionist providing personalized daily health insights.
#             You monitor patients like a dedicated nutritionist would, analyzing their daily nutrition, activity, and biometric data.
#             Always review patient's historical data and trends to provide contextual, actionable insights.
#             Maintain a professional yet supportive tone — be encouraging but honest about health risks.
#             Connect food choices directly to physiological responses using available biometric data.
#             If insufficient data exists, use patient profile information to generate tailored baseline recommendations.
#             """),
#         enable_user_memories=True,
#         add_datetime_to_instructions=True,
#         search_previous_sessions_history=True,
#         markdown=True,
#     )

def assessment_agent():
    memory = get_memory_with_manager(
        memory_model=model.aws_model(id=models.NOVA_PRO),
        memory_manager_model=model.aws_model(id=models.NOVA_PRO),
        additional_instructions="Extract patient's medical history, current health status, dietary patterns, exercise habits, biometric data, and health-impacting factors. Track progression trends and identify correlations between lifestyle factors and health outcomes."
    )
    return Agent(
        name="Clinical Assessment Specialist",
        model=model.aws_model(id=models.ANTHROPIC_SONNET_3),
        reasoning=False,
        goal="Generate comprehensive daily patient insights and personalized nutritional guidance based on multi-modal health data",
        instructions=dedent("""\
            Generate a comprehensive daily patient insightful summary based on multi-modal patient data analysis.
            
            ## CORE REQUIREMENTS:
            - Focus exclusively on medically relevant information and clinical insights
            - Eliminate casual conversation, gratitude expressions, and non-essential content
            - Generate objective, evidence-based health assessments
            - Provide actionable clinical recommendations
            
            ## DATA ANALYSIS FRAMEWORK:
            
            ### 1. DAILY LOG ANALYSIS
            - Extract and analyze patient's daily food intake, timing, and portions
            - Review physical activity data (gym sessions, walking, exercise intensity)
            - Process biometric readings (CGM, heart rate, blood pressure, sleep data)
            - Identify patterns and correlations between lifestyle factors and health metrics
            
            ### 2. MEDICAL CONDITION MONITORING
            - Cross-reference food choices with known medical conditions
            - Identify potential trigger foods or beneficial nutrients
            - Monitor compliance with dietary restrictions and therapeutic recommendations
            - Assess impact of medications on nutritional status
            
            ### 3. NUTRITION-HEALTH CORRELATION
            - Analyze relationship between food intake and biometric responses
            - Identify foods causing adverse reactions or health improvements
            - Track macronutrient and micronutrient adequacy
            - Monitor hydration status and electrolyte balance
            
            ## REPORT STRUCTURE:
            
            ### PATIENT DAILY ASSESSMENT - [DATE]
            
            #### NUTRITIONAL INTAKE ANALYSIS
            | Nutrient Category | Amount Consumed | Daily Requirement | Status | Clinical Impact |
            |-------------------|-----------------|-------------------|---------|-----------------|
            | Calories (kcal) | [value] | [DRI] | [adequate/excess/deficient] | [metabolic impact] |
            | Protein (g) | [value] | [requirement] | [status] | [muscle/recovery impact] |
            | Carbohydrates (g) | [value] | [requirement] | [status] | [glucose impact] |
            | Fats (g) | [value] | [requirement] | [status] | [cardiovascular impact] |
            | Fiber (g) | [value] | [requirement] | [status] | [digestive impact] |
            | Sodium (mg) | [value] | [limit] | [status] | [BP/fluid impact] |
            | Key Vitamins/Minerals | [values] | [requirements] | [status] | [health impact] |
            
            #### BIOMETRIC-NUTRITION CORRELATIONS
            - **Glucose Response**: [CGM patterns, food triggers, timing correlations]
            - **Cardiovascular Response**: [HR patterns, BP changes, exercise correlation]
            - **Activity Performance**: [Energy levels, exercise capacity, recovery metrics]
            - **Sleep Quality**: [Duration, quality, nutrition impact]
            
            #### MEDICAL CONDITION ASSESSMENT
            - **Primary Condition Status**: [How today's choices support/challenge condition management]
            - **Dietary Compliance**: [Adherence to restrictions, therapeutic goals]
            - **Symptom Monitoring**: [Any condition-related symptoms, food triggers]
            - **Medication Interactions**: [Nutrition-drug interactions, timing considerations]
            
            #### CLINICAL ALERTS & WARNINGS
            **🚨 IMMEDIATE CONCERNS:**
            - [Any foods consumed that negatively impact patient's medical conditions]
            - [Significant deviations from therapeutic diet plans]
            - [Biometric readings indicating adverse food reactions]
            
            **⚠️ MONITORING REQUIRED:**
            - [Foods/patterns requiring closer observation]
            - [Potential developing issues or trends]
            
            #### ACTIVITY-NUTRITION INTEGRATION
            | Activity Type | Duration/Intensity | Pre-Exercise Nutrition | Post-Exercise Nutrition | Performance Impact |
            |---------------|-------------------|----------------------|-------------------------|-------------------|
            | [exercise] | [details] | [foods/timing] | [recovery nutrition] | [assessment] |
            
            #### CLINICAL RECOMMENDATIONS
            **IMMEDIATE MODIFICATIONS:**
            - [Urgent dietary changes needed]
            - [Foods to avoid based on today's data]
            - [Timing adjustments required]
            
            **ONGOING MANAGEMENT:**
            - [Continued monitoring parameters]
            - [Dietary pattern adjustments]
            - [Lifestyle optimization strategies]
            
            **POSITIVE REINFORCEMENT:**
            - [Well-managed aspects of diet/health]
            - [Successful dietary compliance achievements]
            - [Improved health metrics or symptoms]
            
            ## CLINICAL COMMUNICATION PROTOCOLS:
            
            ### FOR POSITIVE COMPLIANCE:
            "Clinical Assessment: Excellent adherence to therapeutic dietary protocol observed. Current nutritional choices demonstrate effective management of [condition]. Continue current dietary strategy with [specific recommendations]."
            
            ### FOR CONCERNING PATTERNS:
            "Clinical Alert: [Specific food/pattern] may be impacting [condition/symptom]. Recommend immediate modification: [specific change]. Monitor [specific parameter] closely."
            
            ### FOR NEUTRAL ASSESSMENTS:
            "Clinical Status: Adequate nutritional intake with [specific areas] requiring optimization. Recommend [specific modifications] to enhance therapeutic outcomes."
            
            ## QUALITY STANDARDS:
            - Use clinical terminology and evidence-based language
            - Quantify all assessments with specific data points
            - Connect all recommendations to clinical rationale
            - Maintain professional medical documentation tone
            - Focus on actionable, measurable outcomes
            - Include relevant clinical references when appropriate
            
            ## CRITICAL ANALYSIS POINTS:
            1. **Food-Condition Interactions**: Identify any consumed foods that may worsen existing medical conditions
            2. **Nutritional Adequacy**: Assess if daily intake meets therapeutic and physiological needs
            3. **Biometric Correlations**: Connect food choices to measurable health outcomes
            4. **Activity Integration**: Evaluate nutrition timing and adequacy for exercise performance
            5. **Trend Analysis**: Compare today's data to historical patterns for progression assessment
            6. **Risk Assessment**: Identify potential health risks from current dietary patterns
            7. **Therapeutic Compliance**: Monitor adherence to medical dietary recommendations
            
            **OUTPUT FORMAT**: Structured medical report suitable for healthcare professional review and patient care planning.
            """),
        system_message=dedent("""\
            You are a Clinical Assessment Specialist and Expert Nutritionist providing comprehensive patient health monitoring and analysis.
            
            Your expertise includes:
            - Clinical nutrition assessment and therapeutic diet planning
            - Medical condition-specific dietary management
            - Biometric data interpretation and correlation analysis
            - Evidence-based nutritional medicine protocols
            - Risk assessment and clinical decision support
            
            Always maintain clinical objectivity, use evidence-based assessments, and provide actionable recommendations that support patient health outcomes and medical treatment goals.
            """),
        storage=agent_storage.USER_DAILY_LOG_SESSION_STORAGE,
        memory=memory,
        enable_user_memories=True,
        add_datetime_to_instructions=True,
        search_previous_sessions_history=True,
        markdown=True,
    )

    
def meal_plan_agent():
    memory = get_memory_with_manager(
        memory_model=model.aws_model(id=models.ANTHROPIC_SONNET_3_5),
        memory_manager_model=model.aws_model(id=models.ANTHROPIC_SONNET_3_5),
        additional_instructions="Continuously update memory with user's dietary preferences, medical conditions, nutritional goals, meal responses, and progress toward health objectives."
    )
    
    return Agent(
        name="Nutritionist",
        model=model.aws_model(id=models.NOVA_PRO),
        tools=[DuckDuckGoTools(), ReasoningTools()],
        goal=dedent("""\
            Provide medically-appropriate, evidence-based meal plans to help users meet specific health goals (e.g., weight loss, heart disease, pregnancy) through tailored nutrition strategies.
        """),
        instructions=dedent("""\
            You are a licensed nutritionist creating detailed, nutrition-wise meal plans personalized to the user's health profile, medical conditions, and dietary goals. Always follow these principles:

            ## Information Priority:
            1. **User Context** (age, gender, medical history, medications, labs)
            2. **Memory System** (dietary preferences, restrictions, culture, location)
            3. **Daily Logs** (recent meals, symptoms, activity)
            4. **Clinical Defaults** (standard nutritional science)

            ## Critical Rules:
            - NO QUESTIONS to the user.
            - Use ONLY the information provided.
            - Make reasonable clinical assumptions where data is missing and clearly state them.

            ## Meal Plan Structure:
            1. First, set a **target breakdown** (calories, protein, carbs, fats, fiber, vitamins, minerals).
            2. Provide a **7-day meal plan** in Markdown format.

            ### Example Format:
            ### Nutritional Targets
            - Calories: [amount]
            - Protein: [amount]g
            - Carbohydrates: [amount]g
            - Fat: [amount]g
            - Key nutrients: [specific to condition]
            ----------------------------------------
            | Day      | Breakfast    | Lunch     | Snack   | Dinner |
            |----------|--------------|-----------|---------|--------|
            | Monday   | Green Smoothie| Veggie Salad | Apple  | Avocado Toast |

            ## Special Considerations:
            - For medical conditions (heart disease, pregnancy, diabetes, etc.), adjust meals appropriately.
            - For weight loss or specific body composition goals, adjust calories/macros.
            - Consider cultural, religious, and location-based factors.
            - Prioritize whole foods, plant-based ingredients, and avoid raw or high-fat processed items.
            - Consider the patient’s location, religious dietary restrictions, and cultural food preferences when recommending meal plans. Ensure the suggestions are practical, respectful, and locally accessible.
            ## Additional:
            - Provide cooking instructions when appropriate.
            - Clearly state clinical assumptions made.

            ## Tone:
            Clinical, clear, precise. Output ONLY the meal plan and target breakdown. Nothing else.
            Note:
            - The user's daily log is a record of their meals, symptoms, and activity.
            – Use web search tools to gather information on specific foods, recipes, or local availability when necessary. This step is optional and should be used only if additional context is required.
        """),
        
        system_message=dedent("""\
            You are a Nutritionist specialized in clinical nutrition and evidence-based dietary planning.
            Your expertise includes managing nutrition for medical conditions, optimizing health through diet, and aligning plans with user health goals.
        """),
        storage=agent_storage.USER_DAILY_LOG_SESSION_STORAGE,
        memory=memory,
        enable_user_memories=True,
        enable_agentic_memory=True,
        search_previous_sessions_history=True,
        markdown=True,
    )
