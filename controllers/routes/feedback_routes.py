from flask import Blueprint, render_template, request
from controllers.feedback_generator import GenerateFeedback
from llama_index.core.response.notebook_utils import display_source_node
import os
import json

feedback_generator=GenerateFeedback()

feedback = Blueprint('feedback', __name__)

@feedback.route('/feedback')
def getFeedback():
    nodes=feedback_generator.generateFeedback()

    list_feedback=['Hai sbagliato.La risposta corretta si trova a pagina '+nodes[0].text+'il testo rilevante è il seguete'+nodes[0].metadata['page_label']]#per question
    return render_template("feedback.html", list_feedback=list_feedback)