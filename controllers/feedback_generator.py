from config import llm 
from controllers.utils.pdf_parsing import pdf_to_txt
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, load_index_from_storage, StorageContext,get_response_synthesizer
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
import json
from controllers.routes.quiz_routes import quizGenerator
import os



class GenerateFeedback:
    #the fetch has to be automated
    def __init__(self, doc_path=r"C:\Users\Luigi Daddario\Desktop\webapp\user_doc", context=r"C:\Users\Luigi Daddario\Desktop\webapp\domande-risposte.json"):
        self.context=context
        self.path = doc_path


    def generateFeedback(self):
        

        print(self.context)
        with open("domande-risposte.json", "r") as file:
            # Read the contents of the file
            json_data = file.read()

            # Parse the JSON data into a Python object
            contesto = json.loads(json_data)

        domande = [domanda["domanda"] for domanda in contesto["domande"]]
        risposte_corrette = [domanda["corretta"] for domanda in contesto["domande"]]


        text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=10)

        # check if storage already exists
        PERSIST_DIR = "data"
        if not os.path.exists(PERSIST_DIR):
            print("xxx")
            # load the documents and create the index
            documents = SimpleDirectoryReader(self.path).load_data()
            index = VectorStoreIndex.from_documents (
                documents, transformations=[text_splitter]
            )
            # store it for later
            index.storage_context.persist(persist_dir=PERSIST_DIR)
        else:
            # load the existing index
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context)

        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=10
        )

        response_synthesizer = get_response_synthesizer()

        query_engine = RetrieverQueryEngine.from_args(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
            node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
            response_mode="no_text"
        )
        for i in range (len(domande)):
            nodes=query_engine.retrieve(domande[i]+risposte_corrette[i])

        return nodes

       
