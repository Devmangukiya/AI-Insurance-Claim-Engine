import json
import re
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

# ... your other imports ...
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

# --- 1. NEW, MORE ROBUST JSON EXTRACTOR ---
def extract_json_from_string(s: str) -> str:
    """Finds and extracts the first valid JSON object from a string, handling incomplete JSON."""
    # Find the first '{' and the last '}'
    start = s.find('{')
    end = s.rfind('}')
    if start != -1 and end != -1 and end > start:
        json_str = s[start:end+1]
        # Try to parse it to see if it's valid, if not, it's likely incomplete
        try:
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError:
            # If it fails, it's probably an incomplete JSON, return an empty object
            logger.warning("Incomplete JSON detected, returning empty object.")
            return "{}"
    return "{}" # Return empty JSON if no object is found

# Your PROMPT_PARSER remains the same...
PROMPT_PARSER = PromptTemplate(
    template="""...""", # Your existing parser prompt
    input_variables=["question"],
)

PROMPT_PARSER = PromptTemplate(
    template="""
### ROLE ###
You are an expert data extraction AI. Your task is to parse a user's query about an insurance claim and extract key entities into a structured JSON format.

### TASK ###
Analyze the user's query below. Identify the age, gender, medical procedure, location, and policy tenure. If a piece of information is not present, use a value of null. Your response MUST be only the JSON object, with no other text or explanation.

### USER QUERY TO PROCESS ###
{question}
""",
    input_variables=["question"],
)

# ## TEMPLATE 2: For Making the Final Decision ##
# This prompt takes the structured data and retrieved policy clauses to make a final, justified decision.
PROMPT_DECISION_MAKER = PromptTemplate(
    template="""
### ROLE ###
You are an expert Insurance Claims Adjudicator AI. Your task is to make a decision on a medical claim based on the claimant's details and the provided policy clauses.

### TASK ###
Analyze the Claimant Details and evaluate them against the Relevant Policy Clauses. You must determine if the claim is "Approved" or "Rejected" and provide a clear justification by mapping your reasoning directly to the provided clause numbers. Your response MUST be only a valid JSON object.

### CONTEXT ###

**Claimant Details (from parsed query):**
{claimant_details}

**Relevant Policy Clauses (retrieved from documents):**
{context}

### INSTRUCTIONS ###
1. Evaluate all Claimant Details against the Relevant Policy Clauses.
2. Synthesize your findings into a final "Approved" or "Rejected" decision.
3. If approved and an amount is specified in the clauses, state it.
4. Format your final answer ONLY as a JSON object as specified below.
5. Critically evaluate the claim. Prioritize and actively search the provided clauses for any rules regarding **waiting periods, exclusions, policy tenure, or specific conditions** that would lead to a rejection before making a final decision.

### OUTPUT FORMAT ###
{{
  "decision": "Approved" | "Rejected",
  "payout_amount": "number | null",
  "justification": [
    {{
      "reason": "A summary of the reason for the decision point.",
      "source_clause": "The exact clause number and text that supports this reason."
    }}
  ]
}}
""",
    input_variables=["claimant_details", "context"],
)


def run_adjudication_chain(query:str, llm, db):
    """
    Orchestrates the two-prompt chain to process a query and returns a decision.
    """
    try:
        # STEP 1: PARSE THE USER QUERY
        logger.info(f"Step 1: Parsing query: '{query}'")
        parser_chain = LLMChain(llm=llm, prompt=PROMPT_PARSER)
        parser_output = parser_chain.run(question=query)
        
        json_string = extract_json_from_string(parser_output)
        claimant_details_json = json.loads(json_string)
        logger.info(f"Successfully parsed details: {claimant_details_json}")

        # STEP 2: RETRIEVE RELEVANT CLAUSES (RAG)
        logger.info("Step 2: Retrieving relevant documents from vector store...")
        retriever = db.as_retriever(search_kwargs={"k": 10})
        retrieved_docs = retriever.get_relevant_documents(query)
        context_string = "\n\n".join([f"Clause Reference {i+1}: {doc.page_content}" for i, doc in enumerate(retrieved_docs)])
        logger.info("Document retrieval complete.")

        # STEP 3: MAKE THE FINAL DECISION
        logger.info("Step 3: Making final decision...")
        decision_chain = LLMChain(llm=llm, prompt=PROMPT_DECISION_MAKER)
        
        final_output_str = decision_chain.run(
            claimant_details=json.dumps(claimant_details_json, indent=2),
            context=context_string
        )

        json_string_final = extract_json_from_string(final_output_str)
        final_decision = json.loads(json_string_final)
        logger.info("Adjudication chain completed successfully.")
        
        return final_decision

    except json.JSONDecodeError as e:
        logger.error("--- FAILED TO PARSE JSON ---")
        parser_output_for_log = locals().get('parser_output', 'Not available')
        final_output_for_log = locals().get('final_output_str', 'Not available')
        
        logger.error(f"The AI returned this broken string: {parser_output_for_log or final_output_for_log}")
        logger.error(f"JSONDecodeError details: {e}")

        error_message = CustomException("Failed to parse JSON output from LLM.", e)
        logger.error(str(error_message))
        return {"error": "Failed to process the request due to invalid format from AI."}
    except Exception as e:
        error_message = CustomException("Failed to run adjudication chain.", e)
        logger.error(str(error_message))
        return {"error": "An unexpected error occurred."}