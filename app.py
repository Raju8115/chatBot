from flask import Flask, request, jsonify
import ibm_db
import os
import requests
from nlp_sql import convert_to_sql, getModel


app = Flask(__name__)

# DB2 connection string (update with your creds)
import ibm_db

DB2_CONN_STR = (
    "DATABASE=bludb;"
    "HOSTNAME=729c534a-3978-4750-89d5-65bbf5a84040-brsao.bt1ibm.db2.ibmappdomain.cloud;"
    "PORT=30901;"
    "PROTOCOL=TCPIP;"
    "UID=3deaf01d;"
    "PWD=FCQvv8t9LGBnTBLC;"
    "SECURITY=SSL;"
)

try:
    conn = ibm_db.connect(DB2_CONN_STR, "", "")
    print("✅ Connected successfully to DB2")
except Exception as e:
    print("❌ Connection failed:", e)


def llm_interpret(question, result):
    model = getModel()
    prompt = (
        f"You are an expert data analyst. "
        f"Given the query result below for quesiton {question}, provide the result in formatted way without paragaph of explanation "
        f"Do not mention the original question or the result explicitly and dont say like its hard to intepret or confusion just if you know just provide a direct , easy-to-understand formated response.\n\n"
        f"Data:\n{result}"
    )
    response = model.chat([{"role": "user", "content": prompt}])
    return response["choices"][0]["message"]["content"].strip()


@app.route("/query", methods=["POST"])
def query_db():
    data = request.get_json()
    question = data.get("question")

    # 1. Convert NL → SQL
    sql = convert_to_sql(question)
    if sql and "```" in sql:
        sql = sql.replace("```sql", "").replace("```", "").strip()

    print(sql)
    try:
        # 2. Run SQL query
        stmt = ibm_db.exec_immediate(conn, sql)

        # 3. Fetch rows
        result = []
        row = ibm_db.fetch_assoc(stmt)
        while row:
            result.append(row)
            row = ibm_db.fetch_assoc(stmt)
        
        interpreted = llm_interpret(question, result)
        print("SQL res ", result)

        return jsonify({"result": interpreted})

    except Exception as e:
        return jsonify({
            "result": [["Sorry, I couldn’t find that information in the database."]],
            "error": str(e)
        }), 200

if __name__ == "__main__":
    app.run(port=8080, debug=True)
