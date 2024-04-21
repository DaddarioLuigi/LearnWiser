from flask import Flask
import os
import sys
import os.path
import openai
from llama_index.core import Settings
from openai import OpenAI

#openai keys:
os.environ["OPENAI_API_KEY"]=''
openai.api_key = os.environ["OPENAI_API_KEY"]

#modify temperature
llm = OpenAI()

def create_app():

    #Inizializziamo un oggetto di tipo Flask
    app = Flask(__name__,template_folder='views')

    #import routes
    from controllers.routes.insert_routes import insert
    from controllers.routes.quiz_routes import quiz
    from controllers.routes.feedback_routes import feedback


   #import blueprints
    app.register_blueprint(insert, url_prefix="/")
    app.register_blueprint(quiz, url_prefix="/")
    app.register_blueprint(feedback, url_prefix="/")


    return app