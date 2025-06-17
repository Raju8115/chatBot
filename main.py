from ibm_watsonx_ai.foundation_models import ModelInference
api_key = "29WIfrKNds3_V-Xu7V1SXlD3_u07yGsn_StXDZWsBr0u"
project_id = "1a19fecc-1677-454b-bbc4-20152081b5e5"
from dotenv import load_dotenv
from langchain_ibm.chat_models import ChatWatsonx
import os
from ibm_watsonx_ai.foundation_models.schema import TextChatParameters
parameters = TextChatParameters(
max_tokens=100,
temperature=0.5,
top_p=1,
)
from langchain_ibm import ChatWatsonx
watsonx_llm = ChatWatsonx(
model_id="meta-llama/llama-3-3-70b-instruct",
url="https://us-south.ml.cloud.ibm.com",
apikey=api_key,
project_id=project_id,
params=parameters,
)
def answer_question(prompt):
    response = watsonx_llm.invoke(prompt)
    return response
if __name__ == "__main__":
    while True:
        question = input("\nAsk me anything (or type 'exit'): ")
        if question.lower() == "exit":
            break
        try:
            response = answer_question(question)
            print("Answer:", response.content)
        except Exception as e:
            print(":x: Error:", e)
