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
                api_key="6gq4j-xBSYD1Oi0RUz-4ZXqO8BpIEGL9eFZe7irI7PbQ",
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
2. When the request involves **certifications, credentials, or skills**, check across **all relevant tables**:  
   - PROFESSIONAL_CERTIFICATIONS → professional certifications (TITLE, CERTIFICATION_LEVEL).  
   - USER_CREDENTIALS → digital credentials (CREDENTIAL_LABEL, CREDENTIAL_TYPE, CREDENTIAL_STATUS).  
   - USER_ANCILLARY_SKILLS → additional certifications/skills (PRODUCT, TECHNOLOGY, CERTIFICATION_LEVEL).  
   - USER_SECONDARY_SKILLS → secondary skills and certifications (PRACTICE, PRACTICE_AREA, PRODUCTS_TECHNOLOGIES).  
3. If the query involves **skills/projects**, use:  
   - USER_SKILL and USER_SKILL_INFO (joined with PRACTICE, PRACTICE_AREA, PRACTICE_PRODUCT_TECHNOLOGY for details).  
4. If the query involves **high impact work/assets**, use HIGH_IMPACT_ASSETS.  
5. Always generate a **valid DB2 SQL query** with proper JOINs between USERS and the relevant tables.  
6. If multiple tables are relevant, UNION results with consistent column names.  
7. Return **only the SQL query**, no explanations and ending with semicolon.  
8. Always generate queries only using columns that exist in the schema provided.
If a requested field is not present, do not guess column names. Instead, map the intent to the most relevant existing column.
---

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
