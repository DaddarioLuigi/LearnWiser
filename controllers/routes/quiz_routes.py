from flask import Blueprint, render_template, request
from controllers.quiz_generator import QuizGenerator
import os
import json


quizGenerator = QuizGenerator()

quiz = Blueprint('quiz', __name__)

@quiz.route('/quiz', methods=['GET','POST'])
def insert_answer():
    
    response = quizGenerator.generateQuiz()
    response = json.loads(response)

    #put in the class
    domande = [domanda['domanda'] for domanda in response['domande']]

    # Extract answers
    risposte = [[risposta for risposta in domanda['risposte'].values()] for domanda in response['domande']]

    # Extract correct answers
    risposte_corrette = [domanda['corretta'] for domanda in response['domande']]

    # Output the lists
    print("Domande:", domande)
    print("Risposte:", risposte)
    print("Risposte corrette:", risposte_corrette)


    return render_template("quiz.html", domande=domande, risposte=risposte,  risposte_corrette=risposte_corrette)


