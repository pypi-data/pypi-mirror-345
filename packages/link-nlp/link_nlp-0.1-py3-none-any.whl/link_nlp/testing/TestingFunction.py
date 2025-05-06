from pymilvus import connections, utility, Collection, CollectionSchema, FieldSchema, DataType
from transformers import AutoTokenizer, AutoModel,AutoModelForCausalLM,pipeline
from langchain.llms import HuggingFacePipeline
from vllm import LLM, SamplingParams
from milvus import default_server
import pandas as pd
import numpy as np
import logging
import argparse
import torch
import re
import milvusDb as mv
from sklearn.metrics import ndcg_score

j=0

logging.basicConfig(
    format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO
)

logger = logging.getLogger(__name__)

df_codice_appalti_allegati = pd.read_csv("codice_appalti_allegati.csv", encoding="utf-8", sep=",")
df_codice_appalti = pd.read_csv("data_appalti_v5.csv",encoding="utf-8", sep=",")
df_generazioni_codice_appalti = pd.read_csv("generazione_v1.csv",encoding="utf-8", sep=",")
df_generazioni_codice_appalti_correttivo = pd.read_csv("generation_with_correttivo.csv",encoding="utf-8", sep=",")
MAX_TOTAL_TOKENS = 4000
RESERVED_TOKENS = 600 

# FUNZIONI PRINCIPALI

def load_models(model_name,tokenizerName = None):
    
    global llm_model,tokenizer, llm_sampling_params

    logger.info("Caricamento del modello di generazione...")

    # Inizializza il modello e il tokenizer

    tokenizer = AutoTokenizer.from_pretrained( tokenizerName or model_name)
    tokenizer.eos_token = "<|endoftext|>" 
    tokenizer.eos_token_id = tokenizer.convert_tokens_to_ids(tokenizer.eos_token)

    # Parametri di campionamento
    llm_sampling_params = SamplingParams(
        temperature=0.8, 
        max_tokens=64,
        top_k=10,
        top_p=0.95,
    )

    llm_model = LLM(model=model_name,tokenizer= tokenizerName or model_name)

    logger.info("Caricamento completato")
    
def truncate_context_to_fit(context, question, options, articles, max_tokens=MAX_TOTAL_TOKENS):
    """Tronca il contesto e gli articoli per rientrare nel limite totale di token."""
    
    # Tokenizza DOMANDA + RISPOSTE (fisso)
    prompt_base = f"Domanda: {question}\n"
    for i, option in enumerate(options, 1):
        prompt_base += f"Opzione {i}: {option}\n"
    prompt_base += "Qual è la risposta corretta? Rispondi solo con il numero della risposta corretta.\n\n"

    prompt_tokens = tokenizer.encode(prompt_base, add_special_tokens=False)
    
    # Tokenizza CONTESTO + ARTICOLI
    context_tokens = tokenizer.encode(context, add_special_tokens=False)
    articles_tokens = tokenizer.encode(articles, add_special_tokens=False)
    
    # Calcola lo spazio disponibile per CONTESTO + ARTICOLI
    max_context_articles_tokens = max_tokens - len(prompt_tokens)
    
    # Se il totale è troppo lungo, tronchiamo PRIMA gli ARTICOLI
    total_tokens = len(context_tokens) + len(articles_tokens)
    
    if total_tokens > max_context_articles_tokens:
        # Spazio disponibile per gli articoli
        max_articles_tokens = max_context_articles_tokens // 3  # Riserviamo circa 1/3 agli articoli
        max_context_tokens = max_context_articles_tokens - max_articles_tokens  # Il resto per il contesto
        
        # Tronca prima gli articoli
        if len(articles_tokens) > max_articles_tokens:
            articles_tokens = articles_tokens[:max_articles_tokens]
        
        # Tronca poi il contesto se ancora necessario
        if len(context_tokens) > max_context_tokens:
            context_tokens = context_tokens[:max_context_tokens]

    # Decodifica i testi troncati
    truncated_context = tokenizer.decode(context_tokens)
    truncated_articles = tokenizer.decode(articles_tokens)

    # Costruisci il prompt finale
    final_prompt = f"CONTESTO:\n{truncated_context}\n\nARTICOLI:\n{truncated_articles}\n\n{prompt_base}"
    
    return final_prompt


def retrieveContext(question, collection, top_k=3):
    question_embedding = mv.embed_texts(question)
    search_params = {"metric_type": "IP", "params": {"nprobe": 10}}

    results = collection.search(question_embedding, "embedding", search_params, top_k, output_fields=["chunk", "article","allegato"])

    return [(hit.entity.get("chunk"), hit.entity.get("article"),hit.entity.get("allegato")) for hit in results[0]]

def retrieveContextCorrettivo(question, collection, top_k=3):
    question_embedding = mv.embed_texts(question)
    search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
    results = collection.search(question_embedding, "embedding", search_params, top_k, output_fields=["Testo_Contenuto", "article"])
    return [(hit.entity.get("Testo_Contenuto"), hit.entity.get("article")) for hit in results[0]]



def retrieveContext_with_context_generated(question, collection, top_k=3):
    question_embedding = mv.embed_texts(question)
    search_params = {"metric_type": "IP", "params": {"nprobe": 10}}

    # Aggiungi "context_generated" all'elenco dei campi da estrarre
    results = collection.search(question_embedding, "embedding", search_params, top_k, output_fields=["chunk", "article","context_generated","allegato"])

    # Ritorna una lista di tuple con chunk, articolo e context_generated
    return [(hit.entity.get("chunk"), hit.entity.get("article"),hit.entity.get("context_generated"),hit.entity.get("allegato")) for hit in results[0]]


def retrieveArticle(title):
    results = []
    
    allegato_match = re.search(r'ALLEGATO\s([IVXLCDM\.\d]+)', title, re.IGNORECASE)
    articoli_match = re.findall(r'Art(?:icolo|\.)\s(\d+)', title)
    
    articoli_match = list(set(map(str, articoli_match)))
    if allegato_match:
        allegato = f"ALLEGATO {allegato_match.group(1)}"
        allegato_match = {allegato}
    
    if allegato_match:
        
        df_filtered = df_codice_appalti_allegati[df_codice_appalti_allegati['Allegato'] == allegato]
        df_filtered = df_filtered.sort_values(by=['Articolo'])
        
        if not df_filtered.empty:
            results.append("\n".join(df_filtered['contenuto'].astype(str)))
    contesti_totali = []
    if articoli_match:
        for articolo in articoli_match:
            df_filtered = df_codice_appalti[df_codice_appalti['Articolo'] == articolo]
            df_filtered = df_filtered.sort_values(by=['Comma'])
            
            if not df_filtered.empty:
                results.append("\n".join(df_filtered['Testo_Contenuto'].astype(str)))
            
            contesti_filtrati = df_generazioni_codice_appalti[
                        df_generazioni_codice_appalti["article"].astype(str) == str(articolo)
                    ]["context_generated"].dropna().tolist()
            contesti_totali.extend(contesti_filtrati)
            
    testo_unico = " ".join(contesti_totali)
    return "\n".join(filter(None, testo_unico)),"\n".join(filter(None, results))

def extractArticleNumbers(title):
    articoli_list = []  # Lista per i numeri degli articoli
    allegati_list = []  # Lista per le stringhe degli allegati
    
    # Estrazione di "ALLEGATO" (supporta numeri romani e decimali)
    allegato_match = re.search(r'ALLEGATO\s([IVXLCDM\.\d]+)', title, re.IGNORECASE)
    
    if allegato_match:
        allegato = f"ALLEGATO {allegato_match.group(1).replace('.', '')}"  # Rimuove i punti se ci sono (es. "I.2" diventa "I2")
        allegati_list.append(allegato)
    
    # Estrazione degli articoli (ad esempio "Art. 15", "Art. 8")
    articoli_match = re.findall(r'Art(?:icolo|\.)\s(\d+)', title)
    
    if articoli_match:
        articoli_list = [int(articolo) for articolo in set(articoli_match)]  # Rimuove i duplicati e converte a int
    
    return articoli_list, allegati_list


def format_article_number(article_number):
    # Verifica se il numero contiene lettere
    letters = ''.join([char for char in article_number if char.isalpha()])  # Estrai le lettere
    digits = ''.join([char for char in article_number if char.isdigit()])    # Estrai le cifre
    
    # Formatta come "ALLEGATO LETTERE.CIFRE"
    if letters and digits:
        return f"ALLEGATO {letters}.{digits}"
    else:
        return article_number


def calculate_metrics(retrieved_contexts, target_article, k_list):
    recall_at_k_list = []
    ndcg_at_k_list = []
    mrr = 0
    
    target_field_index = 1
    target_article = int(target_article)
    # # Determine target field index
    # if len(retrieved_contexts[0]) == 4:
    #     if isinstance(target_article, str):
    #         target_field_index = 3  
    #     else:
    #         target_field_index = 1
    # else:
    #     if isinstance(target_article, str):
    #         target_field_index = 2  
    #     else:
    #         target_field_index = 1 

    # Create binary relevance array
    print(target_article)
    for context in retrieved_contexts:
        print(context[target_field_index])
        print(context[target_field_index] == target_article)
    
    relevance = np.array([1 if  int(context[target_field_index]) == target_article else 0 
                          for context in retrieved_contexts])
    
    # Calculate MRR
    first_relevant_idx = np.argmax(relevance) if np.any(relevance) else -1
    if first_relevant_idx != -1:
        mrr = 1.0 / (first_relevant_idx + 1)
    else:
        mrr = 0
    
    # Calculate metrics for each k
    for k in k_list:
        # Recall@K
        if np.sum(relevance) > 0:
            recall_at_k = np.sum(relevance[:k]) / np.sum(relevance)
        else:
            recall_at_k = 0.0
        
        # NDCG@K using scikit-learn
        if k <= len(relevance):
            # For ndcg_score, we need a 2D array for both y_true and y_score
            # y_true contains relevance scores, y_score contains the ranking scores (descending order is better)
            y_true = relevance.reshape(1, -1)
            y_score = np.array([len(relevance) - i for i in range(len(relevance))]).reshape(1, -1)
            ndcg_k = ndcg_score(y_true, y_score, k=k)
        else:
            ndcg_k = ndcg_score(np.array([relevance]), np.array([[len(relevance) - i for i in range(len(relevance))]]), k=min(k, len(relevance)))
        
        recall_at_k_list.append(recall_at_k)
        ndcg_at_k_list.append(ndcg_k)

    return recall_at_k_list, ndcg_at_k_list, mrr

def contextual_retrieval_general(question, options, collection, article, save_metrics=True):
    retrieved_contexts = retrieveContext_with_context_generated(question, collection, 50)
    k = [1, 3, 5, 10, 20, 50]
    recall, ndcg, mrr = calculate_metrics(retrieved_contexts, article, k)
    
    if save_metrics:
        save_retrieval_statistics(recall, ndcg, mrr, k, "contextual_retrieval_statistics.txt")
    
    return recall, ndcg, mrr

def standard_retrieval_general(question, options, collection_appalti, article_appalti, save_metrics=True):
    retrieved_contexts_appalti = retrieveContext(question, collection_appalti, 50)
    k = [1, 3, 5, 10, 20, 50]
    recall, ndcg, mrr = calculate_metrics(retrieved_contexts_appalti, article_appalti, k)
    return recall, ndcg, mrr

def save_retrieval_statistics(recall_at_k, ndcg_at_k, mrr, k_list, filename="retrieval_statistics.txt"):
    global j
    with open(filename, "a") as file:
        file.write(f"DOMANDA {j}: \n")
        file.write(f"    Recall@K ({k_list}): {recall_at_k}\n")
        file.write(f"    MRR: {mrr}\n")
        file.write(f"    NDCG@K ({k_list}): {ndcg_at_k}\n")
        file.write("\n")
    j = j + 1


def contesto_allegati(allegato):
    nome_allegato = format_article_number(allegato)
    
    # Filtra le righe che corrispondono al nome allegato
    filtered_rows = df_generazioni_codice_appalti[df_generazioni_codice_appalti['allegato'] == nome_allegato]
    
    # Combina il contenuto della colonna "context_generated" in un'unica stringa
    contesto_unico = ' '.join(filtered_rows['context_generated'].astype(str))
    
    return contesto_unico
    

def contesto_correttivo(article):
    df_generazioni_codice_appalti_correttivo["article"] = df_generazioni_codice_appalti_correttivo["article"].astype(str)

    df_filtrato = df_generazioni_codice_appalti_correttivo[df_generazioni_codice_appalti_correttivo["article"] == article]
    combined_text = " ".join(df_filtrato["context_generated"].astype(str))

    return combined_text

def calculate_precision_at_k(results, target_article, k):
    relevant_items = sum(1 for _, article_number in results[:k] if article_number == target_article)
    return relevant_items / k if k > 0 else 0.0

def calculate_context_precision_at_k(results, target_article, k):
    """
    Calcola la Context Precision@K per un singolo articolo (target_article).
    
    Parameters:
    - results: I risultati della ricerca (contenenti i chunk e i numeri degli articoli).
    - target_article: Un singolo articolo target.
    - k: Il valore di k per cui calcolare la precisione.
    
    Returns:
    - precision_at_k: La precisione per il valore di k.
    """
    relevant_items = sum(1 for _, article_number in results[:k] if article_number == target_article)
    
    if relevant_items == 0:
        return 0.0

    sum_precision_relevance = 0.0
    for i in range(1, k + 1):
        _, article_number = results[i - 1]
        relevance_at_k = 1 if article_number == target_article else 0
        precision_at_k = calculate_precision_at_k(results, target_article, i)
        sum_precision_relevance += precision_at_k * relevance_at_k

    return sum_precision_relevance / relevant_items

def retrieve_and_filter_chunk(target_articles, retrieved_contexts):
    """
    Filtra i chunk pertinenti a più articoli target e unisce tutti i chunk pertinenti per ciascun articolo.
    
    Parameters:
    - target_articles: Lista di articoli target.
    - retrieved_contexts: Lista di tuple (chunk, article) con i risultati recuperati.
    
    Returns:
    - final_context: Una stringa contenente tutti i chunk pertinenti per i vari articoli.
    """
    chosen_contexts = []

    # Step 1: Filtra i chunk pertinenti per ciascun articolo in target_articles
    for target_article in target_articles:
        relevant_contexts = [chunk for chunk, article,_ in retrieved_contexts if article == target_article]

        # Step 2: Aggiungi tutti i chunk pertinenti per l'articolo
        if relevant_contexts:
            chosen_contexts.extend(relevant_contexts)  # Aggiungi tutti i chunk pertinenti per l'articolo
        else:
            # Step 3: Fallback: Se non ci sono chunk pertinenti, prendi i primi 3 risultati
            chosen_contexts.extend([chunk for chunk, _,_ in retrieved_contexts[:3]])

    # Step 4: Se chosen_contexts è vuoto, prendi il primo retrieved context
    if not chosen_contexts and retrieved_contexts:
        first_chunk, _,_ = retrieved_contexts[0]  # Prendi il primo elemento
        chosen_contexts.append(first_chunk)

    # Step 5: Unisci i chunk in un unico contesto (stringa)
    final_context = " ".join(chosen_contexts)

    return final_context


def retrieve_and_filter_correttivo(target_articles, retrieved_contexts):
    """
    Filtra i chunk pertinenti a più articoli target e unisce tutti i chunk pertinenti per ciascun articolo.
    
    Parameters:
    - target_articles: Lista di articoli target.
    - retrieved_contexts: Lista di tuple (chunk, article) con i risultati recuperati.
    
    Returns:
    - final_context: Una stringa contenente tutti i chunk pertinenti per i vari articoli.
    """
    chosen_contexts = []

    # Step 1: Filtra i chunk pertinenti per ciascun articolo in target_articles
    for target_article in target_articles:
        relevant_contexts = [Testo_Contenuto for Testo_Contenuto, article in retrieved_contexts if article == target_article]

        # Step 2: Aggiungi tutti i chunk pertinenti per l'articolo
        if relevant_contexts:
            chosen_contexts.extend(relevant_contexts)  # Aggiungi tutti i chunk pertinenti per l'articolo
        else:
            # Step 3: Fallback: Se non ci sono chunk pertinenti, prendi i primi 3 risultati
            chosen_contexts.extend([Testo_Contenuto for Testo_Contenuto, _ in retrieved_contexts[:3]])

    # Step 4: Se chosen_contexts è vuoto, prendi il primo retrieved context
    if not chosen_contexts and retrieved_contexts:
        first_Testo_Contenuto, _ = retrieved_contexts[0]  # Prendi il primo elemento
        chosen_contexts.append(first_Testo_Contenuto)

    # Step 5: Unisci i chunk in un unico contesto (stringa)
    final_context = " ".join(chosen_contexts)

    return final_context


def retrieve_and_filter_with_chunk_and_context_generated(target_articles, retrieved_contexts):
    """
    Filtra i chunk pertinenti a più articoli target e unisce tutti i chunk pertinenti per ciascun articolo.
    
    Parameters:
    - target_articles: Lista di articoli target.
    - retrieved_contexts: Lista di tuple (chunk, article, context_generated) con i risultati recuperati.
    
    Returns:
    - final_context: Una stringa contenente tutti i chunk pertinenti per i vari articoli.
    """
    chosen_contexts = []

    # Step 1: Filtra i chunk pertinenti per ciascun articolo in target_articles
    for target_article in target_articles:
        relevant_contexts = [
            chunk + " " + context_generated  # Concatenazione di chunk e context_generated
            for chunk, article, context_generated,_ in retrieved_contexts if article == target_article
        ]

    #     # Step 2: Aggiungi tutti i chunk pertinenti per l'articolo
        if relevant_contexts:
            chosen_contexts.extend(relevant_contexts)  # Aggiungi tutti i chunk pertinenti per l'articolo
        else:
            # Step 3: Fallback: Se non ci sono chunk pertinenti, prendi i primi 3 risultati
            chosen_contexts.extend([chunk+"\n"+context_generated for chunk, _, context_generated,_ in retrieved_contexts[:3]])
    
    chosen_contexts.extend([chunk+"\n"+context_generated for chunk, _, context_generated,_ in retrieved_contexts[:3]])

    # Step 4: Unisci i chunk in un unico contesto (stringa)
    final_context = " ".join(chosen_contexts)

    return final_context

def retrieve_and_filter_chunk_and_context_generated(target_articles, retrieved_contexts):
    """
    Filtra i chunk pertinenti a più articoli target e unisce tutti i chunk pertinenti per ciascun articolo.
    
    Parameters:
    - target_articles: Lista di articoli target.
    - retrieved_contexts: Lista di tuple (chunk, article, context_generated) con i risultati recuperati.
    
    Returns:
    - final_context: Una stringa contenente tutti i chunk pertinenti per i vari articoli.
    """
    chosen_contexts = []

    # Step 1: Filtra i chunk pertinenti per ciascun articolo in target_articles
    for target_article in target_articles:
        relevant_contexts = [
            chunk + " " + context_generated  # Concatenazione di chunk e context_generated
            for chunk, article, context_generated,_ in retrieved_contexts if article == target_article
        ]

        # Step 2: Aggiungi tutti i chunk pertinenti per l'articolo
        if relevant_contexts:
            chosen_contexts.extend(relevant_contexts)  # Aggiungi tutti i chunk pertinenti per l'articolo
        else:
            # Step 3: Fallback: Se non ci sono chunk pertinenti, prendi i primi 3 risultati
            chosen_contexts.extend([chunk + " " + context_generated for chunk, _, context_generated,_ in retrieved_contexts[:3]])

    # Step 4: Unisci i chunk in un unico contesto (stringa)
    final_context = " ".join(chosen_contexts)

    return final_context

def retrieve_and_filter_context_generated(target_articles, retrieved_contexts):
    """
    Filtra i chunk pertinenti a più articoli target e unisce tutti i chunk pertinenti per ciascun articolo.
    
    Parameters:
    - target_articles: Lista di articoli target.
    - retrieved_contexts: Lista di tuple (chunk, article, context_generated) con i risultati recuperati.
    
    Returns:
    - final_context: Una stringa contenente tutti i chunk pertinenti per i vari articoli.
    """
    chosen_contexts = []

    # Step 1: Filtra i chunk pertinenti per ciascun articolo in target_articles
    for target_article in target_articles:
        relevant_contexts = [
            context_generated  # Concatenazione di chunk e context_generated
            for _, article, context_generated,_ in retrieved_contexts if article == target_article
        ]

        # Step 2: Aggiungi tutti i chunk pertinenti per l'articolo
        if relevant_contexts:
            chosen_contexts.extend(relevant_contexts)  # Aggiungi tutti i chunk pertinenti per l'articolo
        else:
            # Step 3: Fallback: Se non ci sono chunk pertinenti, prendi i primi 3 risultati
            chosen_contexts.extend([context_generated for _, _, context_generated,_ in retrieved_contexts[:3]])

    # Step 4: Unisci i chunk in un unico contesto (stringa)
    final_context = " ".join(chosen_contexts)

    return final_context

def calculate_context_precisions(results, target_articles, k_values):
    """
    Calcola la Context Precision@K per ogni valore in k_values considerando più articoli (target_articles).
    
    Parameters:
    - results: I risultati della ricerca (contenenti i chunk e i numeri degli articoli).
    - target_articles: Lista di articoli target.
    - k_values: Lista dei valori di k per cui calcolare la precisione.

    Returns:
    - precision_list: Lista di tuple (k, precisione) per ogni valore di k.
    """
    precision_list = []
    
    for k in k_values:
        # Calcola la precisione per ogni articolo in target_articles e poi media i risultati
        precisions_at_k = []
        for target_article in target_articles:
            precision_at_k = calculate_context_precision_at_k(results, target_article, k)
            precisions_at_k.append(precision_at_k)
        
        # Calcola la media delle precisioni per tutti gli articoli target
        mean_precision_at_k = sum(precisions_at_k) / len(precisions_at_k) if precisions_at_k else 0.0
        precision_list.append((k, mean_precision_at_k))
    
    return precision_list

def find_best_k(precisions_per_k):
    """
    Trova il k con la precisione più alta.
    In caso di parità (stessa precisione), prende il k più alto.
    """
    best_k, best_precision = precisions_per_k[0]  # Inizializza con il primo elemento
    for k, precision in precisions_per_k:
        if precision > best_precision:
            best_k, best_precision = k, precision
        # Se la precisione è uguale, scegli il k più piccolo
        elif precision == best_precision and k > best_k:
            best_k = k

    return best_k

i=1

def save_precisions_to_file(precisions_list, file_path="precisions.txt"):
    """
    Salva le precisioni per una singola domanda in un file di testo in modalità append.

    Parameters:
    - precisions_per_k: Lista di tuple (k, precisione).
    - file_path: Percorso del file in cui salvare i risultati.
    """
    global i
    
    with open(file_path, "a") as file:  # Modalità append
        precisions_str = ", ".join(f"{precision}" for _, precision in precisions_list)
        file.write(f"Domanda {i} : [{precisions_str}]\n")
    i=i+1

# FUNZIONI PER GENERAZIONE

def evaluate_answers_with_retrieval(question, options, collection):

    retrieved_contexts = retrieveContext(question, collection)
    
    best_context = retrieved_contexts[0] if retrieved_contexts else "Nessun contesto trovato"
    
    response = generate_answer(question, best_context, options,)
    
    return response

def evaluate_answers_with_correttivo_and_retrieval(question, options, collection, collection_correttivi, association_table):

    retrieved_contexts = retrieveContext(question, collection)

    if retrieved_contexts:
        best_context_chunk = retrieved_contexts[0]
        
        search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
        results = collection.search(
            [mv.embed_texts(question)], 
            "embedding", 
            search_params, 
            1, 
            output_fields=["id", "chunk"]
        )
        
        if results and results[0]:  
            best_context_id = results[0][0].entity.get("id")
            
            correttivo_entry = next(
                (entry for entry in association_table if entry["articolo_id"] == best_context_id), 
                None
            )
            
            if correttivo_entry:
                correttivo_id = correttivo_entry["correttivo_id"]
                
                correttivo_result = collection_correttivi.query(
                    expr=f"id == {correttivo_id}",
                    output_fields=["Testo_Contenuto"],
                    limit=1
                )
                
                if correttivo_result:
                    correttivo_chunk = correttivo_result[0]["Testo_Contenuto"]
                    best_context_chunk += f"\n\nCorrettivo: {correttivo_chunk}"
    else:
        best_context_chunk = "Nessun contesto trovato"

    response = generate_answer(question, best_context_chunk, options)

    return response



def evaluate_answers_with_correttivo_and_articoli(question, options,contesto_articoli,article_reference,collection,is_contextual_retrieval):

    context = ""
    retrieval_precision = 0.0
    
    if(is_contextual_retrieval):
        k_values = [1, 3, 5, 10, 20, 30, 40, 50]

        retrieved_contexts = retrieveContext_with_context_generated(question, collection,50)
        precisions_per_k = calculate_context_precisions(retrieved_contexts, [article_reference], k_values)
        best_k = find_best_k(precisions_per_k)
        save_precisions_to_file(precisions_per_k)
        context = retrieve_and_filter_chunk([article_reference],retrieved_contexts[:best_k])
        contesto_articoli = ""

    response = generate_answer(question, context, options,contesto_articoli)

    return response,retrieval_precision



########################

# NewContextRetrieval.py

def header_general(question, options,collection,article,save_metrics=True):

    retrieved_contexts = retrieveContext_with_context_generated(question, collection,50)
    k = [1,3,5,10,20,50]
    recall,ndgc,mrr = calculate_metrics(retrieved_contexts,article,k)
    return recall,ndgc,mrr







def zero_shot_generation(question, options):
    
    prompt = f"Domanda: {question}\n"
    
    # Aggiungi le opzioni al prompt
    for i, option in enumerate(options, 1):
        prompt += f"Opzione {i}: {option}\n"
    
    # Aggiungi la richiesta di risposta
    prompt += "Qual è la risposta corretta? Rispondi solo con il numero della risposta corretta (non usare lettere). Niente frasi solo il numero della risposta corretta."
    
    messages = [
        {
            "role": "user", 
            "content": prompt},
    ]
    
    outputs = llm_model.chat(messages,llm_sampling_params)
    
    generated_text = ""
    
    if outputs:  # Controlla che outputs non sia vuoto
        first_output = outputs[0]  # Prendi solo il primo elemento
        prompt = first_output.prompt
        generated_text = first_output.outputs[0].text

    return generated_text

def standard_retrieval_correttivo(question, options,collection_appalti,collection_correttivo,article_appalti,article_correttivo,save_metrics=True):
    
    retrieved_contexts_appalti = retrieveContext(question, collection_appalti,50)
    retrieved_contexts_correttivo = retrieveContextCorrettivo(question, collection_correttivo,50)
    if save_metrics:
        statistics_retrieval_appalti = calculate_metrics(retrieved_contexts_appalti,article_appalti,50)
        statistics_retrieval_correttivo = calculate_metrics(retrieved_contexts_correttivo,article_correttivo,50)
        
        save_retrieval_statistics(statistics_retrieval_appalti,"standard_retrieval_statistics_gpt4o.txt")
        save_retrieval_statistics(statistics_retrieval_correttivo,"standard_retrieval_statistics_gpt4o.txt")
    context_appalti = retrieve_and_filter_chunk([article_appalti],retrieved_contexts_appalti[:5])
    context_correttivo = retrieve_and_filter_correttivo([article_correttivo],retrieved_contexts_correttivo[:5])
    context = context_correttivo+context_appalti
    response = generate_answer(question, context, options,"")
    return response

def standard_retrieval_general(question, options,collection_appalti,article_appalti,save_metrics=True):
    
    retrieved_contexts_appalti = retrieveContext(question, collection_appalti,50)
    k = [1,3,5,10,20,50]
    recall,ndgc,mrr = calculate_metrics(retrieved_contexts_appalti,article_appalti,k)
    return recall,ndgc,mrr
    
    
def recall_at_k(relevant_items, retrieved_items, k):
    """
    Calcola Recall@K.
    :param relevant_items: Set degli elementi rilevanti.
    :param retrieved_items: Lista degli elementi recuperati ordinati per rilevanza.
    :param k: Numero di elementi da considerare.
    :return: Valore di Recall@K.
    """
    retrieved_at_k = set(retrieved_items[:k])
    relevant_at_k = retrieved_at_k.intersection(relevant_items)
    return len(relevant_at_k) / len(relevant_items) if relevant_items else 0.0

def ndcg_at_k(relevant_items, retrieved_items, k):
    """
    Calcola NDCG@K usando scikit-learn.
    :param relevant_items: Dizionario {item: gain} degli elementi rilevanti con i loro guadagni.
    :param retrieved_items: Lista degli elementi recuperati ordinati per rilevanza.
    :param k: Numero di elementi da considerare.
    :return: Valore di NDCG@K.
    """
    y_true = np.zeros(len(retrieved_items))
    for i, item in enumerate(retrieved_items):
        if item in relevant_items:
            y_true[i] = relevant_items[item]
    
    return ndcg_score([y_true], [np.arange(len(retrieved_items))], k=k)
    
    
    
    
########################


def evaluate_answers_codice_appalti_generated(question, options,contesto_articoli,article_title,collection,is_contextual_retrieval):

    context = ""
    retrieval_precision = 0.0
    
    if(is_contextual_retrieval):
        k_values = [1, 3, 5, 10, 20, 30, 40, 50]
        article_reference,_ = extractArticleNumbers(article_title)
        retrieved_contexts = retrieveContext_with_context_generated(question, collection,50)
        retrieved_contexts_copy = [(chunk, article) for chunk, article, _ in retrieved_contexts]

        precisions_per_k = calculate_context_precisions(retrieved_contexts_copy, article_reference, k_values)
        best_k = find_best_k(precisions_per_k)
        save_precisions_to_file(precisions_per_k)
        if(len(article_reference) < 1):
            context = retrieve_and_filter_with_chunk_and_context_generated(article_reference,retrieved_contexts[:4])
        else:
            context = retrieve_and_filter_with_chunk_and_context_generated(article_reference,retrieved_contexts[:best_k])
 
        contesto_articoli = ""

    response = generate_answer(question, context, options,contesto_articoli)

    return response,retrieval_precision

def evaluate_answers_codice_appalti(question, options,contesto_articoli,article_title,collection,is_contextual_retrieval):

    context = ""
    retrieval_precision = 0.0
    
    if(is_contextual_retrieval):
        k_values = [1, 3, 5, 10, 20, 30, 40, 50]
        article_reference,_ = extractArticleNumbers(article_title)
        retrieved_contexts = retrieveContext(question, collection,50)

        precisions_per_k = calculate_context_precisions(retrieved_contexts, article_reference, k_values)
        best_k = find_best_k(precisions_per_k)
        save_precisions_to_file(precisions_per_k)
        if(len(article_reference) < 1):
            context = retrieve_and_filter_chunk(article_reference,retrieved_contexts[:4])
        else:
            context = retrieve_and_filter_chunk(article_reference,retrieved_contexts[:best_k])

        contesto_articoli = ""

    response = generate_answer(question, context, options,contesto_articoli)

    return response,retrieval_precision

def evaluate_answers_con_titolo(question, options,title):
    best_context,articles = retrieveArticle(title)
    # print("BEST CONTEXT:\n" + best_context)
    # print("ARTICLES:\n" + articles)
    response = generate_answer(question, best_context, options,articles)
    return response

def generate_answer(question, context, options,articles=""):

    context = truncate_context_to_fit(context, question, options,articles)
    
    messages = [
        {
            "role": "user", 
            "content": context},
    ]
    
    outputs = llm_model.chat(messages,llm_sampling_params)
    generated_text = ""
    
    if outputs:
        first_output = outputs[0]
        context = first_output.prompt
        generated_text = first_output.outputs[0].text

    return generated_text

def context_generated_genie_generations(question,options,dataset_generazioni):
    
    context = retrieve_and_merge_contexts_for_question(dataset_generazioni,question)
    articles = ""
    response = generate_answer(question, context, options,articles)
    return response

def context_generated_collection_generations(question,options,collection,article_title):
    articoli_menzionati,_ = extractArticleNumbers(article_title)
    
    context = retrieve_and_merge_all_contexts_from_collection(collection,articoli_menzionati)
    
    articles = ""
    
    response = generate_answer(question, context, options,articles)
    return response

def retrieve_and_merge_contexts_for_question(data, question):
    """
    Trova tutte le righe con la stessa domanda e unisce i loro contesti generati.
    
    Parameters:
    - data: Lista di dizionari caricata dal file JSONL.
    - question: Domanda da cercare.

    Returns:
    - merged_context: Una stringa contenente i contesti generati uniti.
    """
    # Step 1: Filtra tutte le righe con la stessa domanda
    filtered_rows = [row for row in data if row["question"] == question]
    
    # Step 2: Estrai i contesti generati
    generated_contexts = [row["generated_context"] for row in filtered_rows]

    # Step 3: Unisci i contesti generati in un'unica stringa
    merged_context = " ".join(generated_contexts)

    return merged_context

def retrieve_and_merge_all_contexts_from_collection(collection, article_list):
    """
    Recupera e unisce tutti i contesti generati per gli articoli nella lista, ordinandoli per chunk_id.

    Parameters:
    - collection: Collection di Milvus da cui recuperare i dati.
    - article_list: Lista di articoli (lista di int).

    Returns:
    - final_context: Una singola stringa contenente tutti i contesti uniti e ordinati.
    """
    # Step 1: Recupera tutti i dati che corrispondono agli articoli nella lista
    query_filter = f"article in {article_list}"
    results = collection.query(
        query_filter,
        output_fields=["article", "chunk_id", "context_generated"]
    )

    # Step 2: Ordina tutti i risultati per articolo e chunk_id
    sorted_results = sorted(results, key=lambda x: (x["article"], x["chunk_id"]))

    # Step 3: Unisci tutti i contesti generati in un'unica stringa
    final_context = " ".join(result["context_generated"] for result in sorted_results)

    return final_context