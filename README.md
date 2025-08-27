# 🤖 AI-Powered Engine for Insurance Policy Claims 🤖
An intelligent system built for a hackathon that uses Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) to process natural language insurance queries, retrieve information from unstructured policy documents, and make automated, auditable decisions.

# 🚀 Key Features
  - Natural Language Understanding: Parses complex, informal user queries (e.g., "46M, knee surgery, Pune, 3-month policy") into a structured format.

  - Semantic Document Search: Utilizes a vector database (FAISS) and sentence-transformer embeddings to find the most relevant clauses from a large corpus of unstructured policy documents (PDFs, etc.).

  - Intelligent Decision Making: Employs a two-step LLM chain to first parse the query and then reason over the retrieved clauses to make a final, justified decision.

  - Understands Key Insurance Logic: The system is designed to interpret and apply critical insurance concepts like waiting periods, specific procedure exclusions, and coverage limits.

  - Auditable Responses: Every decision (Approved/Rejected) is returned in a structured JSON format, complete with justifications that cite the exact source clauses from the documents.

  - Web Interface: A simple and intuitive web interface built with Flask for easy interaction and demonstration.

# 🔑 Key Insurance Terms Handled
This system is specifically designed to understand and reason with the following core insurance concepts found in policy documents:

  - Waiting Period: The duration a policyholder must wait after the policy's inception before certain coverages become effective. The AI checks the policy tenure against these rules (e.g., a 24-month wait for cataract surgery).

  - Exclusions: Specific conditions, procedures, or circumstances that are not covered by the policy. The AI actively looks for these clauses to prevent incorrect approvals.

  - Covered Procedures: A list of medical treatments and surgeries that are eligible for a claim. The system matches the user's query against this list.

  - Deductible: The amount the insured must pay out-of-pocket before the insurer pays a claim. While not calculating the final payout, the AI can identify if a deductible applies.

  - Co-payment: A fixed amount the insured pays for a covered health care service. The AI can identify clauses mentioning co-payment responsibilities.

# ⚙️ How It Works (Architecture)
This project uses a sophisticated two-prompt RAG chain to ensure both accuracy and consistency.

1. Query Parsing:

  - The user's raw query is first sent to an LLM chain specifically prompted to act as a data extractor.

  - It identifies key entities (age, procedure, location, policy tenure) and converts the query into a structured JSON object.

2. Semantic Retrieval (RAG):

  - The original query is used to perform a semantic search against a pre-computed FAISS vector store containing embeddings of the policy documents.

  - The system retrieves the top k most relevant document chunks (clauses) to form a context for the decision-making step.

3. Decision Making:

  - A second, more powerful LLM chain is prompted to act as an "Insurance Claims Adjudicator."

  - It receives the structured JSON from Step 1 and the retrieved clauses from Step 2.

  - It critically evaluates the evidence, checking for waiting periods, exclusions, and coverage, before making a final decision and generating a detailed justification.

# 🛠️ Tech Stack
- Backend: Python, Flask

- AI Framework: LangChain

- LLM: OpenAI (gpt-3.5-turbo)

- Embeddings: Hugging Face sentence-transformers/all-MiniLM-L6-v2

- Vector Store: FAISS (Facebook AI Similarity Search)

- Document Loading: PyMuPDF for PDFs

- Environment Management: python-dotenv

# 📦 Setup and Installation
Follow these steps to get the application running locally.

1. Prerequisites
  - Python 3.10+
  - An OpenAI API Key

2. Clone the Repository
  - git clone https://github.com/Devmangukiya/AI-Insurance-Claim-Engine.git
  - cd AI-Insurance-Claim-Engine


3. Set Up a Virtual Environment
# For Windows
  - python -m venv venvai
  - venv\Scripts\activate

# For macOS/Linux
  - python3 -m venv venv
  - source venv/bin/activate


4. Install Dependencies
pip install -r requirements.txt


5. Set Up Environment Variables
Create a file named .env in the root of the project and add your OpenAI API key



6. Ingest Your Data
Before running the app, you must process your policy documents and create the vector store. Place all your PDF documents in a designated folder (e.g., data/).

Then, run the ingestion script (you may need to create this script if you haven't already).

python data_loader.py


This will create a faiss_index folder in your project directory.

7. Run the Application
python application.py


# 🚀 Usage
1. Navigate to http://127.0.0.1:5000 in your web browser.

2. Enter a query in the text box. Be as specific or as vague as you like.

3. Example 1: 42-year-old man, cataract surgery in Mumbai, policy is 3 years old

4. Example 2: my wife needs knee surgery in pune, we got the policy 2 months ago

5. Click "Evaluate Claim" to receive the AI-generated decision and justification.