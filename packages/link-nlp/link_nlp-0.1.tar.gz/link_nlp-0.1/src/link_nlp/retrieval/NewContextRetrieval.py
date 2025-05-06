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
import TestingFunction as tf

logging.basicConfig(
    format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO
)
logger = logging.getLogger(__name__)

letter_to_value = {
    'a': 1, 'b': 2, 'c': 3, 'd': 4,
}









#######################################################################################################

# GENERAL FUNCTIONS

def average_test_results(test_func, test, iterations=10):
    """Esegue più test e calcola la media dei risultati."""
    correct_totals = 0
    wrong_totals = 0
    precision_totals = 0.0

    for _ in range(iterations):
        correct, wrong, precision = test_func(test)
        correct_totals += correct
        wrong_totals += wrong
        precision_totals += precision

    # Calcola la media
    avg_correct = correct_totals / iterations
    avg_wrong = wrong_totals / iterations
    avg_precision = precision_totals / iterations

    return avg_correct, avg_wrong, avg_precision


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
    
def cast_article_number(article):
    if pd.isna(article):
        return None
    
    # Verifica se è un numero intero
    if str(article).isdigit():
        return int(article)
    
    # Se è una stringa del tipo "I2", "II4", ecc.
    match = re.match(r"([A-Za-z]+)(\d+)", str(article))
    if match:
        letters = match.group(1).upper()  # Parte alfabetica in maiuscolo
        number = match.group(2)           # Parte numerica
        return f"ALLEGATO {letters}.{number}"
    
    # Se non corrisponde a nessun formato previsto, ritorna la stringa originale
    return str(article)


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

#######################################################################################################

# FUNZIONI TEST



def zero_shot_test_generated_output_mc(dataset_test):
    risposte_corrette = 0
    risposte_sbagliate = 0

    for test in dataset_test:
        
        correct_answer = test["multiple_choice"]["correct_answer"]
        wrong_answers = test["multiple_choice"]["wrong_answers"]

        options = wrong_answers + [correct_answer]

        random.shuffle(options)
        correct_index = options.index(correct_answer)

        result = tf.zero_shot_generation(test['question'], options)
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

def contextual_retrieval_test_generated_output_mc(dataset_test):
    risposte_corrette = 0
    risposte_sbagliate = 0
    
    for test in dataset_test:
        
        correct_answer = test["multiple_choice"]["correct_answer"]
        wrong_answers = test["multiple_choice"]["wrong_answers"]
        old_article_number = test["old_article_number"]

        article_number = cast_article_number(old_article_number)
    
        options = wrong_answers + [correct_answer]

        random.shuffle(options)
        correct_index = options.index(correct_answer)
        result = tf.contextual_retrieval_general(test['question'], options,collection_decreto_appalti_with_context_generation_correttivo,article_number)
        
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

    return risposte_corrette, risposte_sbagliate, precisione

def header_test_generated_output_mc(dataset_test):
    
    risposte_corrette = 0
    risposte_sbagliate = 0
    
    for test in dataset_test:
        
        correct_answer = test["multiple_choice"]["correct_answer"]
        wrong_answers = test["multiple_choice"]["wrong_answers"]
        old_article_number = test["old_article_number"]
        article_number = cast_article_number(old_article_number)
        options = wrong_answers + [correct_answer]

        random.shuffle(options)
        correct_index = options.index(correct_answer)
        result = tf.header_general(test['question'], options,collection_decreto_appalti_with_context_generation_correttivo,article_number)
        
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

    return risposte_corrette, risposte_sbagliate, precisione

def standard_retrieval_test_generated_output_mc(dataset_test):
    risposte_corrette = 0
    risposte_sbagliate = 0
    
    for test in dataset_test:
        
        correct_answer = test["multiple_choice"]["correct_answer"]
        wrong_answers = test["multiple_choice"]["wrong_answers"]
        old_article_number = test["old_article_number"]
        new_article_number = test["new_article_number"]

        options = wrong_answers + [correct_answer]
        old_article_number_formatted = cast_article_number(old_article_number)
        new_article_number_formatted = cast_article_number(new_article_number)
        random.shuffle(options)
        correct_index = options.index(correct_answer)
        result = tf.standard_retrieval_correttivo(test['question'], options,collection_decreto_appalti_without_context_generation,collection_decreto_appalti_correttivo,old_article_number_formatted,new_article_number_formatted)
        
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

    return risposte_corrette, risposte_sbagliate, precisione


def zero_shot_test_synth_qa_gpt_4o(dataset_test):
    risposte_corrette = 0
    risposte_sbagliate = 0

    for test in dataset_test:
        
        question = test["question"]
        options = test["options"]
        correct_answer = int(test["correct_answer"])

        result = tf.zero_shot_generation(question, options)
        try:
            result_int = extract_number(result.strip())

            if result_int is None:
                result = result.strip().lower()
                if len(result) == 1 and result in letter_to_value:
                    result_int = letter_to_value[result]
                else:
                    raise ValueError(f"Nessun numero valido trovato in '{result}' o risposta non valida.")

            correct_option_int = correct_answer+1

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

def contextual_retrieval_test_synth_qa_gpt_4o(dataset_test):
    risposte_corrette = 0
    risposte_sbagliate = 0
    
    for test in dataset_test:
        
        article = test["article"]
        question = test["question"]
        options = test["options"]
        correct_answer = int(test["correct_answer"])
    
        result = tf.contextual_retrieval_general(question, options,collection_decreto_appalti_with_context_generation,article)
        
        try:
            result_int = extract_number(result.strip())

            if result_int is None:
                result = result.strip().lower()
                if len(result) == 1 and result in letter_to_value:
                    result_int = letter_to_value[result]
                else:
                    raise ValueError(f"Nessun numero valido trovato in '{result}' o risposta non valida.")

            correct_option_int = correct_answer + 1

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

    return risposte_corrette, risposte_sbagliate, precisione

def header_test_synth_qa_gpt_4o(dataset_test):
    
    risposte_corrette = 0
    risposte_sbagliate = 0
    
    for test in dataset_test:
        
        article = test["article"]
        question = test["question"]
        options = test["options"]
        correct_answer = int(test["correct_answer"])

        result = tf.header_general(question, options,collection_decreto_appalti_with_context_generation_correttivo,article)
        
        try:
            result_int = extract_number(result.strip())

            if result_int is None:
                result = result.strip().lower()
                if len(result) == 1 and result in letter_to_value:
                    result_int = letter_to_value[result]
                else:
                    raise ValueError(f"Nessun numero valido trovato in '{result}' o risposta non valida.")

            correct_option_int = correct_answer + 1

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

    return risposte_corrette, risposte_sbagliate, precisione

def standard_retrieval_test_synth_qa_gpt_4o(dataset_test):
    risposte_corrette = 0
    risposte_sbagliate = 0
    
    for test in dataset_test:
        
        article = test["article"]
        question = test["question"]
        options = test["options"]
        correct_answer = int(test["correct_answer"])
        
        result = tf.standard_retrieval_general(question, options,collection_decreto_appalti_without_context_generation,article)
        
        try:
            result_int = extract_number(result.strip())

            if result_int is None:
                result = result.strip().lower()
                if len(result) == 1 and result in letter_to_value:
                    result_int = letter_to_value[result]
                else:
                    raise ValueError(f"Nessun numero valido trovato in '{result}' o risposta non valida.")

            correct_option_int = correct_answer + 1

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

    return risposte_corrette, risposte_sbagliate, precisione


########################################################################

# TEST

def test_generated_output_mc():
    
    test = get_qa_test_from_jsonl(test_3)
    iterations = 1
        
    # Zero-shot test
    zero_corrette, zero_sbagliate, zero_precisione = average_test_results(zero_shot_test_generated_output_mc, test, iterations)

    # Contextual retrieval test
    contextual_corrette, contextual_sbagliate, contextual_precisione = average_test_results(contextual_retrieval_test_generated_output_mc, test, iterations)

    # Header test
    header_corrette, header_sbagliate, header_precisione = average_test_results(header_test_generated_output_mc, test, iterations)

    # Standard retrieval test
    standard_corrette, standard_sbagliate, standard_precisione = average_test_results(standard_retrieval_test_generated_output_mc, test, iterations)

    # PRINT RISULTATI
    
    print_results("ZERO SHOT TEST:",zero_corrette,zero_sbagliate,zero_precisione)
    print_results("CONTEXTUAL RETRIEVAL TEST:",contextual_corrette,contextual_sbagliate,contextual_precisione)
    print_results("HEADER TEST:",header_corrette,header_sbagliate,header_precisione)
    print_results("STANDARD RETRIEVAL TEST:",standard_corrette,standard_sbagliate,standard_precisione)


def test_synth_qa_gpt_4o():
    test = get_qa_test_from_jsonl(test_5)
    iterations = 1
    
        # Zero-shot test
    zero_corrette, zero_sbagliate, zero_precisione = average_test_results(zero_shot_test_synth_qa_gpt_4o, test, iterations)

    # Contextual retrieval test
    contextual_corrette, contextual_sbagliate, contextual_precisione = average_test_results(contextual_retrieval_test_synth_qa_gpt_4o, test, iterations)

    # Header test
    header_corrette, header_sbagliate, header_precisione = average_test_results(header_test_synth_qa_gpt_4o, test, iterations)

    # Standard retrieval test
    standard_corrette, standard_sbagliate, standard_precisione = average_test_results(standard_retrieval_test_synth_qa_gpt_4o, test, iterations)
    
    
    print_results("ZERO SHOT TEST:",zero_corrette,zero_sbagliate,zero_precisione)
    print_results("CONTEXTUAL RETRIEVAL TEST:",contextual_corrette,contextual_sbagliate,contextual_precisione)
    print_results("HEADER TEST:",header_corrette,header_sbagliate,header_precisione)
    print_results("STANDARD RETRIEVAL TEST:",standard_corrette,standard_sbagliate,standard_precisione)

def calcolo_metriche_contextual(dataset_test):
    
    media_recall = [0,0,0,0,0,0]
    media_mmr = [0,0,0,0,0,0]
    media_ndgc = [0,0,0,0,0,0]
    
    finale_recall = [0,0,0,0,0,0]
    finale_mmr = [0,0,0,0,0,0]
    finale_ndgc = [0,0,0,0,0,0]
    
    k = [0,1,2,3,4,5]
    elementi = len(dataset_test)
    
    for test in dataset_test:
        
        article = int(test["article"])
        question = test["question"]
        options = test["options"]
    
        recall,ndgc,mrr = tf.contextual_retrieval_general(question, options,collection_decreto_appalti_with_context_generation,article)
        
        for i in k:
            media_recall[i] = media_recall[i]+recall[i]
            media_ndgc[i] = media_ndgc[i]+ndgc[i]
            # Avoid division by zero
            if recall[i] > 0:
                media_mmr[i] = media_mmr[i] + (1/recall[i])
            else:
                media_mmr[i] = media_mmr[i]  # Keep the current value
            
    for i in k:
        finale_recall[i] = media_recall[i]/elementi
        finale_mmr[i] = media_mmr[i]/elementi
        finale_ndgc[i] = media_ndgc[i]/elementi

    mrr_definitiva = 0  # Inizializza mrr

    for el in recall:
        mrr += float(1) / float(el)

    mrr /= len(recall) 

    return finale_recall, mrr_definitiva, finale_ndgc

def calcolo_metriche_header(dataset_test):
    
    media_recall = [0,0,0,0,0,0]
    media_mmr = [0,0,0,0,0,0]
    media_ndgc = [0,0,0,0,0,0]
    
    finale_recall = [0,0,0,0,0,0]
    finale_mmr = [0,0,0,0,0,0]
    finale_ndgc = [0,0,0,0,0,0]
    
    k = [0,1,2,3,4,5]
    elementi = len(dataset_test)
    
    for test in dataset_test:
        
        article = test["article"]
        question = test["question"]
        options = test["options"]

        recall,ndgc,mrr = tf.header_general(question, options,collection_decreto_appalti_with_context_generation_correttivo,article)
        
        for i in k:
            media_recall[i] = media_recall[i]+recall[i]
            media_ndgc[i] = media_ndgc[i]+ndgc[i]
            # Avoid division by zero
            if recall[i] > 0:
                media_mmr[i] = media_mmr[i] + (1/recall[i])
            else:
                media_mmr[i] = media_mmr[i]  # Keep the current value

    for i in k:
        finale_recall[i] = media_recall[i]/elementi
        finale_mmr[i] = media_mmr[i]/elementi
        finale_ndgc[i] = media_ndgc[i]/elementi

    mrr_definitiva = 0
    for el in recall: mrr += 1/el
    mrr /= len(recall)

    return finale_recall, mrr_definitiva, finale_ndgc

def calcolo_metriche_standard(dataset_test):
    
    media_recall = [0,0,0,0,0,0]
    media_mmr = [0,0,0,0,0,0]
    media_ndgc = [0,0,0,0,0,0]
    
    finale_recall = [0,0,0,0,0,0]
    finale_mmr = [0,0,0,0,0,0]
    finale_ndgc = [0,0,0,0,0,0]
    
    k = [0,1,2,3,4,5]
    elementi = len(dataset_test)
    
    for test in dataset_test:
        
        article = test["article"]
        question = test["question"]
        options = test["options"]
        
        recall,ndgc,mrr = tf.standard_retrieval_general(question, options,collection_decreto_appalti_without_context_generation,article)
        
        for i in k:
            media_recall[i] = media_recall[i]+recall[i]
            media_ndgc[i] = media_ndgc[i]+ndgc[i]
            # Avoid division by zero
            if recall[i] > 0:
                media_mmr[i] = media_mmr[i] + (1/recall[i])
            else:
                media_mmr[i] = media_mmr[i]  # Keep the current value
        
    for i in k:
        finale_recall[i] = media_recall[i]/elementi
        finale_mmr[i] = media_mmr[i]/elementi
        finale_ndgc[i] = media_ndgc[i]/elementi
      
    return finale_recall, finale_mmr, finale_ndgc




def test_metriche():
    test = get_qa_test_from_jsonl(test_5)
    
    recall_contextual,mmr_contextual,ndgc_contextual = calcolo_metriche_contextual(test)
    # recall_header,mmr_header,ndgc_header = calcolo_metriche_header(test)
    # recall_standard,mmr_standard,ndgc_standard = calcolo_metriche_standard(test)
    
    print("###############################")
    print("contexutal retrieval:")
    print(recall_contextual)
    print(mmr_contextual)
    print(ndgc_contextual)
    # print("###############################")
    # print("header:")
    # print(recall_header)
    # print(mmr_header)
    # print(ndgc_header)
    # print("###############################")
    # print("standard retrieval:")
    # print(recall_standard)
    # print(mmr_standard)
    # print(ndgc_standard)

##########################################################################

#DATASETS

df_codice_appalti_allegati = pd.read_csv("codice_appalti_allegati.csv", encoding="utf-8", sep=",")
df_codice_appalti = pd.read_csv("data_appalti_v5.csv", encoding="utf-8", delimiter=",")
jsonl_contesti_domande_codice_appalti = get_qa_test_from_jsonl("legal_genie_cod_app.jsonl")

# MODELS

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
test_4 = "synth_qa_gpt_4o.jsonl"
test_5 = "synth_qa_claude_3_5_sonnet_20241022.jsonl"
# LOAD MODELS FOR TESTING

# tf.load_models(Smol_1_7)

# GET CONNECTION WITH MILVUS DB

clear_terminal()
db.MilvusConnectionManager.get_connection()

db.drop_collection_by_name("CodiceAppalti2023")

# CREATE OR LOAD COLLECTIONS
decreto_appalti_context = db.ContextCollection()
decreto_appalti_articoli = db.ArticoliCollection()
decreto_appalti_correttivo = db.CorrettivoCollection() 
decreto_appalti_context_correttivo = db.CorrettivoContextCollection()

collection_decreto_appalti_without_context_generation = decreto_appalti_articoli.get_collection("CodiceAppalti2023_Base","data_appalti_v5.csv")
collection_decreto_appalti_with_context_generation = decreto_appalti_context.get_collection("CodiceAppalti2023","generazione_contesti_v4.csv")
collection_decreto_appalti_correttivo = decreto_appalti_correttivo.get_collection("CorrettivoCodiceAppalti2024","codice_appalti_correttivo.csv")
collection_decreto_appalti_with_context_generation_correttivo = decreto_appalti_context_correttivo.get_collection("CodiceAppalti2023_Con_Correttivo","generazione_contesti_correttivi_v4.csv")
table_associtation_decreto_appalti_with_correttivo = db.create_association_table(collection_decreto_appalti_with_context_generation,collection_decreto_appalti_correttivo)

# ESEGUI TEST

# test_generated_output_mc()

# test_synth_qa_gpt_4o()

test_metriche()

# CLOSE CONNECTION WITH MILVUS DB
db.MilvusConnectionManager.close_connection()


