from transformers import AutoTokenizer, AutoModel,AutoModelForCausalLM,pipeline
from langchain.llms import HuggingFacePipeline
from vllm import LLM, SamplingParams
from langchain.prompts import ChatPromptTemplate
import pandas as pd
import numpy as np
import logging
import argparse
import torch
import re
import milvusDb as db

logging.basicConfig(
    format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO
)

logger = logging.getLogger(__name__)

df_codice_appalti_allegati = pd.read_csv("codice_appalti_allegati.csv", encoding="utf-8", sep=";")
df_codice_appalti = pd.read_csv("data_appalti_v2.csv",encoding="utf-8", sep=",")


chat_prompt = ChatPromptTemplate.from_template(
    """Domanda: {question}
    Contesto: {context}
    Opzioni: {options}

    Qual è la risposta corretta? Rispondi solo con il numero della risposta corretta senza aggiungere altro. deve essere riportato solo un numero niente parole o frasi aggiuntive."""
)

def load_models_alternative(model_name):
    
    global embedder_model,llm_model,hf_pipeline

    embedder_model = db.get_embedder()

    logger.info("Caricamento del modello di generazione...")
    # Inizializza tokenizer e modello
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    hf_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        temperature=0.8,
        max_new_tokens=3,
        top_k=3,
        top_p=0.95,
        do_sample=True,
        return_full_text=False,
        eos_token_id=tokenizer.eos_token_id
    )

    # Integrazione con LangChain
    llm_model = HuggingFacePipeline(pipeline=hf_pipeline)
    logger.info("Caricamento completato")  
  

    
def setModel():
    global llm_model,llm_sampling_params,embedder_model
    embedder_model = db.get_embedder()
    llm_model,llm_sampling_params = db.getModel()



# GENERAZIONI QUESTION MULTIPLE CHOICE CON CORRETTIVO

def contextualRetrievalWithCorrettivo_mc_alternative(question,options,collection,collectionCorrettivo,tabella_associazione_corretivi):
    
    return evaluate_answers_with_correttivo_mc_alternative(question,options,collection,collectionCorrettivo,tabella_associazione_corretivi)

def evaluate_answers_with_correttivo_mc_alternative(question, options, collection, collection_correttivi, association_table):
    # Recupera il contesto pertinente dal DB Milvus
    retrieved_contexts = db.retrieveContext(question, collection)

    # Seleziona il contesto più pertinente (ad esempio, il primo recuperato)
    if retrieved_contexts:
        best_context_chunk = retrieved_contexts[0]  # Testo del chunk più pertinente
        
        # Recupera l'ID del chunk corrispondente
        search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
        results = collection.search(
            [db.embed_text_single(question, embedder_model)], 
            "embedding", 
            search_params, 
            1, 
            output_fields=["id", "chunk"]
        )
        
        if results and results[0]:  
            best_context_id = results[0][0].entity.get("id")  # ID del chunk più pertinente
            
            # Trova il correttivo_id corrispondente nella tabella di associazione
            correttivo_entry = next(
                (entry for entry in association_table if entry["articolo_id"] == best_context_id), 
                None
            )
            
            if correttivo_entry:
                correttivo_id = correttivo_entry["correttivo_id"]
                
                # Recupera il chunk del correttivo dalla collection dei correttivi
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

    # Genera la risposta basata sul contesto aggiornato
    response = generate_answer_mc_alternative(question, best_context_chunk, options)

    return response



# GENERAZIONI QUESTION ANSWERING ALTERNATIVE CON CORRETTIVO

def contextualRetrievalWithCorrettivo_qa_alternative(question,options,collection,collectionCorrettivo,tabella_associazione_corretivi):
    
    return evaluate_answers_with_correttivo_qa_alternative(question,options,collection,collectionCorrettivo,tabella_associazione_corretivi)

def evaluate_answers_with_correttivo_qa_alternative(question, options, collection, collection_correttivi, association_table):
    # Recupera il contesto pertinente dal DB Milvus
    retrieved_contexts = db.retrieveContext(question, collection)

    # Seleziona il contesto più pertinente (ad esempio, il primo recuperato)
    if retrieved_contexts:
        best_context_chunk = retrieved_contexts[0]  # Testo del chunk più pertinente
        
        # Recupera l'ID del chunk corrispondente
        search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
        results = collection.search(
            [db.embed_text_single(question, embedder_model)], 
            "embedding", 
            search_params, 
            1, 
            output_fields=["id", "chunk"]
        )
        
        if results and results[0]:  
            best_context_id = results[0][0].entity.get("id")  # ID del chunk più pertinente
            
            # Trova il correttivo_id corrispondente nella tabella di associazione
            correttivo_entry = next(
                (entry for entry in association_table if entry["articolo_id"] == best_context_id), 
                None
            )
            
            if correttivo_entry:
                correttivo_id = correttivo_entry["correttivo_id"]
                
                # Recupera il chunk del correttivo dalla collection dei correttivi
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

    # Genera la risposta basata sul contesto aggiornato
    response = generate_answer_qa_alternative(question, best_context_chunk, options)

    return response



# GENERAZIONI QUESTION ANSWERING ALTERNATIVE

def contextualRetrieval_qa_alternative(question, options, collection,title,context=False):
    
    return evaluate_answers_qa_alternative(question, options, collection,context,title)

def evaluate_answers_qa_alternative(question, options, collection,context,title):
    best_context = ""
    if context:
        retrieved_contexts = db.retrieveContext(question, collection)
        best_context += retrieved_contexts[0] if retrieved_contexts else "Nessun contesto trovato"
    best_context += retrieveArticle(title)
    response = generate_answer_qa_alternative(question, best_context, options)
    return response

def generate_answer_qa_alternative(question, context, options):
    # Prepara il prompt per il modello di generazione
    # prompt = f"Domanda: {question}\nContesto: {context}\n"
    prompt = f"Domanda: {question}\nContesto: {context}\n"
    
    # Aggiungi le opzioni al prompt
    for i, option in enumerate(options, 1):
        prompt += f"Opzione {i}: {option}\n"
    
    # Aggiungi la richiesta di risposta
    prompt += "Qual è la risposta corretta? Rispondi solo con il numero della risposta corretta (non usare lettere). Niente frasi solo il numero della risposta corretta."
    
    messages = [
        {
            "role": "system",
            "content": "Rispondi alle domande fornendo come risposta solo il numero della risposta corretta.",
        },
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


# GENERAZIONI QUESTION MULTIPLE CHOICE

def contextualRetrieval_mc_alternative(question, options, collection):
    
    return evaluate_answers_mc_alternative(question, options, collection)

def evaluate_answers_mc_alternative(question, options, collection):
    retrieved_article = retrieveArticle()
    
    response = generate_answer_mc_alternative(question, retrieved_article, options)
    
    return response

def generate_answer_mc_alternative(question, context, options):
    # Prepara il prompt per il modello di generazione
    prompt = f"Domanda: {question}\nArticolo di riferimento: {context}\n"
    
    # Aggiungi le opzioni al prompt
    for i, option in enumerate(options, 1):
        prompt += f"Opzione {i}: {option}\n"
    
    # Aggiungi la richiesta di risposta
    prompt += "Qual è la risposta corretta? Rispondi solo con il numero della risposta corretta. Niente frasi solo il numero della risposta corretta."

    # Genera la risposta usando la pipeline di Hugging Face
    generated_text = hf_pipeline(prompt, max_length=256, num_return_sequences=1)[0]['generated_text']

    return generated_text



# GENERAZIONI QUESTION SENZA NESSUNA AGGIUNTA

def generate_answer_qa_only_question_alternative(question, options):
    
    prompt = f"Domanda: {question}\n"
    
    # Aggiungi le opzioni al prompt
    for i, option in enumerate(options, 1):
        prompt += f"Opzione {i}: {option}\n"
    
    # Aggiungi la richiesta di risposta
    prompt += "Qual è la risposta corretta? Rispondi solo con il numero della risposta corretta (non usare lettere). Niente frasi solo il numero della risposta corretta."
    
    messages = [
        {
            "role": "system",
            "content": "Rispondi alle domande fornendo come risposta solo il numero della risposta corretta.",
        },
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


# OTHER FUNCTIONS

def retrieveArticle(title):
    results = []
    
    # Estrarre informazioni dal titolo
    allegato_match = re.search(r'ALLEGATO\s([IVXLCDM\.\d]+)', title, re.IGNORECASE)
    articoli_match = re.findall(r'Art(?:icolo|\.)\s(\d+)', title)
    
    # Rimuovi i duplicati dagli articoli e allegati
    articoli_match = list(set(map(str, articoli_match)))
    if allegato_match:
        allegato = f"ALLEGATO {allegato_match.group(1)}"
        allegato_match = {allegato}  # Usando un set per garantire unicità
    
    if allegato_match:
        # Filtriamo il dataset degli allegati
        df_filtered = df_codice_appalti_allegati[df_codice_appalti_allegati['Allegato'] == allegato]
        df_filtered = df_filtered.sort_values(by=['Articolo'])
        
        # Controlliamo se df_filtered non è vuoto
        if not df_filtered.empty:
            results.append("\n".join(df_filtered['contenuto'].astype(str)))
    
    if articoli_match:
        for articolo in articoli_match:
            df_filtered = df_codice_appalti[df_codice_appalti['Articolo'] == articolo]
            df_filtered = df_filtered.sort_values(by=['Comma'])
            
            # Controlliamo se df_filtered non è vuoto
            if not df_filtered.empty:
                results.append("\n".join(df_filtered['Testo_Contenuto'].astype(str)))
    
    return "\n".join(filter(None, results))
    