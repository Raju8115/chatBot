from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials
from dotenv import load_dotenv
import os

# Load .env file for credentials if present
load_dotenv()

# DB2 schema context

_model_instance = None

def getModel():
    """Singleton pattern for Watsonx model instance"""
    global _model_instance
    if _model_instance is None:
        try:
            creds = Credentials(
                url="https://ca-tor.ml.cloud.ibm.com",
                api_key="UOtMgA5jazmnI2PsrmBa9s18jIfqGRBVKrapNaxrF0V6",
            )
            _model_instance = ModelInference(
                model_id="meta-llama/llama-3-3-70b-instruct",
                credentials=creds,
                project_id="f06b08b3-b5a1-4c67-ae23-92ce02754a66",
            )
        except Exception as e:
            print("Error initializing model:", str(e))
            _model_instance = None
    return _model_instance


def convert_to_sql(natural_query: str) -> str:
    """Converts a natural language query into DB2 SQL using Watsonx.ai model"""
    prompt = f"""
You are an expert SQL generator. 
Target database: IBM DB2.

### SCHEMA DETAILS ###

Table: USERS  
- EMAIL: VARCHAR  
- ID: BIGINT (Primary key)  
- NAME: VARCHAR  
- SLACK_ID: VARCHAR  
- MANAGER_NAME: VARCHAR

Table: PROFESSIONAL_CERTIFICATIONS  
- Stores professional certifications of a user.  
- CERTIFICATION_LEVEL: VARCHAR  
- CERTIFICATION_LINK: VARCHAR  
- CERTIFIED: BOOLEAN  
- ID: BIGINT (Primary key)  
- PENDING_DELETE: BOOLEAN  
- TITLE: VARCHAR (Certification name)  
- USER_ID: BIGINT (FK → USERS.ID)  

Table: USER_ANCILLARY_SKILLS  
- Stores ancillary/extra certifications or skills of a user.  
- CERTIFICATION_LEVEL: VARCHAR  
- CERTIFICATION_LINK: VARCHAR  
- CERTIFIED: BOOLEAN  
- ID: BIGINT (Primary key)  
- PENDING_DELETE: BOOLEAN  
- PRODUCT: VARCHAR  
- RECENCY_OF_CERTIFICATION: VARCHAR  
- TECHNOLOGY: VARCHAR  
- USER_ID: BIGINT (FK → USERS.ID)  

Table: USER_CREDENTIALS  
- Stores user credentials and digital badges.  
- CREDENTIAL_DATE: TIMESTAMP  
- CREDENTIAL_EXPIRY_DATE: TIMESTAMP  
- CREDENTIAL_LABEL: VARCHAR (Credential name)  
- CREDENTIAL_ORDER_ID: VARCHAR  
- CREDENTIAL_STATUS: VARCHAR  
- CREDENTIAL_TYPE: VARCHAR  
- DIGITAL_CREDENTIAL_ID: VARCHAR  
- EMPLOYEE_ID: VARCHAR  
- ID: BIGINT (Primary key)  
- LEARNING_SOURCE: VARCHAR  
- USER_ID: BIGINT (FK → USERS.ID)  

Table: USER_SECONDARY_SKILLS  
- Stores secondary skills and certifications of a user.  
- CERTIFICATION_LEVEL: VARCHAR  
- CERTIFICATION_LINK: VARCHAR  
- DURATION: VARCHAR  
- ID: BIGINT (Primary key)  
- PENDING_DELETE: BOOLEAN  
- PRACTICE: VARCHAR  
- PRACTICE_AREA: VARCHAR  
- PRODUCTS_TECHNOLOGIES: VARCHAR  
- RECENCY_OF_CERTIFICATION: VARCHAR  
- USER_ID: BIGINT (FK → USERS.ID)  

Table: USER_SKILL  
- General skills mapped to practices and technologies.  
- ID: BIGINT (Primary key)  
- PRACTICE_AREA_ID: BIGINT  
- PRACTICE_ID: BIGINT  
- PRACTICE_PRODUCT_TECHNOLOGY_ID: BIGINT  
- PROFESSIONAL_LEVEL: VARCHAR  
- PROJECTS_DONE: VARCHAR  
- SELF_ASSESSMENT_LEVEL: VARCHAR  
- USER_ID: BIGINT (FK → USERS.ID)  

Table: USER_SKILL_INFO  
- Detailed project/skill history for a user.  
- CLIENT_TIER: VARCHAR  
- CLIENT_TIER_V2: VARCHAR  
- DURATION: VARCHAR  
- ID: BIGINT (Primary key)  
- PENDING_DELETE: BOOLEAN  
- PROJECT_COMPLEXITY: VARCHAR  
- PROJECT_TITLE: VARCHAR  
- RESPONSIBILITIES: VARCHAR  
- TECHNOLOGIES_USED: VARCHAR  
- USER_ID: BIGINT (FK → USERS.ID)  
- USER_SKILL_ID: BIGINT (FK → USER_SKILL.ID)  

Table: HIGH_IMPACT_ASSETS  
- Stores high-impact contributions by users.  
- BUSINESS_IMPACT: VARCHAR  
- DESCRIPTION: VARCHAR  
- ID: INTEGER (Primary key)  
- PENDING_DELETE: BOOLEAN  
- TITLE: VARCHAR  
- USER_ID: INTEGER (FK → USERS.ID)  
- VISIBILITY_ADOPTION: VARCHAR  

Table: PRACTICE  
- DESCRIPTION: VARCHAR  
- ID: BIGINT (Primary key)  
- NAME: VARCHAR  

Table: PRACTICE_AREA  
- DESCRIPTION: VARCHAR  
- ID: BIGINT (Primary key)  
- NAME: VARCHAR  
- PRACTICE_ID: BIGINT (FK → PRACTICE.ID)  

Table: PRACTICE_PRODUCT_TECHNOLOGY  
- ID: BIGINT (Primary key)  
- PRACTICE_AREA_ID: BIGINT  
- PRODUCT_NAME: VARCHAR  
- TECHNOLOGY_NAME: VARCHAR  

---

### INSTRUCTIONS FOR QUERY GENERATION ###

1. Always **start from USERS** to filter by user name or email.  
2. Use **only the columns and tables listed in the SCHEMA DETAILS above**.  
   - ❌ Do NOT invent new columns.  
   - ❌ Do NOT assume a `TITLE` column exists if it is not explicitly in the schema.  
   - ✅ If the request mentions a field that does not exist, map it to the most relevant available column.  
   - If no relevant mapping exists, generate a query that returns an empty result set, e.g. `SELECT * FROM USERS WHERE 1=0;`  
3. When the request involves **certifications, credentials, or skills**, check across:  
   - PROFESSIONAL_CERTIFICATIONS → TITLE, CERTIFICATION_LEVEL, CERTIFICATION_LINK, CERTIFIED  
   - USER_CREDENTIALS → CREDENTIAL_LABEL, CREDENTIAL_TYPE, CREDENTIAL_STATUS, CREDENTIAL_DATE, CREDENTIAL_EXPIRY_DATE  
   - USER_ANCILLARY_SKILLS → PRODUCT, TECHNOLOGY, CERTIFICATION_LEVEL, CERTIFICATION_LINK, CERTIFIED, RECENCY_OF_CERTIFICATION  
   - USER_SECONDARY_SKILLS → PRACTICE, PRACTICE_AREA, PRODUCTS_TECHNOLOGIES, CERTIFICATION_LEVEL, RECENCY_OF_CERTIFICATION  
4. For **skills/projects**, use:  
   - USER_SKILL + USER_SKILL_INFO (joined with PRACTICE, PRACTICE_AREA, PRACTICE_PRODUCT_TECHNOLOGY).  
5. For **high impact work/assets**, use HIGH_IMPACT_ASSETS (TITLE, DESCRIPTION, BUSINESS_IMPACT, VISIBILITY_ADOPTION).  
6. Always generate **valid DB2 SQL** using ANSI JOIN syntax.  
7. If multiple tables are relevant, UNION results with consistent column names.  
8. Always end the query with a semicolon.  
9. Return **only the SQL query**, with no natural language explanation. 
10. Only use columns that exist in the schema provided. 
11. If you use aggregate functions (COUNT, SUM, MAX, etc.), include all non-aggregated columns in a GROUP BY clause. 
12. Do not generate invalid columns or aliases. 
13. Prefer simple SELECT statements. 
14. Always return SQL that can run without syntax errors in Db2.

### STRICTLY USE THE ABOVE GIVEN INSTRUCTION ###

### Query to Generate:  
{natural_query}
"""
    try:
        response = getModel().chat([{"role": "user", "content": prompt}])
        sql = response["choices"][0]["message"]["content"].strip()
        return sql
    except Exception as e:
        print("Error generating SQL:", str(e))
        return None


# ✅ Example usage
if __name__ == "__main__":
    query = "Show me all users and their associated practice areas"
    sql_query = convert_to_sql(query)
    print("Generated SQL:\n", sql_query)
