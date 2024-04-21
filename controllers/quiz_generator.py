from config import llm 
from controllers.utils.pdf_parsing import pdf_to_txt
import json


class QuizGenerator:
    #the fetch has to be automated
    def __init__(self, doc_path=r"C:\Users\Luigi Daddario\Desktop\webapp\user_doc\medioevo.pdf"):
        self.content=None
        self.path = doc_path
    


    def generateQuiz(self):
    # to be implemented with LLAMA index
        text = pdf_to_txt(self.path)

        quiz = llm.chat.completions.create(
            messages=[
                {'role': 'system', 'content': 'Sei un tutor che aiuta le persone nello studio, specializzato nei quiz.'},
                {'role': 'user',     'role': 'user','content': f'''A partire da questo documento "{text}" restituisci un JSON con 5 
                  domande e per ogni domanda 4 risposte possibili di cui solo una corretta
                  seguendo il seguente schema: {{
                      'domande': {{
                          'domanda': 'string',
                          'risposte': {{
                              'risposta1': 'string',
                              'risposta2': 'string',
                              'risposta3': 'string',
                              'risposta4': 'string'
                          }},
                          'corretta': 'string'
                      }}
                  }}'''}
            ],
            model="gpt-3.5-turbo-0125",
            response_format={"type": "json_object"}
        )

        #print(quiz.choices[0].message.content)

        self.content=json.loads(quiz.choices[0].message.content)
        print(self.content)
        # Serialize the JSON variable to a string
        json_string = json.dumps(self.content)  # Optionally, specify the indentation for pretty formatting

        # Open a file in write mode and write the JSON string to it
        with open("domande-risposte.json", "w") as file:
            file.write(json_string)

        #retun content
        return quiz.choices[0].message.content

       
