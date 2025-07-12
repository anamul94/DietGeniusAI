memory_capture_instructions = dedent("""\
Memories should include key information that enables the AI dietitian to provide personalized and context-aware nutrition guidance. This includes:

- 👤 **User Profile and Background**
  - Full name, age, gender, location, occupation
  - Lifestyle context (e.g., sedentary, active, shift worker)
  - Health goals (e.g., weight loss, muscle gain, managing diabetes)

- 🧾 **Medical History and Reports**
  - Diagnosed conditions (e.g., diabetes, hypertension, PCOS)
  - Relevant lab test results and biomarkers (e.g., cholesterol, blood sugar, creatinine)
  - Allergies or food intolerances
  - Medications or prescriptions that affect nutrition
  - Medical restrictions or doctor's dietary recommendations

- 🍽️ **Dietary Preferences and Restrictions**
  - Preferred cuisines, foods the user enjoys or dislikes
  - Religious or cultural food practices (e.g., vegetarian, Halal)
  - Known allergies or ingredients to avoid

- 🏃 **Physical Activity and Lifestyle**
  - Typical daily routine or schedule
  - Workout or exercise frequency, type, and duration
  - Sedentary vs active job
  - Sleep patterns or energy complaints

- 📥 **User Input Over Time**
  - Food intake logs and nutrition uploads (photos, entries)
  - Changes in goals or preferences
  - Consistency or adherence to past recommendations

- 🎯 **AI Observations & Long-Term Needs**
  - Trends in lab results or lifestyle behavior
  - Motivation levels or potential mental blocks
  - Long-term support needs (e.g., managing chronic illness, recovering post-surgery)

Focus on capturing facts and insights that will improve long-term personalization, help the AI understand the user's evolving health context, and enable more effective nutrition guidance over time. 

If the user shares casual information (like they dislike a certain food or skipped a workout), capture it if it's relevant to their dietary planning or motivation.
""")
