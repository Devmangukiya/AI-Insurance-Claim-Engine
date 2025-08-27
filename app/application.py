from flask import Flask, render_template, request, session, redirect, url_for
from markupsafe import Markup
from dotenv import load_dotenv
import os
from app.components.retriever import run_adjudication_chain
from app.components.llm import load_llm
from app.components.vector_store import load_vector_store

from app.components.retriever import run_adjudication_chain

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# load model Globally (This happens only once at startup)
print("Loading models into memory, please wait...")
try:
    llm_model = load_llm()
    vector_store_db = load_vector_store()
    print("Models loaded successfully!")
except Exception as e:
    print(f"Failed to load models on startup: {e}")
    llm_model = None
    vector_store_db = None


# This filter helps render newlines and other HTML from the response string correctly
@app.template_filter('nl2br')
def nl2br_filter(s):
    return Markup(s.replace('\n', '<br>'))  


def format_response_for_display(response_dict: dict) -> str:
    """Formats the JSON decision into a clean, flat structure for the chat interface."""
    if not isinstance(response_dict, dict):
        return "Error: Received an invalid response format."

    if "error" in response_dict:
        return f"An error occurred: {response_dict['error']}"

    try:
        decision = response_dict.get('decision', 'N/A')
        payout = response_dict.get('payout_amount', 'Not Applicable')
        justification_list = response_dict.get('justification', [])

        result_str = f"<b>Decision :-</b> {decision}<br>"
        result_str += f"<b>Payout Amount :-</b> {payout}<br><br>"

        if justification_list:
            result_str += "<b>Justification Details :-</b><br>"

        # Loop through the justification items and number them
        for i, item in enumerate(justification_list):
            reason = item.get('reason', 'No reason given.')
            source = item.get('source_clause', 'No source clause specified.')

            # Format with numbered labels for each reason and source
            result_str += f"<b>Reason {i+1} :-</b> {reason}<br>"
            result_str += f"<b>Source {i+1} :-</b> {source}<br><br>" 

        return result_str.strip()

    except Exception as e:
        return f"Error: Could not parse the response dictionary. Details: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def index():
    if "messages" not in session:
        session["messages"] = []

    if request.method == "POST":
        user_input = request.form.get("prompt")

        if user_input:
            messages = session["messages"]
            messages.append({"role": "user", "content": user_input})
            session["messages"] = messages

            try:
               
                # Directly call the new chain function with the user's query
                response_dict = run_adjudication_chain(user_input,llm=llm_model,db=vector_store_db)

                # Format the structured dictionary response into a display string
                result = format_response_for_display(response_dict)

                messages.append({"role": "assistant", "content": result})
                session["messages"] = messages

            except Exception as e:
                # Catch any unexpected errors during the chain execution
                error_msg = f"A critical application error occurred: {str(e)}"
                messages.append({"role": "assistant", "content": error_msg})
                session["messages"] = messages
            
        return redirect(url_for("index"))
    
    return render_template("index.html", messages=session.get("messages", []))


@app.route("/clear")
def clear():
    session.pop("messages", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)