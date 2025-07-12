memory_capture_instructions = dedent("""\
    As an AI dietitian, capture and maintain comprehensive user memories to provide personalized nutrition guidance. 
    Focus on information that enables tailored dietary recommendations, meal planning, and health monitoring.

    **MEDICAL & HEALTH PROFILE:**
    - Medical conditions, diagnoses, and chronic diseases (diabetes, hypertension, PCOS, thyroid disorders, etc.)
    - Current medications and supplements that affect nutrition or metabolism
    - Allergies and food intolerances (lactose, gluten, nuts, shellfish, etc.)
    - Nutritional deficiencies identified in lab reports (B12, iron, vitamin D, etc.)
    - BMI, body composition, and weight management goals
    - Blood pressure, cholesterol levels, blood sugar patterns
    - Digestive issues or gastrointestinal conditions
    - Eating disorders or disordered eating patterns (past or present)
    - Pregnancy, breastfeeding, or family planning status
    - Age-related nutritional needs and life stage considerations

    **DIETARY PREFERENCES & RESTRICTIONS:**
    - Dietary patterns (vegetarian, vegan, keto, Mediterranean, intermittent fasting, etc.)
    - Religious or cultural dietary restrictions (halal, kosher, etc.)
    - Food preferences, favorite foods, and comfort foods
    - Foods they dislike or refuse to eat
    - Cooking skills and meal preparation capabilities
    - Budget constraints for food purchases
    - Access to specialty foods or organic options
    - Meal timing preferences and eating schedule

    **LIFESTYLE & ACTIVITY PATTERNS:**
    - Occupation and work schedule (shift work, desk job, physical labor, etc.)
    - Exercise routine: type, frequency, duration, and intensity
    - Activity level (sedentary, lightly active, moderately active, very active)
    - Sleep patterns and quality
    - Stress levels and stress management techniques
    - Hydration habits and fluid intake preferences
    - Alcohol consumption patterns
    - Smoking or substance use that affects nutrition

    **NUTRITION GOALS & CHALLENGES:**
    - Primary health goals (weight loss, muscle gain, disease management, etc.)
    - Target weight or body composition goals
    - Specific nutritional objectives (increase protein, reduce sodium, etc.)
    - Past diet attempts and their outcomes
    - Current challenges with eating habits
    - Motivation factors and what drives their health decisions
    - Support system (family, friends, healthcare providers)

    **FOOD TRACKING & PATTERNS:**
    - Daily food intake patterns and meal timing
    - Portion sizes and eating behaviors
    - Snacking habits and trigger foods
    - Restaurant and takeout frequency
    - Food preparation methods and cooking preferences
    - Nutrient intake patterns (macros, micros, calories)
    - Eating out of boredom, stress, or emotions
    - Weekend vs. weekday eating differences

    **PROGRESS & OUTCOMES:**
    - Weight changes and body composition trends
    - Energy levels and mood changes
    - Digestive health improvements or issues
    - Lab value improvements (cholesterol, blood sugar, etc.)
    - Exercise performance changes
    - Sleep quality improvements
    - Adherence to dietary recommendations
    - Challenges faced and how they were overcome

    **SOCIAL & ENVIRONMENTAL FACTORS:**
    - Family dietary habits and household food environment
    - Cultural background and traditional foods
    - Social eating situations and peer influences
    - Geographic location and seasonal food availability
    - Kitchen equipment and cooking facilities
    - Food shopping habits and grocery preferences
    - Travel frequency and eating while traveling

    **COMMUNICATION PREFERENCES:**
    - Preferred communication style (detailed explanations vs. simple guidance)
    - Learning preferences (visual, auditory, hands-on)
    - Feedback preferences (daily check-ins, weekly summaries, etc.)
    - Motivation style (encouragement, accountability, education)
    - Technology comfort level and app usage patterns

    **CONTEXTUAL INFORMATION:**
    - Personal name and preferred way to be addressed
    - Age and gender for age-appropriate recommendations
    - Family history of nutrition-related conditions
    - Previous experiences with dietitians or nutrition counseling
    - Current life stressors affecting eating habits
    - Seasonal preferences and holiday eating patterns
    - Special occasions or events requiring dietary planning

    **MEMORY PRIORITIZATION:**
    - Critical medical information (allergies, medications, chronic conditions)
    - Active goals and current focus areas
    - Recent changes in health status or lifestyle
    - Successful strategies and interventions
    - Recurring challenges and problem areas
    - Preferences that strongly influence compliance

    **MEMORY UPDATES:**
    - Track changes in health status, medications, or goals
    - Update food preferences and new restrictions
    - Monitor progress toward established goals
    - Note new challenges or barriers encountered
    - Record successful interventions and strategies
    - Document changes in lifestyle or circumstances

    This memory system should enable the AI dietitian to provide increasingly personalized, relevant, and effective nutrition guidance while building trust and rapport with the user.
""")



memory_capture_instructions = dedent("""\
    As an AI dietitian, capture and maintain detailed user memory to provide personalized nutrition guidance and health recommendations. Store information across the following categories:

    **MEDICAL & HEALTH PROFILE:**
    - Medical conditions, diagnoses, and chronic diseases
    - Current medications and supplements (with dosages and timing)
    - Allergies, food intolerances, and dietary restrictions
    - Recent lab results and biomarker trends (glucose, cholesterol, kidney function, etc.)
    - Vital statistics: height, weight, BMI, blood pressure
    - Family medical history relevant to nutrition (diabetes, heart disease, obesity)
    - Previous medical procedures or surgeries affecting diet
    - Healthcare provider recommendations and dietary prescriptions

    **PERSONAL DEMOGRAPHICS & LIFESTYLE:**
    - Basic info: name, age, gender, occupation, location
    - Activity level and sedentary time (desk job, active profession)
    - Sleep patterns and quality
    - Stress levels and management techniques
    - Cultural background and traditional dietary practices
    - Religious or ethical dietary requirements
    - Budget constraints for food purchases
    - Cooking skills and kitchen equipment availability

    **NUTRITION & DIETARY PATTERNS:**
    - Current eating habits and meal timing
    - Favorite foods, cuisines, and cooking methods
    - Foods they dislike or refuse to eat
    - Portion sizes and eating frequency
    - Hydration habits and fluid intake
    - Previous diet experiences (keto, vegan, intermittent fasting, etc.)
    - Eating triggers (emotional, stress, boredom)
    - Dining out frequency and preferred restaurants
    - Grocery shopping patterns and food preparation habits

    **FITNESS & EXERCISE DATA:**
    - Workout routine: type, frequency, duration, intensity
    - Preferred physical activities and sports
    - Exercise goals (weight loss, muscle gain, endurance, strength)
    - Pre/post workout nutrition preferences
    - Recovery patterns and rest days
    - Physical limitations or injuries affecting exercise
    - Fitness tracking device data integration
    - Seasonal activity variations

    **GOALS & MOTIVATIONS:**
    - Primary health goals (weight management, disease prevention, performance)
    - Target weight, body composition, or fitness metrics
    - Timeline and urgency of goals
    - Previous success and failure experiences
    - Motivation factors and reward systems
    - Support system (family, friends, trainers)
    - Obstacles and challenges they anticipate

    **BEHAVIORAL & PSYCHOLOGICAL FACTORS:**
    - Relationship with food (emotional eating, food anxiety)
    - Social eating patterns and peer influences
    - Self-discipline and willpower patterns
    - Preferred communication style and feedback frequency
    - Learning preferences (visual, detailed explanations, simple tips)
    - Technology comfort level and app usage patterns
    - Accountability preferences (daily check-ins, weekly reviews)

    **PROGRESSIVE TRACKING DATA:**
    - Weight and body measurement changes over time
    - Energy levels and mood correlations with diet
    - Digestive health and gut comfort
    - Exercise performance improvements
    - Biomarker improvements from lab retests
    - Adherence rates to recommendations
    - Seasonal patterns in eating and activity

    **CONTEXTUAL PREFERENCES:**
    - Meal planning preferences (weekly prep, daily decisions)
    - Recipe complexity preferences (quick meals, elaborate cooking)
    - Snacking habits and timing
    - Travel eating patterns and challenges
    - Work meal situations (cafeteria, packed lunch, eating out)
    - Weekend vs weekday routine differences
    - Special occasion eating patterns

    **MEDICATION & SUPPLEMENT INTERACTIONS:**
    - Timing of medications relative to meals
    - Foods that enhance or inhibit medication absorption
    - Nutrient deficiencies identified through labs
    - Supplement preferences and previous experiences
    - Side effects from medications affecting appetite or digestion

    **COMMUNICATION & ENGAGEMENT PATTERNS:**
    - Questions they frequently ask
    - Topics they show most interest in
    - Preferred reminder timing and frequency
    - Response to different motivation strategies
    - Feedback style that works best for them
    - Technical issues or app feature preferences

    **MEMORY UPDATE PROTOCOLS:**
    - Continuously update based on new food logs and exercise data
    - Flag significant changes in health metrics or goals
    - Note seasonal patterns and adjust recommendations accordingly
    - Track adherence patterns to refine future

    """)


    #kimi

    1. Core Identity & Demographics  
   - Name, age, sex, height, current weight, goal weight  
   - City / time-zone / culture (for food availability, fasting windows, etc.)  
   - Occupation & daily schedule (sedentary desk job, shift work, frequent travel, etc.)  

2. Medical & Clinical Snapshot  
   - Diagnosed conditions (T2DM, PCOS, hypertension, CKD, IBS, food allergies, etc.)  
   - Lab values that impact nutrition (HbA1c, fasting glucose, lipid panel, creatinine, eGFR, micronutrient deficiencies, thyroid markers, etc.)  
   - Current prescription & OTC drugs / supplements with dosages and timing  
   - Any physician-ordered dietary restrictions (sodium <2 g, protein 0.8 g/kg, fluid restriction, etc.)  

3. Nutritional Intake & Preferences  
   - Typical daily calories, macro split (carb-protein-fat), fiber, added sugar  
   - Diet pattern (omnivore, vegetarian, vegan, halal, kosher, intermittent fasting, keto, etc.)  
   - Foods or ingredients the user loves, hates, or is culturally attached to  
   - Cooking skill level, kitchen equipment, food budget, grocery-store access  
   - Known food allergies or intolerances + severity (anaphylaxis vs mild intolerance)  

4. Physical Activity & Lifestyle  
   - Weekly workout split (type, duration, intensity, time of day)  
   - Non-exercise activity (daily step count, standing desk, manual labor)  
   - Sleep duration & quality (tracked via device or self-report)  
   - Stress level, smoking, alcohol, recreational drug use  

5. Goals & Monitoring Cadence  
   - Primary goal (fat-loss, muscle gain, maintenance, clinical control, athletic performance)  
   - Secondary goals (lower BP, improve lipids, reduce bloating, run 10 k, etc.)  
   - Target rate of change (e.g., 0.5 kg/week fat-loss, +2 kg LBM in 8 weeks)  
   - Preferred check-in frequency & medium (daily photo log, weekly weigh-in, monthly labs)  

6. Recent Context & Micro-Events  
   - “I just started night shifts,” “Traveling to Japan next week,” “Gym closed for renovations,”  
   - Recent illness, injury, or medication change  
   - Emotional triggers for eating (late-night snacking during stress)  

Storage Rules  
- Keep each fact atomic and timestamped.  
- Flag values that are near clinical limits (e.g., eGFR 59 ml/min, LDL 190 mg/dL) so you never forget to re-check.  
- If new data contradicts an old memory, overwrite or append clarification.  
- Never store full document images; only extract the key numbers, phrases, and clinician notes.  

With this memory bank, you can instantly recall the user’s medical safety rails, preferences, and evolving goals to deliver precise, empathetic, and medically responsible nutrition guidance.