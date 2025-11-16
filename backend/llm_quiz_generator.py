from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate # type: ignore
from langchain.output_parsers import JsonOutputParser # type: ignore
from langchain.chains import LLMChain # type: ignore
from pydantic import BaseModel, Field

# 1️⃣ Define the quiz schema for structured output
class QuizQuestion(BaseModel):
    question: str = Field(description="The question text")
    options: list[str] = Field(description="A list of four answer options")
    correct_answer: str = Field(description="The correct answer option text")

class QuizResponse(BaseModel):
    quiz: list[QuizQuestion] = Field(description="A list of quiz questions with answers")

# 2️⃣ Define prompt template
prompt_template = PromptTemplate(
    template=(
        "You are an expert quiz generator. "
        "Given the following article, create exactly 5 multiple-choice questions (MCQs) "
        "with 4 options each and provide the correct answer.\n\n"
        "Article:\n{article_text}\n\n"
        "Return the result strictly in JSON format following this structure:\n{format_instructions}"
    ),
    input_variables=["article_text"],
    partial_variables={"format_instructions": JsonOutputParser(pydantic_object=QuizResponse).get_format_instructions()},
)

# 3️⃣ Initialize Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.3,
    google_api_key="YOUR_GOOGLE_API_KEY"  # Replace this with your real Gemini API key
)

# 4️⃣ Setup the parser
parser = JsonOutputParser(pydantic_object=QuizResponse)

# 5️⃣ Create chain
quiz_chain = LLMChain(
    llm=llm,
    prompt=prompt_template,
    output_parser=parser
)

# 6️⃣ Define function to generate quiz
def generate_quiz(article_text: str) -> dict:
    """Generate quiz questions from given article text."""
    try:
        result = quiz_chain.invoke({"article_text": article_text})
        return result
    except Exception as e:
        print("Error generating quiz:", e)
        return {"error": str(e)}
