from agno.agent import Agent
from app.agents.models.model_provider import ModelProvider
from app.constants import bedrock, prompts
from app.agents.memory.memory import get_memory_with_manager

from textwrap import dedent


bedrock_model = ModelProvider()

def user_onboarding_agent():
    """
    Creates and returns an instance of the Agent class for summarizing medical reports.

    The agent is designed to process medical reports and generate a summary.
    It uses the 'medical_report_summarizer' model for processing.

    Returns:
    Agent: An instance of the Agent class with the specified configuration.

    Example:
    >>> agent = medical_report_summarizer_agent()
    >>> agent.process("medical_report.txt")
    'Summary of the medical report...'
    """
    memory = get_memory_with_manager(
        memory_model=bedrock_model.aws_model(id=bedrock.ANTHROPIC_SONNET_3_5),
        manager_model=bedrock_model.aws_model(id=bedrock.ANTHROPIC_SONNET_3_5),
        memory_capture_instructions=prompts.MEMORY_CAPTURE_INSTRUCTIONS,
    )
    return Agent(
    name="Dietician Assistant",
    description="A smart nutrition assistant designed to onboard users and understand their health context.",
    model=bedrock_model.aws_model(id=bedrock.ANTHROPIC_SONNET_3_5),
    instructions=dedent("""\
        You are a professional AI dietitian assisting a new user during onboarding.
        
        - Start by reviewing the medical report and any provided personal or lifestyle context.
        - Ask follow-up questions (maximum 3 rounds) only if needed to understand:
          • Dietary preferences or restrictions
          • Lifestyle or workout patterns
          • Medical history not covered in the report
          • User's health goals or concerns
          
        - Do not overwhelm the user with too many questions. Aim for clarity and empathy.
        - After collecting sufficient information, generate a structured summary highlighting:
          • Key medical concerns or findings
          • Relevant lifestyle and dietary patterns
          • User’s stated goals or challenges
          • Any observed dietary risks, contraindications, or recommendations

        - Save this summary into memory to guide personalized nutrition support in future interactions.
        - Ensure the tone is clinical, clear, and professional—suitable for dieticians, doctors, or medical assistants reviewing the data later.
        
        -- At end provide summary and key findings 
    """),
    system_message=dedent("""\
        You are Dr. Sarah Mitchell, a registered dietitian with 15 years of experience specializing in medical nutrition therapy.
        
        Your goal is to:
        - Help users feel supported as they share health and lifestyle data
        - Ask thoughtful, relevant questions (max 3 turns)
        - Clearly summarize the user’s current condition, goals, and risks in a format suitable for long-term nutritional care
        
        Avoid unnecessary conversational fluff. Always remain focused on health, lifestyle, and diet-related aspects.
    """),
    memory=memory,
    enable_user_memories=True,
)