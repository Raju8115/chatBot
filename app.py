# chatbot_api.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
from langchain_ibm import ChatWatsonx
from ibm_watsonx_ai.foundation_models.schema import TextChatParameters

app = FastAPI()

# Set up the model
llm = ChatWatsonx(
    model_id="meta-llama/llama-3-3-70b-instruct",
    url="https://us-south.ml.cloud.ibm.com",
    apikey="29WIfrKNds3_V-Xu7V1SXlD3_u07yGsn_StXDZWsBr0u",
    project_id="1a19fecc-1677-454b-bbc4-20152081b5e5",
    params=TextChatParameters(max_tokens=100, temperature=0.5)
)

class Input(BaseModel):
    question: str

@app.post("/ask")
def ask_question(input: Input):
    response = llm.invoke(input.question)
    return {"answer": response.content}
