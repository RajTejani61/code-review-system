import os
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "mistral-small-2603")
llm = ChatMistralAI(model_name=LLM_MODEL_NAME)

# Authentication Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
