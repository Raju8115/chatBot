from flask import Flask, request, jsonify
from langchain_ibm import ChatWatsonx
from ibm_watsonx_ai.foundation_models.schema import TextChatParameters

# Watsonx config
api_key = "29WIfrKNds3_V-Xu7V1SXlD3_u07yGsn_StXDZWsBr0u"
project_id = "1a19fecc-1677-454b-bbc4-20152081b5e5"

parameters = TextChatParameters(
    max_tokens=100,
    temperature=0.5,
    top_p=1,
)

# Initialize model
watsonx_llm = ChatWatsonx(
    model_id="meta-llama/llama-3-3-70b-instruct",
    url="https://us-south.ml.cloud.ibm.com",
    apikey=api_key,
    project_id=project_id,
    params=parameters,
)

# Flask app
app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        question = data.get("question")
        if not question:
            return jsonify({"error": "Missing 'question' in request"}), 400

        response = watsonx_llm.invoke(question)
        return jsonify({"answer": response.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "Chat API is running"})

