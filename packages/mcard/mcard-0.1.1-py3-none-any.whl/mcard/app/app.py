from flask import Flask, render_template, jsonify
from mcard.model.card_collection import CardCollection
from mcard.engine.sqlite_engine import SQLiteConnection, SQLiteEngine
from mcard.config.env_parameters import EnvParameters
from mcard.config.config_constants import DEFAULT_PAGE_SIZE
from flask_cors import CORS

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept"],
        "expose_headers": ["Content-Type"]
    }
})

# Load environment parameters
env_params = EnvParameters()
db_path = env_params.MCARD_DB_PATH
page_size = DEFAULT_PAGE_SIZE
print(f"Database path: {db_path}")
connection = SQLiteConnection(db_path)
engine = SQLiteEngine(connection)
card_collection = CardCollection(engine)

@app.route("/")
def index():
    """Render the home page with all cards"""
    initial_cards = card_collection.get_all_cards(page_number=1, page_size=page_size).items
    return render_template("index.html", initial_cards=initial_cards, page_size=page_size)

@app.route("/api/data")
def get_data():
    # Example API route for React to fetch data
    return jsonify({"message": "Hello from Flask!"})

def main():
    """
    Entry point for the application when installed via pip.
    This function is referenced in setup.py's entry_points.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="MCard: Memory Card with TDD approach")
    parser.add_argument("--host", default="127.0.0.1", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the server on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    print(f"Starting MCard server on {args.host}:{args.port}")
    print(f"Database path: {db_path}")
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()
