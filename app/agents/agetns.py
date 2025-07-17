import os
from textwrap import dedent


from agno.agent import Agent
from app.agents.models.model_provider import ModelProvider
from app.constants import models
from app.agents.memory.memory import get_memory_with_manager
from app.constants.prompts import prompts, daily_summary
from app.schemas.NutritionistQA import NutritionistQA
from app.schemas.MealPlanTemplate import NutritionistMealPlanTemplate

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
        memory_model=model.aws_model(id=models.ANTHROPIC_SONNET_3_5),
        memory_manager_model=model.aws_model(id=models.ANTHROPIC_SONNET_3_5),
        additional_instructions="Extract patient's medical history, current health status, dietary patterns, exercise habits, biometric data, and health-impacting factors. Track progression trends and identify correlations between lifestyle factors and health outcomes."
    )
    return Agent(
        name="Clinical Assessment Specialist",
        model=model.aws_model(id=models.NOVA_PRO),
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
        additional_instructions=(
            "Track user's medical conditions, dietary preferences, nutritional goals, "
            "meal responses, and health progress."
        )
    )

    return Agent(
        name="Clinical Nutritionist",
        model=model.aws_model(id=models.ANTHROPIC_SONNET_4),
        goal=(
            "Create medically-tailored meal plans with specific nutritional targets "
            "and cooking resources for optimal health outcomes."
        ),
        instructions=dedent("""\
            You are a clinical nutritionist creating therapeutic meal plans based on health conditions and goals.
            
            # 🥦 Dietitian Meal Planner Template

            ## 🧾 Client Information
            | Field                      | Description                                  |
            |---------------------------|----------------------------------------------|
            | Full Name                 |                                              |
            | Age / Gender              |                                              |
            | Height / Weight / BMI     |                                              |
            | Occupation / Lifestyle    | Sedentary / Active / Shift Work, etc.        |
            | Location & Food Access    | For cultural and seasonal food relevance     |
            | Dietary Goals             | Weight loss, weight gain, maintenance, etc.  |
            | Medical History           | Diabetes, PCOS, GI issues, kidney disease, etc. |
            | Food Allergies/Intolerances | Gluten, lactose, nuts, etc.               |
            | Dietary Preferences       | Vegetarian, Vegan, Paleo, Low-FODMAP, etc.   |
            | Religious/Cultural Factors| Halal, Kosher, Hindu Veg, etc.               |

            ---

            ## ⚕️ Clinical & Nutritional Assessment
            | Metric / Lab Result       | Notes                                        |
            |---------------------------|----------------------------------------------|
            | Blood Pressure            |                                              |
            | Fasting Blood Sugar / A1C |                                              |
            | Lipid Profile             | HDL / LDL / Triglycerides                    |
            | Hemoglobin / Iron Levels  |                                              |
            | Vitamin D / B12           |                                              |
            | Digestive Symptoms        | Bloating, constipation, GERD, etc.           |
            | Appetite / Cravings       |                                              |
            | Menstrual/Thyroid Status  | (if applicable)                              |

            ---

            ## 📅 Weekly Meal Plan Overview
            | Day       | Breakfast | Snack (AM) | Lunch | Snack (PM) | Dinner | Notes (timing, hydration, etc.) |
            |-----------|-----------|------------|-------|------------|--------|----------------------------------|
            | Monday    |           |            |       |            |        |                                  |
            | Tuesday   |           |            |       |            |        |                                  |
            | Wednesday |           |            |       |            |        |                                  |
            | Thursday  |           |            |       |            |        |                                  |
            | Friday    |           |            |       |            |        |                                  |
            | Saturday  |           |            |       |            |        |                                  |
            | Sunday    |           |            |       |            |        |                                  |

            ---

            ## 🥗 Daily Sample Meal Plan (Example)
            ### Breakfast (7:30 AM – 9:00 AM)
            - High-fiber cereal + low-fat milk + berries  
            - Boiled egg / tofu scramble (protein boost)  
            - Herbal tea / black coffee  

            ### Mid-Morning Snack (11:00 AM)
            - Fruit + handful of seeds  
            - Coconut water  

            ### Lunch (1:00 PM – 2:00 PM)
            - Brown rice / quinoa  
            - Grilled chicken / lentils  
            - Cooked vegetables + salad  
            - Low-fat yogurt  

            ### Afternoon Snack (4:30 PM)
            - Roasted chickpeas or hummus + cucumber sticks  
            - Green tea  

            ### Dinner (7:00 PM – 8:30 PM)
            - Soup + whole grain bread  
            - Steamed vegetables + lean protein  
            - Herbal infusion / warm milk  

            ---

            ## ⚖️ Macronutrient & Caloric Breakdown (Customize Per Client)
            | Nutrient     | Daily Goal | % of Total Calories |
            |--------------|------------|----------------------|
            | Calories     | 1800 kcal  | 100%                 |
            | Carbohydrates| 200g       | ~45–50%              |
            | Protein      | 80g        | ~20–25%              |
            | Fat          | 50g        | ~25–30%              |
            | Fiber        | 25–35g     |                      |
            | Water        | 2.5–3L     |                      |

            ---

            ## 🔁 Food Rotation Ideas
            - **Grains:** Oats, quinoa, bulgur, millet, brown rice  
            - **Proteins:** Eggs, paneer, chicken, legumes, tofu  
            - **Vegetables:** Leafy greens, carrots, gourds, peppers  
            - **Fruits:** Banana, papaya, guava, berries, citrus  
            - **Healthy Fats:** Nuts, seeds, olive oil, ghee (moderation)  

            ---

            ## 🧠 Behavior & Lifestyle Recommendations
            | Area               | Advice                                      |
            |--------------------|---------------------------------------------|
            | Sleep              | 7–8 hrs/night                               |
            | Physical Activity  | 30–45 mins most days (walk, yoga, gym)      |
            | Stress Management  | Deep breathing, mindfulness, journaling     |
            | Meal Timing        | Regular meals; avoid late-night eating      |
            | Hydration          | Minimum 8–10 glasses/day                    |
            | Supplementation    | As per deficiencies (e.g., Vitamin D, B12)  |

            ---

            ## 📈 Follow-Up & Monitoring Schedule
            | Week | Goal / Focus               | Plan                               |
            |------|----------------------------|------------------------------------|
            | 1    | Diet initiation & adherence| Review response, adjust portions   |
            | 2    | Monitor energy & symptoms  | Check stool, sleep, hunger cues    |
            | 4    | Lab tests / progress check | Modify calories/macros if needed   |
            | 6+   | Sustainable habits         | Introduce mindful eating, diversity|

            > ✅ **Note to Dietitian:** Always personalize according to client’s metabolic health, local food culture, accessibility, and readiness for change.

            Output ONLY the structured meal plan above. No additional text.
        """),
        system_message=(
            "You are a Clinical Dietitian specializing in medical nutrition therapy. "
            "Create evidence-based meal plans that address specific health conditions through "
            "targeted dietary interventions with practical cooking resources."
        ),
        storage=agent_storage.USER_DAILY_LOG_SESSION_STORAGE,
        memory=memory,
        enable_user_memories=True,
        enable_agentic_memory=True,
        search_previous_sessions_history=True,
        markdown=True,
        # use_json_mode=True,
    )
