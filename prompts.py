from langchain.schema import SystemMessage

COURSE_STRUCTURE_SYSTEM_MSG = SystemMessage(
    content="You are a course architect tasked with designing structured educational content in JSON format."
)

COURSE_STRUCTURE_HUMAN_TEMPLATE = """
Using the following summarized content:

{summaries}

Propose **3 to 5 different course structures**. Each structure must include:
- A course introduction
- At least **8 to 10 full chapters**
- Each chapter must have a:
  - 'name' (string): the chapter title
  - 'topics' (list of strings): key topics covered in the chapter

Label each as "Structure 1", "Structure 2", etc.

Respond only with valid **JSON** in the following format:

{{
"structures": [
    {{
    "name": "Structure 1",
    "chapters": [
        {{
        "name": "Chapter Title 1",
        "topics": [
            "Topic A",
            "Topic B"
        ]
        }},
        {{
        "name": "Chapter Title 2",
        "topics": [
            "Topic C",
            "Topic D"
        ]
        }}
    ]
    }}
]
}}

Only include the JSON output. Do **not** add explanations, markdown formatting, or commentary.
"""

COURSE_GENERATION_SYSTEM_MSG = SystemMessage(
    content="You are a professional course designer. Respond only with valid, production-quality HTML."
)

COURSE_GENERATION_HUMAN_TEMPLATE = """
Design a complete, interactive HTML course using the following configuration:

- **Course Title:** {course_name}
- **Type:** {course_type}
- **Length:** {course_length}
- **Tone:** Professional (clear, confident, and instructional)
- **Visual Theme:** Light and modern, clean, attractive UI

###  Course Structure
Use **all the chapters below** exactly as provided. Do not skip or merge any chapter.
Generate **one full chapter per line/item**:

{structure}

###  Summarized Knowledge Base
{summaries}

###  Chapter Requirements
Each chapter must:
- Use the exact title provided in the structure
- Contain a rich introduction
- Explain concepts deeply and clearly
- Include step-by-step breakdowns
- Show real-world examples
- Address 1–2 common misconceptions
- End with a 'Try It Yourself' reflection
- Include a summary with 3–5 bullet points
- Include a quiz with **5–6 MCQs in every chapter** using inline JavaScript

###  Final Course Quiz
At the end of the course, include a **10-question quiz which is not in chapter** with MCQs from across all chapters. Use inline JavaScript for feedback.

###  Design Requirements
- Use **only internal CSS and JS** (no external dependencies)
- Layout should be **light, mobile-friendly, and collapsible**
- Each chapter should be **inside a collapsible section** labeled with the chapter title
- MCQs must be clickable with box with immediate feedback
- Return **only valid HTML** — no Markdown or explanations

 IMPORTANT: Do not skip chapters. Generate one full, rich HTML section for **each chapter listed in the structure above**.
"""


COURSE_GENERATION_SYSTEM_MSG_FOR_JSON = SystemMessage(
    content="You are a professional course designer. Respond only with valid, production-quality JSON."
)

COURSE_GENERATION_HUMAN_TEMPLATE_FOR_JSON = """
Design a complete course using the following configuration and respond in **valid JSON format** only.

### Course Metadata:
- **Title:** {course_name}
- **Type:** {course_type}
- **Length:** {course_length}
- **Tone:** Professional (clear, confident, instructional)
- **Visual Theme Preference:** Light and modern

### Structure Instructions:
Use **all the chapters listed below** exactly as provided. Do not skip, merge, or rename any chapter.
Generate one **complete object per chapter**:

{structure}

### Knowledge Base (for concept reference and summaries):
{summaries}

### JSON Output Schema:
Respond with a JSON object using the following structure:

```json
{{
  "course_title": "string",
  "course_type": "string",
  "course_length": "string",
  "chapters": [
    {{
      "title": "string",
      "introduction": "string",
      "concepts": [
        {{
          "heading": "string",
          "explanation": "string",
          "examples": ["string", "..."],
          "misconceptions": ["string", "..."]
        }}
      ],
      "try_it_yourself": "string",
      "summary_points": ["string", "..."],
      "quiz": [
        {{
          "question": "string",
          "options": ["string", "..."],
          "correct_answer": "string",
          "explanation": "string"
        }}
      ]
    }}
  ],
  "final_quiz": [
    {{
      "question": "string",
      "options": ["string", "..."],
      "correct_answer": "string",
      "explanation": "string"
    }}
  ]
}}
'''
"""
