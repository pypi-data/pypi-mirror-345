import pickle
import requests
import time
import re
import gc
import os
import pathlib
import requests
import torch
import regex
import pandas                               as pd
import numpy                                as np
from datasets                               import load_dataset
from pymilvus import connections, utility, Collection, CollectionSchema, FieldSchema, DataType
from transformers import AutoTokenizer, AutoModel
import pandas as pd
import numpy as np
from argparse import Namespace
import torch
import milvusDb as db
import logging
import csv
import os
import platform
import json
import random 
import MilvusDbAlternative as dba
# GENERAL FUNCTIONS

df_codice_appalti_allegati = pd.read_csv("codice_appalti_allegati.csv", encoding="utf-8", sep=";")


def load_codice_appalti():
    global df_codice_appalti
    df_codice_appalti = pd.read_csv("data_appalti_v2.csv", encoding="utf-8", delimiter=",")


def extract_number(text):
    """Estrae il primo numero intero da una stringa."""
    match = re.search(r"\d+", text)  # Trova il primo numero nella stringa
    return int(match.group()) if match else None  # Ritorna il numero intero se esiste

def clear_terminal():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

logging.basicConfig(
    format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO
)
logger = logging.getLogger(__name__)


# DOWNLOAD COLLECTIONS

def getDbCollectionBase(data_path,collection_name):
    
    args = Namespace(
            csv_path=data_path,
            collection_name=collection_name
        )

    collection = db.create_or_download_db_collection_base(args)
    if(collection is None):
        print("collezione non creata.")
        return None
    return collection

def getDbCollection(data_path,collection_name):

    args = Namespace(
            csv_path=data_path,
            collection_name=collection_name
        )

    collection = db.create_or_download_db_collection(args)
    if(collection is None):
        print("collezione non creata.")
        return None
    return collection

def getDbCollection_correttivo(data_path,collection_name):
    args = Namespace(
            csv_path=data_path,
            collection_name=collection_name
        )

    collection = db.create_or_download_db_collection_correttivo(args)
    if(collection is None):
        print("collezione non creata.")
        return None
    return collection


# DOWNLOAD DATASET TEST

def get_mc_test_from_csv(csv_path):
    # Leggi il file CSV come una lista di dizionari
    with open(csv_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = [row for row in reader]  # Ogni riga è un dizionario
    return rows

def get_qa_test_from_jsonl(file_path):
    # Lista per memorizzare gli elementi
    lista_elementi = []

    # Lettura del file JSONL
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            elemento = json.loads(line)  # Converte la riga JSON in un dizionario
            lista_elementi.append(elemento)  # Aggiunge l'elemento alla lista
    return lista_elementi


def format_articolo(articolo):
    # Se l'articolo contiene una lettera seguita da un numero (esempio: "I1", "II2", etc.)
    if re.match(r"^[A-Z]+\d+$", articolo):  # Pattern che cerca lettere seguite da numeri
        # Aggiungi il punto dopo la lettera
        return "ALLEGATO " + re.sub(r"([A-Z]+)(\d+)", r"\1.\2", articolo)  # Es: "I1" diventa "I.1"
    else:
        # Non toccare gli articoli che non corrispondono al formato lettera-numero
        return articolo

# GET RESULTS FOR DATASET TEST
def search_and_combine_articles(collection, articles, article_type="chunk"):
    combined_text = ""  # Variabile per accumulare il testo

    for articolo in articles:  # Assicurati che `articles` sia una lista
        # Usa l'articolo come un intero (senza convertirlo in stringa)
        if any(char.isalpha() for char in str(articolo)):
            number_articolo = format_articolo(str(articolo))
            matching_rows = df_codice_appalti_allegati[df_codice_appalti_allegati["Allegato"] == number_articolo]
            for _, row in matching_rows.iterrows():
                combined_text += row["contenuto"] + "\n"
        else:
            search_result = collection.query(expr=f"article == {articolo}", output_fields=[article_type])

            # Aggiungi il testo trovato alla stringa combinata
            if search_result:
                for result in search_result:
                    combined_text += result[article_type] + "\n"  # Aggiungi il risultato alla stringa
    
    # print("ARTICOLO CITATO: "+articles[0])
    # print("CONTENUTO: \n"+combined_text)

    return combined_text

def evaluate_dataset_with_correttivo_qa_alternative(qa_test, collection,collection_correttivo,table_association):
    risposte_corrette = 0
    risposte_sbagliate = 0
    
    letter_to_value = {
        'a': 1, 'b': 2, 'c': 3, 'd': 4,
    }
    


    for test in qa_test:
        
        correct_answer = test["multiple_choice"]["correct_answer"]
        wrong_answers = test["multiple_choice"]["wrong_answers"]
        old_article_number = test["old_article_number"]
        new_article_number = test["new_article_number"]

        old_article = search_and_combine_articles(collection_decreto_appalti_without_context_generation,[old_article_number],"chunk")
        new_article = search_and_combine_articles(collection_decreto_appalti_correttivo,[new_article_number],"Testo_Contenuto")
        
        contesto_generato_correttivo = db.contesto_correttivo(old_article_number)
        # Crea una lista combinata di risposte corrette e sbagliate
        options = wrong_answers + [correct_answer]
    
        contesto_articoli =old_article + "\n" + new_article

        # Mischia le risposte
        random.shuffle(options)
        correct_index = options.index(correct_answer)
        result = db.evaluate_answers_with_correttivo_qa_alternative(test['question'], options, collection,collection_correttivo,contesto_articoli)
        try:
            # Estrai il numero dalla risposta
            result_int = extract_number(result.strip())

            # Se non c'è un numero valido, controlla che la stringa sia lunga 1 carattere
            if result_int is None:
                result = result.strip().lower()  # Converti a minuscolo
                if len(result) == 1 and result in letter_to_value:
                    result_int = letter_to_value[result]
                else:
                    raise ValueError(f"Nessun numero valido trovato in '{result}' o risposta non valida.")

            correct_option_int = correct_index + 1  # Converte la risposta corretta

            # Verifica se la risposta è corretta
            if result_int == correct_option_int:
                risposte_corrette += 1
            else:
                risposte_sbagliate += 1

        except ValueError as e:
            # Se la conversione fallisce (testo o altro carattere), segna come sbagliata
            print(f"Errore: {e}. La risposta corretta era {correct_answer}")
            risposte_sbagliate += 1

    # Calcola la precisione
    totale_risposte = risposte_corrette + risposte_sbagliate
    precisione = (risposte_corrette / totale_risposte) * 100 if totale_risposte > 0 else 0

    return risposte_corrette, risposte_sbagliate, precisione

def evaluate_dataset_qa_alternative(qa_test,collection,context):
    risposte_corrette = 0
    risposte_sbagliate = 0

    letter_to_value = {
        'a': 1, 'b': 2, 'c': 3, 'd': 4,
    }

    for test in qa_test:
        options = [test['correct_answer'], test['negative_option_1'], test['negative_option_2'], test['negative_option_3']]
        random.shuffle(options)
        correct_index = options.index(test['correct_answer'])
        result = db.contextualRetrieval_qa_alternative(test['question'], options, collection,str(test["article_title"]),context)
        try:
            # Estrai il numero dalla risposta
            result_int = extract_number(result.strip())

            # Se non c'è un numero valido, controlla che la stringa sia lunga 1 carattere
            if result_int is None:
                result = result.strip().lower()  # Converti a minuscolo
                if len(result) == 1 and result in letter_to_value:
                    result_int = letter_to_value[result]
                else:
                    raise ValueError(f"Nessun numero valido trovato in '{result}' o risposta non valida.")

            correct_option_int = correct_index+1  # Converte la risposta corretta

            # Verifica se la risposta è corretta
            if result_int == correct_option_int:
                risposte_corrette += 1
            else:
                risposte_sbagliate += 1

        except ValueError as e:
            # Se la conversione fallisce (testo o altro carattere), segna come sbagliata
            print(f"Errore: {e}. La risposta corretta era {test['correct_answer']}")
            risposte_sbagliate += 1

    # Calcola la precisione
    totale_risposte = risposte_corrette + risposte_sbagliate
    precisione = (risposte_corrette / totale_risposte) * 100 if totale_risposte > 0 else 0

    return risposte_corrette, risposte_sbagliate, precisione

def evaluate_dataset_qa_alternative_void(qa_test):
    risposte_corrette = 0
    risposte_sbagliate = 0

    letter_to_value = {
        'a': 1, 'b': 2, 'c': 3, 'd': 4,
    }

    for test in qa_test:
        
        correct_answer = test["multiple_choice"]["correct_answer"]
        wrong_answers = test["multiple_choice"]["wrong_answers"]
        # Crea una lista combinata di risposte corrette e sbagliate
        options = wrong_answers + [correct_answer]

        # Mischia le risposte
        random.shuffle(options)
        correct_index = options.index(correct_answer)
        
        # options = [test['correct_answer'], test['negative_option_1'], test['negative_option_2'], test['negative_option_3']]
        # random.shuffle(options)
        # correct_index = options.index(test['correct_answer'])
        result = db.generate_answer_qa_only_question_alternative(test['question'], options)
        try:
            # Estrai il numero dalla risposta
            result_int = extract_number(result.strip())

            # Se non c'è un numero valido, controlla che la stringa sia lunga 1 carattere
            if result_int is None:
                result = result.strip().lower()  # Converti a minuscolo
                if len(result) == 1 and result in letter_to_value:
                    result_int = letter_to_value[result]
                else:
                    raise ValueError(f"Nessun numero valido trovato in '{result}' o risposta non valida.")

            correct_option_int = correct_index+1  # Converte la risposta corretta

            # Verifica se la risposta è corretta
            if result_int == correct_option_int:
                risposte_corrette += 1
            else:
                risposte_sbagliate += 1

        except ValueError as e:
            # Se la conversione fallisce (testo o altro carattere), segna come sbagliata
            print(f"Errore: {e}. La risposta corretta era {test['correct_answer']}")
            risposte_sbagliate += 1

    # Calcola la precisione
    totale_risposte = risposte_corrette + risposte_sbagliate
    precisione = (risposte_corrette / totale_risposte) * 100 if totale_risposte > 0 else 0

    return risposte_corrette, risposte_sbagliate, precisione


# EXECUTE DATASET TEST

def test_question_answer_alternative():
    qa_test = get_qa_test_from_jsonl(mc_macro_test_2)
    qa_test_10 = qa_test[:10]
    corrette_only, sbagliate_only, precisione_only = evaluate_dataset_qa_alternative_void(qa_test)
    # corrette_con_articolo, sbagliate_con_articolo, precisione_con_articolo = evaluate_dataset_qa_alternative(qa_test, collection_decreto_appalti_with_context_generation,False)
    # corrette_con_articolo_contesto,sbagliate_con_articolo_contesto,precisione_con_articolo_contesto = evaluate_dataset_qa_alternative(qa_test, collection_decreto_appalti_with_context_generation,True)
    corrette_con_articolo_e_correttivo, sbagliate_con_articolo_e_correttivo, precisione_con_articolo_e_correttivo = evaluate_dataset_with_correttivo_qa_alternative(qa_test,collection_decreto_appalti_with_context_generation,collection_decreto_appalti_correttivo,table_associtation_decreto_appalti_with_correttivo)
    
    # Stampa i risultati
    print("--- RISULTATI SOLO DOMANDA E RISPOSTE ---")
    print(f"Risposte corrette: {corrette_only}")
    print(f"Risposte sbagliate: {sbagliate_only}")
    print(f"Precisione: {precisione_only:.2f}%")
    print("################")
    # print("--- RISULTATI CON ARTICOLO CORRETTO ---")
    # print(f"Risposte corrette: {corrette_con_articolo}")
    # print(f"Risposte sbagliate: {sbagliate_con_articolo}")
    # print(f"Precisione: {precisione_con_articolo:.2f}%")
    # print("################")
    # print("--- RISULTATI CON ARTICOLO CORRETTO E CONTESTO ---")
    # print(f"Risposte corrette: {corrette_con_articolo_contesto}")
    # print(f"Risposte sbagliate: {sbagliate_con_articolo_contesto}")
    # print(f"Precisione: {precisione_con_articolo_contesto:.2f}%")
    print("--- RISULTATI CORRETTIVO ---")
    print(f"Risposte corrette: {corrette_con_articolo_e_correttivo}")
    print(f"Risposte sbagliate: {sbagliate_con_articolo_e_correttivo}")
    print(f"Precisione: {precisione_con_articolo_e_correttivo:.2f}%")
    
    
################## MAIN 


# MODELS
phi4 = "phi-4-Q4_K_M.gguf"
phi4tokenizer = "microsoft/phi-4"
mistral_v03 = "mistralai/Mistral-7B-Instruct-v0.3"
mistral_v01 = "mistralai/Mistral-7B-Instruct-v0.1"
phi3_5 = "microsoft/Phi-3.5-mini-instruct"
llama3 = "meta-llama/Meta-Llama-3-8B-instruct"
llama3_1 = "meta-llama/Meta-Llama-3.1-8B-Instruct"
llama3_2 = "meta-llama/Llama-3.2-1B-Instruct"

google_gemma = "google/gemma-2-2b-it"
granite = "ibm-granite/granite-3.1-2b-instruct"
Qwen1_5 = "Qwen/Qwen2.5-1.5B-Instruct"
Qwen_0_5 = "Qwen/Qwen2.5-0.5B-Instruct"
Smol1_7 = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
Smol_0_5 = "HuggingFaceTB/SmolLM2-360M-Instruct"
Saul = "Equall/Saul-7B-Instruct-v1"
Romulus = "louisbrulenaudet/Romulus-cpt-Llama-3.1-8B-v0.1-Instruct"

# DATASET TEST
qa_macro_test_1 = "codice_appalti_qa.jsonl"
mc_macro_test_1 = "ca_synth_mc.csv"
mc_macro_test_2 = "generated_output_mc.jsonl"

# GET CONNECTION WITH MILVUS DB
db.MilvusConnectionManager.get_connection()
# LOAD MODELS FOR TESTING
db.load_models(google_gemma)

clear_terminal()

# CREATE OR LOAD COLLECTIONS
collection_decreto_appalti_without_context_generation = getDbCollectionBase("generazione_v1.csv","CodiceAppalti2023_Base")
collection_decreto_appalti_with_context_generation = getDbCollection("generazione_v1.csv","CodiceAppalti2023")
collection_decreto_appalti_correttivo = getDbCollection_correttivo("codice_appalti_correttivo.csv","CorrettivoCodiceAppalti2024")
table_associtation_decreto_appalti_with_correttivo = db.get_association_table(collection_decreto_appalti_with_context_generation,collection_decreto_appalti_correttivo)

#test_multiple_choice()

test_question_answer_alternative()

# CLOSE CONNECTION WITH MILVUS DB
db.MilvusConnectionManager.close_connection()