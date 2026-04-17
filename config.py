from langchain_mistralai import ChatMistralAI

from dotenv import load_dotenv
load_dotenv()

llm = ChatMistralAI(model_name="mistral-small-2603")
