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

def clear_terminal():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

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


def test_metriche():
    test = get_qa_test_from_jsonl(test_5)
    
    recall_contextual,mmr_contextual,ndgc_contextual = calcolo_metriche_contextual(test)
    
    print("###############################")
    print("contexutal retrieval:")
    print(recall_contextual)
    print(mmr_contextual)
    print(ndgc_contextual)

def get_qa_test_from_jsonl(file_path):
    # Lista per memorizzare gli elementi
    lista_elementi = []

    # Lettura del file JSONL
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            elemento = json.loads(line)  # Converte la riga JSON in un dizionario
            lista_elementi.append(elemento)  # Aggiunge l'elemento alla lista
    
    return lista_elementi



test_1 = "codice_appalti_qa.jsonl"
test_2 = "ca_synth_mc.csv"
test_3 = "generated_output_mc.jsonl"
test_4 = "synth_qa_gpt_4o.jsonl"
test_5 = "synth_qa_claude_3_5_sonnet_20241022.jsonl"

clear_terminal()
db.MilvusConnectionManager.get_connection()

df_codice_appalti_allegati = pd.read_csv("codice_appalti_allegati.csv", encoding="utf-8", sep=",")
df_codice_appalti = pd.read_csv("data_appalti_v5.csv", encoding="utf-8", delimiter=",")
jsonl_contesti_domande_codice_appalti = get_qa_test_from_jsonl("legal_genie_cod_app.jsonl")


decreto_appalti_context = db.ContextCollection()
decreto_appalti_articoli = db.ArticoliCollection()
decreto_appalti_correttivo = db.CorrettivoCollection() 
decreto_appalti_context_correttivo = db.CorrettivoContextCollection()

collection_decreto_appalti_without_context_generation = decreto_appalti_articoli.get_collection("CodiceAppalti2023_Base","data_appalti_v5.csv")
collection_decreto_appalti_with_context_generation = decreto_appalti_context.get_collection("CodiceAppalti2023","generazione_contesti_v4.csv")
collection_decreto_appalti_correttivo = decreto_appalti_correttivo.get_collection("CorrettivoCodiceAppalti2024","codice_appalti_correttivo.csv")
collection_decreto_appalti_with_context_generation_correttivo = decreto_appalti_context_correttivo.get_collection("CodiceAppalti2023_Con_Correttivo","generazione_contesti_correttivi_v4.csv")
table_associtation_decreto_appalti_with_correttivo = db.create_association_table(collection_decreto_appalti_with_context_generation,collection_decreto_appalti_correttivo)

test_metriche()

# CLOSE CONNECTION WITH MILVUS DB
db.MilvusConnectionManager.close_connection()


