import chainlit as cl
from flask import current_app
import asyncio
from functools import partial

# Store Flask app instance
flask_app = None

def init_chainlit(app):
    global flask_app
    flask_app = app

@cl.on_chat_start
async def start():
    await cl.Message(content="Welcome to MCard Assistant! How can I help you today?").send()

@cl.on_message
async def main(message: str):
    # Here you can access Flask app context
    with flask_app.app_context():
        # Example of accessing Flask config or services
        # db = flask_app.db
        # You can perform Flask-specific operations here
        
        # For demonstration, we'll echo the message
        response = f"You said: {message}"
        await cl.Message(content=response).send()

# Function to run Chainlit server
def run_chainlit():
    import sys
    import os
    
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set up the command to run chainlit from the correct directory
    sys.argv = ["chainlit", "run", __file__, "-w"]
    os.chdir(current_dir)  # Change to the current directory
    cl.run()
