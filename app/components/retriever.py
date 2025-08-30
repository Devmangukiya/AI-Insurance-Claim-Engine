import json
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

from app.components.llm import load_llm
from app.components.vector_store import load_vector_store
from app.config.config import GROQ_API_KEY, GROQ_MODEL_NAME
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

# ## TEMPLATE 1: For Parsing the User's Raw Query ##
# This prompt turns the natural language query into structured JSON data.
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

def run_adjudication_chain(query: str,llm,db):
    """
    Orchestrates the two-prompt chain to process a query and return a decision.
    
    Args:
        query: The raw natural language query from the user.

    Returns:
        A dictionary with the final decision.
    """
    try:
        # --- Load necessary components ---
        logger.info("Loading LLM and Vector Store...")
        llm = load_llm(model_name=GROQ_MODEL_NAME,groq_api_key=GROQ_API_KEY)
        db = load_vector_store()

        if llm is None or db is None:
            raise CustomException("Failed to load LLM or Vector Store.")

        # STEP 1: PARSE THE USER QUERY 
        logger.info(f"Step 1: Parsing query: '{query}'")
        parser_chain = LLMChain(llm=llm, prompt=PROMPT_PARSER)
        parser_output = parser_chain.run(question=query)

            
        print("\n" + "="*20 + " RAW PARSER OUTPUT " + "="*20)
        print(parser_output)
        print("="*59 + "\n")
        
        
        # Clean the string to remove markdown wrappers before parsing
        if "```" in parser_output:
            start_index = parser_output.find('{')
            end_index = parser_output.rfind('}') + 1
            json_string = parser_output[start_index:end_index]
        else:
            json_string = parser_output

        # parse the cleaned string
        claimant_details_json = json.loads(json_string)
        logger.info(f"Successfully parsed details: {claimant_details_json}")

        # STEP 2: RETRIEVE RELEVANT CLAUSES (RAG) 
        logger.info("Step 2: Retrieving relevant documents from vector store...")
        retriever = db.as_retriever(search_kwargs={"k": 10}) 
        
        # We use the original, context-rich query for the semantic search
        retrieved_docs = retriever.get_relevant_documents(query)
        
        # Format the retrieved documents into a single string for the next prompt
        context_string = "\n\n".join([f"Clause Reference {i+1}: {doc.page_content}" for i, doc in enumerate(retrieved_docs)])
        logger.info("Document retrieval complete.")

        # STEP 3: MAKE THE FINAL DECISION
        logger.info("Step 3: Making final decision...")
        decision_chain = LLMChain(llm=llm, prompt=PROMPT_DECISION_MAKER)
        
        final_output_str = decision_chain.run(
            claimant_details=json.dumps(claimant_details_json, indent=2),
            context=context_string
        )

        print("\n" + "="*20 + " RAW DECISION MAKER OUTPUT " + "="*20)
        print(final_output_str)
        print("="*65 + "\n")
        
        # Clean the string to remove markdown wrappers before parsing
        if "```" in final_output_str:
            start_index = final_output_str.find('{')
            end_index = final_output_str.rfind('}') + 1
            json_string_final = final_output_str[start_index:end_index]
        else:
            json_string_final = final_output_str

        # Parse the final cleaned JSON output string into a dictionary
        final_decision = json.loads(json_string_final)
        logger.info("Adjudication chain completed successfully.")
        
        return final_decision

    except json.JSONDecodeError as e:
        error_message = CustomException("Failed to parse JSON output from LLM.", e)
        logger.error(str(error_message))
        return {"error": "Failed to process the request due to invalid format from AI."}
    except Exception as e:
        error_message = CustomException("Failed to run adjudication chain.", e)
        logger.error(str(error_message))
        return {"error": "An unexpected error occurred."}