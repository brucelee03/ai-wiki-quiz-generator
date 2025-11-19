from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

load_dotenv()  # load from .env

# -------------------------------
# 1. Define Pydantic Schema
# -------------------------------

class Question(BaseModel):
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str


class Quiz(BaseModel):
    title: str
    questions: list[Question]  # will hold 5+ questions


# -------------------------------
# 2. Load LLM
# -------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.2,
    api_key="AIzaSyCYSQv-UzhSLq_Z0q5neFipLuy43qRVjTY"
)

parser = JsonOutputParser(pydantic_object=Quiz)


# -------------------------------
# 3. Prompt Template (Updated)
# -------------------------------

format_instructions = parser.get_format_instructions()

prompt = PromptTemplate(
    input_variables=["article_text", "num_questions"],
    template=f"""
You are an expert quiz generator.
Read the following article and create a quiz of **at least {{num_questions}} questions**.

Rules:
- Each question must be clear, factual, and high-quality.
- Provide exactly 4 options labeled A, B, C, D.
- Provide the correct answer.
- Do NOT add explanations.
- Return your output strictly in JSON format.

JSON FORMAT:
{format_instructions}

ARTICLE:
{{article_text}}
"""
)


# -------------------------------
# 4. Quiz Generator Function
# -------------------------------

def generate_quiz(article_text: str, num_questions: int = 5) -> Quiz:
    chain = prompt | llm | parser
    result = chain.invoke({
        "article_text": article_text,
        "num_questions": num_questions
    })
    return result
