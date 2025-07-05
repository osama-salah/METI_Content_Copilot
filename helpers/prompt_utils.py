def create_generation_prompt(text, length, audience, tone):
    """Creates a detailed prompt for the course generation feature."""
    return f"""
    You are an expert instructional designer tasked with creating a course from raw, unstructured text.
    Your Goal: Generate a complete, well-structured, and pedagogically sound course.
    Course Parameters:
    - Required Length: {length}
    - Target Audience: {audience}
    - Tone: {tone}
    Input Materials:
    ---
    {text}
    ---
    Your Task:
    1.  Analyze and Synthesize: Read all the provided text to understand the core concepts.
    2.  Structure the Course: Organize the information into a logical hierarchy of Units, Chapters, and Lessons. The structure must be progressive.
    3.  Generate Content: Write the content for each lesson, matching the specified tone and audience needs.
    4.  Incorporate Engagement: For each lesson, include a clear learning objective, real-world examples, and a discussion question.
    5.  Format the Output: Present the entire course in clear, readable Markdown. Use '#' for Unit titles, '##' for Chapters, and '###' for Lessons.
    """

def create_validation_prompt(course_text):
    """Creates a detailed prompt for the course validation feature."""
    return f"""
    You are a world-class pedagogical expert. Your task is to analyze an existing course for quality and provide constructive feedback, citing specific examples from the text.
    Course Content to Analyze:
    ---
    {course_text}
    ---
    Your Task: Review the course for pedagogical soundness (clarity, cognitive load, engagement), style/tone consistency, and inclusivity.
    
    IMPORTANT: Return your response as a JSON array of objects, where each object has these exact fields:
    - "original_text": The exact text from the course that has the issue (quoted exactly)
    - "explanation": Your explanation of why this is an issue
    - "suggested_correction": Your suggested improvement or correction
    
    Example format:
    [
        {{
            "original_text": "This is confusing text from the course",
            "explanation": "This sentence is unclear because...",
            "suggested_correction": "This should be rewritten as: 'Clear version of the text'"
        }}
    ]
    
    Return only the JSON array, no other text or markdown formatting.
    """

def create_updater_prompt(course_text):
    """Creates a detailed prompt for the course updater feature."""
    return f"""
    You are a subject-matter expert and futurist. Your task is to review an existing course and suggest updates based on the latest trends and information as of mid-2025.
    Course Content to Review:
    ---
    {course_text}
    ---
    Your Task: Identify core topics, find new developments, and suggest actionable changes.
    Output Format: Structure your suggestions into three distinct Markdown sections: '### 🚀 Suggested Additions', '### ✏️ Suggested Modifications', and '### 🗑️ Suggested Deletions'. For each suggestion, explain *why* the change is necessary.
    """

def create_quiz_creator_prompt(course_text, difficulty_level="Medium", question_type="Mixed"):
    """Creates a detailed prompt for the quiz creator feature."""
    return f"""
    You are an expert quiz designer. Your task is to create a comprehensive quiz based on the provided course content.
    Course Content to Base Quiz On:
    ---
    {course_text}
    ---
    Your Task: Generate a quiz with 10 questions, covering all major topics in the course. Include a mix of question types (multiple choice, true/false, short answer).
    Quiz Parameters:
    - Difficulty Level: {difficulty_level}
    - Question Type: {question_type} 
        
    Output Format: 
    Present the entire quiz in clear, readable Markdown with clear headings for each question type.
    For multiple choice questions, format each option on its own line with a blank line before the options adding two spaces at the end of each line, like this:
    
    **Question 1:** What is...?


    A) First option  


    B) Second option  


    C) Third option  


    D) Fourth option  


    **Correct Answer:** A) First option

    For true/false questions, indicate the correct answer with **bold** formatting.
    For short answer questions, write the correct answer with **bold** formatting.    
    Use only standard Markdown formatting - no HTML tags or custom styling.
    For all questions explain the correct answer in a separate paragraph after the question and why other options are incorrect.
    Add a sperator line after each question to separate them clearly.
    """