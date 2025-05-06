"""
This module provides context-aware retrieval functionality for legal documents.
It implements various methods for searching, retrieving, and evaluating
contextual information from legal articles stored in Milvus database collections.

Key components:
- Collection management functions for accessing legal document databases
- Search functions for finding and combining relevant articles
- Evaluation functions for testing retrieval accuracy
- Utility functions for text extraction and formatting

The module works with different types of legal documents, particularly focusing
on the Italian Public Procurement Code and its amendments.
"""

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
import pandas as pd
import numpy as np
from datasets import load_dataset
from pymilvus import connections, utility, Collection, CollectionSchema, FieldSchema, DataType
from transformers import AutoTokenizer, AutoModel
from argparse import Namespace
import torch
# Adjust import path for restructured project
import sys
sys.path.append('..')
from database import milvusDb as db
import logging
import csv
import os
import platform
import json
import random
import TestingFunction as tf

logging.basicConfig(
    format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO
)
logger = logging.getLogger(__name__)



# GENERAL FUNCTIONS

def extract_number(text):
    """Estrae il primo numero intero da una stringa."""
    match = re.search(r"\d+", text)  # Trova il primo numero nella stringa
    return int(match.group()) if match else None  # Ritorna il numero intero se esiste

def clear_terminal():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def print_results(titolo,risp_corrette,risp_errate,precisione):
    print(f"--- {titolo} ---")
    print(f"Risposte corrette: {risp_corrette}")
    print(f"Risposte sbagliate: {risp_errate}")
    print(f"Precisione: {precisione:.2f}%")
    print("################")

def format_articolo(articolo):

    if re.match(r"^[A-Z]+\d+$", articolo):  # Pattern che cerca lettere seguite da numeri
        return "ALLEGATO " + re.sub(r"([A-Z]+)(\d+)", r"\1.\2", articolo)  # Es: "I1" diventa "I.1"
    else:
        return articolo

def search_and_combine_articles(collection, articles, article_type="chunk"):
    combined_text = ""

    for articolo in articles:  
        if any(char.isalpha() for char in str(articolo)):
            number_articolo = format_articolo(str(articolo))
            matching_rows = df_codice_appalti_allegati[df_codice_appalti_allegati["Allegato"] == number_articolo]
            for _, row in matching_rows.iterrows():
                combined_text += row["contenuto"] + "\n"
        else:
            search_result = collection.query(expr=f"article == {articolo}", output_fields=[article_type])

            if search_result:
                for result in search_result:
                    combined_text += result[article_type] + "\n"  

    return combined_text

def is_numeric(article_number):
    return bool(re.match(r'^\d+$', article_number))

# GET COLLECTIONS

def get_decreto_appalti_articoli():
    return collection_decreto_appalti_without_context_generation

def get_decreto_appalti_context():
    return collection_decreto_appalti_with_context_generation

def get_decreto_appalti_correttivo():
    return collection_decreto_appalti_correttivo

def get_decreto_appalti_context_correttivo():
    return collection_decreto_appalti_with_context_generation_correttivo

def get_table_associations():
    return table_associtation_decreto_appalti_with_correttivo


### BASIC FUNCTION FOR DOWNLOAD COLLECTIONS AND TABLES

logging.basicConfig(
    format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO
)
logger = logging.getLogger(__name__)

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

# FUNZIONI TEST CORRETTIVO

def evaluate_dataset_correttivo_with_articles(dataset_test,articolo_correttivo = False, articolo_vecchio = False, contesto = False, context_retrieval = False):
    risposte_corrette = 0
    risposte_sbagliate = 0
    somma_retrieval_precision = 0
    num_domande = 0
    
    letter_to_value = {
        'a': 1, 'b': 2, 'c': 3, 'd': 4,
    }
    
    for test in dataset_test:
        
        correct_answer = test["multiple_choice"]["correct_answer"]
        wrong_answers = test["multiple_choice"]["wrong_answers"]
        old_article_number = test["old_article_number"]
        new_article_number = test["new_article_number"]

        old_article = search_and_combine_articles(collection_decreto_appalti_without_context_generation,[old_article_number],"chunk")
        new_article = search_and_combine_articles(collection_decreto_appalti_correttivo,[new_article_number],"Testo_Contenuto")
        
        contesto_generato_correttivo = ""
        
        contesto_generato_correttivo = tf.contesto_correttivo(old_article_number)

        options = wrong_answers + [correct_answer]
    
        contesto_articoli = ""
        
        if(contesto):
            contesto_articoli += contesto_generato_correttivo
        if(articolo_correttivo):
            contesto_articoli += new_article
        if(articolo_vecchio):
            contesto_articoli += old_article

        random.shuffle(options)
        correct_index = options.index(correct_answer)
        result,retrieval_precision = tf.evaluate_answers_with_correttivo_and_articoli(test['question'], options,contesto_articoli,int(old_article_number),collection_decreto_appalti_with_context_generation,context_retrieval)
        somma_retrieval_precision += retrieval_precision
        num_domande += 1
        
        try:
            result_int = extract_number(result.strip())

            if result_int is None:
                result = result.strip().lower()
                if len(result) == 1 and result in letter_to_value:
                    result_int = letter_to_value[result]
                else:
                    raise ValueError(f"Nessun numero valido trovato in '{result}' o risposta non valida.")

            correct_option_int = correct_index + 1

            if result_int == correct_option_int:
                risposte_corrette += 1
            else:
                risposte_sbagliate += 1

        except ValueError as e:
            print(f"Errore: {e}. La risposta corretta era {correct_answer}")
            risposte_sbagliate += 1

    # Calcola la precisione
    totale_risposte = risposte_corrette + risposte_sbagliate
    precisione = (risposte_corrette / totale_risposte) * 100 if totale_risposte > 0 else 0

    if context_retrieval:
        media_retrieval_precision = (somma_retrieval_precision / num_domande) if num_domande > 0 else 0
        print("##################")
        print(f"RETRIEVAL PRECISION MEAN: {media_retrieval_precision}")

    return risposte_corrette, risposte_sbagliate, precisione


def evaluate_dataset_context(dataset_test):
    risposte_corrette = 0
    risposte_sbagliate = 0

    letter_to_value = {
        'a': 1, 'b': 2, 'c': 3, 'd': 4,
    }

    for test in dataset_test:
        
        options = [test['correct_answer'], test['negative_option_1'], test['negative_option_2'], test['negative_option_3']]
        random.shuffle(options)
        correct_index = options.index(test['correct_answer'])        
        
        result,retrieval_precision = tf.evaluate_answers_codice_appalti_generated(test['question'], options,"",test["article_title"],collection_decreto_appalti_with_context_generation,True)
        # result = tf.evaluate_answers_codice_appalti_generated(test['question'], options,"",test["article_title"],collection_decreto_appalti_with_context_generation,True)
        try:
            result_int = extract_number(result.strip())

            if result_int is None:
                result = result.strip().lower()
                if len(result) == 1 and result in letter_to_value:
                    result_int = letter_to_value[result]
                else:
                    raise ValueError(f"Nessun numero valido trovato in '{result}' o risposta non valida.")

            correct_option_int = correct_index+1

            if result_int == correct_option_int:
                risposte_corrette += 1
            else:
                risposte_sbagliate += 1

        except ValueError as e:
            print(f"Errore: {e}. La risposta corretta era {test['correct_answer']}")
            risposte_sbagliate += 1

    totale_risposte = risposte_corrette + risposte_sbagliate
    precisione = (risposte_corrette / totale_risposte) * 100 if totale_risposte > 0 else 0

    return risposte_corrette, risposte_sbagliate, precisione

def evaluate_dataset_without_context(dataset_test):
    risposte_corrette = 0
    risposte_sbagliate = 0

    letter_to_value = {
        'a': 1, 'b': 2, 'c': 3, 'd': 4,
    }

    for test in dataset_test:
        
        options = [test['correct_answer'], test['negative_option_1'], test['negative_option_2'], test['negative_option_3']]
        random.shuffle(options)
        correct_index = options.index(test['correct_answer'])
        result = tf.generate_answer_without_context(test['question'], options)
        try:
            result_int = extract_number(result.strip())

            if result_int is None:
                result = result.strip().lower()
                if len(result) == 1 and result in letter_to_value:
                    result_int = letter_to_value[result]
                else:
                    raise ValueError(f"Nessun numero valido trovato in '{result}' o risposta non valida.")

            correct_option_int = correct_index+1

            if result_int == correct_option_int:
                risposte_corrette += 1
            else:
                risposte_sbagliate += 1

        except ValueError as e:
            print(f"Errore: {e}. La risposta corretta era {test['correct_answer']}")
            risposte_sbagliate += 1

    totale_risposte = risposte_corrette + risposte_sbagliate
    precisione = (risposte_corrette / totale_risposte) * 100 if totale_risposte > 0 else 0

    return risposte_corrette, risposte_sbagliate, precisione

def evaluate_dataset_correttivo_without_context(dataset_test):
    risposte_corrette = 0
    risposte_sbagliate = 0

    letter_to_value = {
        'a': 1, 'b': 2, 'c': 3, 'd': 4,
    }

    for test in dataset_test:
        
        correct_answer = test["multiple_choice"]["correct_answer"]
        wrong_answers = test["multiple_choice"]["wrong_answers"]

        options = wrong_answers + [correct_answer]

        random.shuffle(options)
        correct_index = options.index(correct_answer)
        
        # options = [test['correct_answer'], test['negative_option_1'], test['negative_option_2'], test['negative_option_3']]
        # random.shuffle(options)
        # correct_index = options.index(test['correct_answer'])
        result = tf.generate_answer_without_context(test['question'], options)
        try:
            result_int = extract_number(result.strip())

            if result_int is None:
                result = result.strip().lower()
                if len(result) == 1 and result in letter_to_value:
                    result_int = letter_to_value[result]
                else:
                    raise ValueError(f"Nessun numero valido trovato in '{result}' o risposta non valida.")

            correct_option_int = correct_index+1

            if result_int == correct_option_int:
                risposte_corrette += 1
            else:
                risposte_sbagliate += 1

        except ValueError as e:
            print(f"Errore: {e}. La risposta corretta era {correct_answer}")
            risposte_sbagliate += 1

    totale_risposte = risposte_corrette + risposte_sbagliate
    precisione = (risposte_corrette / totale_risposte) * 100 if totale_risposte > 0 else 0

    return risposte_corrette, risposte_sbagliate, precisione

# EXECUTE DATASET TEST

def test_question_answer_correttivo(file_path):
    
    if file_path.endswith(".csv"):
        test = get_mc_test_from_csv(file_path)
    elif file_path.endswith(".jsonl"):
        test = get_qa_test_from_jsonl(file_path)
    else:
        raise ValueError("Formato file non supportato. Solo .csv e .jsonl sono accettati.")
    
    test_filtrato = [t for t in test if is_numeric(t["old_article_number"]) and is_numeric(t["new_article_number"])]
    
    # corrette_correttivo_without_context, sbagliate_correttivo_without_context, precisione_correttivo_without_context = evaluate_dataset_correttivo_without_context(test)
    corrette_with_correttivo, sbagliate_with_correttivo, precisione_with_correttivo = evaluate_dataset_correttivo_with_articles(test_filtrato,True,False,False,False)
    
    # print_results("RISULTATI SOLO DOMANDE",corrette_correttivo_without_context,sbagliate_correttivo_without_context,precisione_correttivo_without_context)
    print_results("RISULTATI CON ARTICOLI VECCHI E CORRETTIVO",corrette_with_correttivo,sbagliate_with_correttivo,precisione_with_correttivo)


def test_question_answer_codice_appalti(file_path):
    if file_path.endswith(".csv"):
        test = get_mc_test_from_csv(file_path)
    elif file_path.endswith(".jsonl"):
        test = get_qa_test_from_jsonl(file_path)
    else:
        raise ValueError("Formato file non supportato. Solo .csv e .jsonl sono accettati.")
    
    test_filtrato = [t for t in test if is_numeric(t["old_article_number"]) and is_numeric(t["new_article_number"])]
    
    corrette_without_context, sbagliate_without_context, precisione_without_context = evaluate_dataset_without_context(test_filtrato)
    corrette, sbagliate, precisione = evaluate_dataset_context(test_filtrato)
    
    print_results("RISULTATI SOLO DOMANDE",corrette_without_context,sbagliate_without_context,precisione_without_context)
    print_results("RISULTATI CON CONTEXTUAL RETRIEVAL",corrette,sbagliate,precisione)


################## MAIN 

#DATASETS

df_codice_appalti_allegati = pd.read_csv("codice_appalti_allegati.csv", encoding="utf-8", sep=";")
df_codice_appalti = pd.read_csv("data_appalti_v5.csv", encoding="utf-8", delimiter=",")
jsonl_contesti_domande_codice_appalti = get_qa_test_from_jsonl("legal_genie_cod_app.jsonl")

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
Qwen_1_5 = "Qwen/Qwen2.5-1.5B-Instruct"
Qwen_0_5 = "Qwen/Qwen2.5-0.5B-Instruct"
Smol_1_7 = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
Smol_0_5 = "HuggingFaceTB/SmolLM2-360M-Instruct"
Saul = "Equall/Saul-7B-Instruct-v1"
Romulus = "louisbrulenaudet/Romulus-cpt-Llama-3.1-8B-v0.1-Instruct"

# DATASET TEST
test_1 = "codice_appalti_qa.jsonl"
test_2 = "ca_synth_mc.csv"
test_3 = "generated_output_mc.jsonl"

# LOAD MODELS FOR TESTING
# tf.load_models(granite)

# GET CONNECTION WITH MILVUS DB
clear_terminal()
db.MilvusConnectionManager.get_connection()
# CREATE OR LOAD COLLECTIONS
decreto_appalti_context = db.ContextCollection()
decreto_appalti_articoli = db.ArticoliCollection()
decreto_appalti_correttivo = db.CorrettivoCollection() 
decreto_appalti_context_correttivo = db.CorrettivoContextCollection()

collection_decreto_appalti_without_context_generation = decreto_appalti_articoli.get_collection("CodiceAppalti2023_Base","generazione_v1.csv")
collection_decreto_appalti_with_context_generation = decreto_appalti_context.get_collection("CodiceAppalti2023","generazione_v1.csv")
collection_decreto_appalti_correttivo = decreto_appalti_correttivo.get_collection("CorrettivoCodiceAppalti2024","codice_appalti_correttivo.csv")
collection_decreto_appalti_with_context_generation_correttivo = decreto_appalti_context_correttivo.get_collection("CodiceAppalti2023_Con_Correttivo","generation_with_correttivo.csv")
table_associtation_decreto_appalti_with_correttivo = db.create_association_table(collection_decreto_appalti_with_context_generation,collection_decreto_appalti_correttivo)

test_question_answer_correttivo(test_3)
# test_question_answer_codice_appalti(test_1)

# CLOSE CONNECTION WITH MILVUS DB
db.MilvusConnectionManager.close_connection()