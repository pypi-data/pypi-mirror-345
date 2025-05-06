from transformers import AutoTokenizer, pipeline
import pandas as pd
import psutil
import os
import spacy
from findReferencesOptimized import extract_references
from vllm import LLM, SamplingParams


# Prompt di sistema
system_prompt = """
You are an AI assistant skilled at generating context and additional information for a provided chunk of text and his correttivo. When references to articles and paragraphs are included, you can explain and contextualize them using the provided references.
You task is to define a header for a chunk of this article to preserve the contexual information of the whole text without adding any prehamble or comment. this chunk is provided to a RAG system. use bullet list for expain better.
Please give a short succinct context for the purposes of improving search retrieval of the chunk. You MUST use a correct italian language.
"""

# Function for monitoring RAM usage
def get_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    rss = memory_info.rss / (1024 * 1024)
    return rss

# Function for load dataset from a .csv file
def downloadDataset(dataset):
    # Caricamento dei dati e processing di questi ultimi
    data = pd.read_csv(dataset, sep=",", encoding="utf-8")
    data_filtered = data[(data["Comma"].notna()) & (pd.isna(data["Allegato"]))]

    # Raggruppa i dati per Decreto e Articolo
    grouped = data_filtered.groupby(["Decreto", "Articolo"])

    references_grouped = data[(data["Comma"].isna()) & (pd.isna(data["Allegato"]))].groupby(["Decreto", "Articolo"])

    allegati_grouped = data[pd.notna(data["Allegato"])].groupby(["Decreto", "Allegato"])


    # Salviamo i vari articoli completi
    text_articles = {}

    for (decreto, articolo), group in grouped:

        sorted_group = group.sort_values(by="Comma")

        testo_contenuto = " ".join(sorted_group["Testo_Contenuto"].tolist())

        text_articles[(decreto, articolo)] = testo_contenuto
        
        
    text_allegati = {}
    for (decreto, allegato), group in allegati_grouped:
        testo_contenuto = " ".join(group["Testo_Contenuto"].tolist())
        text_allegati[(decreto, allegato)] = testo_contenuto

    return grouped, references_grouped, allegati_grouped, text_articles, text_allegati


# Inizialize the selected model
def inizializeModel(model,isPhi4=False):

    if(isPhi4):
        phi4tokenizer = "microsoft/phi-4"
        phi4model_path = "phi-4-Q4_K_M.gguf"

        # Parametri di campionamento
        phi4sampling_params = SamplingParams(
            temperature=0.8, 
            max_tokens=1024,
            min_tokens=16,
            top_k=10,
            top_p=0.95
        )

        # Inizializza il modello e il tokenizer
        llm_phi4 = LLM(model=phi4model_path, tokenizer=phi4tokenizer)

        return llm_phi4,phi4sampling_params,None

    else:

        tokenizer = AutoTokenizer.from_pretrained(model)

        llm = pipeline("text-generation",
                    model=model,
                    model_kwargs={
                        "device_map" : "cuda",
                        "torch_dtype" : "bfloat16"
                        }
                    )

        # Configurazione per la generazione
        gen_config = {
            "max_new_tokens" : 2048,
            "min_new_tokens" : 32,
            "do_sample" : True,
            "temperature" : 0.2,
            "top_k" : 30,
            "num_return_sequences" : 1,
        }

        return llm,gen_config,tokenizer
       

def split_with_spacy(text):
    nlp = spacy.load("it_core_news_sm") # python -m spacy download it_core_news_sm
    doc = nlp(text)
    chunks = [sent.text.strip() for sent in doc.sents]
    return chunks

def merge_short_chunks(chunks, min_length=45):
    merged_chunks = []
    buffer = "" 

    for chunk in chunks:
        buffer += (" " + chunk).strip()

        if len(buffer) >= min_length:
            merged_chunks.append(buffer)
            buffer = "" 

    if buffer:
        merged_chunks.append(buffer)

    return merged_chunks


def constructPrompt(article,references,chunk):
    
    context_generation_prompt = """
    
       Genera un testo breve e conciso che esegua un riassunto del chunk e utilizzi il testo del correttivo disponibile nei riferimenti. Molto importante l'inserimento del correttivo nella risposta.
       I riferimenti li trovi nelle referenze. Utilizza un linguaggio italiano corretto
       senza introdurre commenti o frasi superflue. La risposta deve essere sintetica ma completa è scritta in modo diretto,
       NON USARE ASSOLUTAMENTE frasi del tipo "Il contesto" o "il chunk" o "il testo descrive" o "il frammento".Testo di massimo di 200 parole. Struttura la risposta
       come la risposta di questo esempio:
       
       esempio:
       "
       1.Tutte le stazioni appaltanti, fermi restando gli obblighi di utilizzo di strumenti di acquisto e
        di negoziazione previsti dalle vigenti disposizioni in materia di contenimento della spesa, possono
        procedere direttamente e autonomamente all'acquisizione di forniture e servizi di importo non
        superiore alle soglie previste per gli affidamenti diretti, e all'affidamento di lavori d'importo
        pari o inferiore a 500.000 euro, nonché attraverso l'effettuazione di ordini a valere su strumenti
        di acquisto messi a disposizione dalle centrali di committenza qualificate e dai soggetti
        aggregatori.
        "
        risposta:
        "
        Le stazioni appaltanti acquisiscono forniture, servizi e lavori agendo direttamente per importi inferiori alle soglie degli affidamenti diretti e per lavori fino a 500.000 euro. Possono inoltre utilizzare strumenti di acquisto forniti da centrali di committenza qualificate e soggetti aggregatori. È obbligatorio rispettare le norme relative all'uso di strumenti di acquisto e di negoziazione per il contenimento della spesa. Le disposizioni garantiscono efficienza ed efficacia amministrativa nelle procedure di acquisizione.
        "
  
        Nota che il testo è diretto, senza frasi inizali o commenti.  
    
    
        Qui c'è l'articolo:
        <articolo>
        {SPECIFIC_ARTICLE}
        </articolo>

        Qui ci sono i riferimenti:
        <riferimenti>
        {REFERENCES}
        </riferimenti>

        qui c'è il chunk da analizzare:
        <chunk>
        {CHUNK}
        </chunk>

        """.strip()
    
    return context_generation_prompt.format(
                SPECIFIC_ARTICLE=article,REFERENCES=references,CHUNK=chunk
            )
    

def generation_with_chunks(llm,config,tokenizer,text_articles):
    """
    Generate chunks of context forassociated article texts. Every articles is divided in chunks and foreach chunk
    we generate a context.

    Parameters:
        text_articles: Dictionary containing article texts, indexed by (decree, article).

    Returns:
        List of dictionaries with generated chunks and context.
    """

    generated_chunks = []
    
    for key, value in text_articles.items():
        # Splitta il testo in chunks
        chunks = split_with_spacy(value)

        # Unisci i chunks troppo corti
        merged_chunks = merge_short_chunks(chunks, min_length=45)

        for chunk in merged_chunks:

            input_prompt = constructPrompt(value,"",chunk)

            chat_formatted_template = tokenizer.apply_chat_template([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_prompt}
            ], tokenize=False, add_generation_prompt=True)
            
            # Generazione del contesto
            gen_ctx = llm(chat_formatted_template, **config)[0]["generated_text"].strip()

            # Aggiungi il risultato alla lista dei chunks generati
            generated_chunks.append({
                "decree": key[0],
                "article": key[1],
                "chunk": chunk,
                "context_generated": gen_ctx
            })
            
            print(f"\nGenerated Response:\n -CHUNK:\n {chunk} \n ************ \n -CONTESTO GENERATO:\n {gen_ctx}\n\n\n")
            print("-"*50)

    return generated_chunks


def generation_with_commas(llm,config,tokenizer,grouped_commas,grouped_allegati,references_grouped,text_articles,text_allegati,isPhi4):

    generated_chunks = []
    
    i=1

    for (decreto, articolo), group in grouped_commas:

        article_text = text_articles.get((decreto, articolo), "")

        if not article_text:
            print(f"No text found for Decreto: {decreto}, Articolo: {articolo}. Skipping.")
            continue

        for chunk in group["Testo_Contenuto"]:
            
            riga_associata = group[group["Testo_Contenuto"] == chunk]
    
            # Verifica se la riga è stata trovata
            if not riga_associata.empty:
                # Estrai titolo e articolo dalla riga trovata
                titolo_articolo_associato = riga_associata["titolo_art"].values[0]
            
            ### RIFERIMENTI ESTERNI
            references_content = []

            if (decreto, articolo) in references_grouped.groups:
                reference_group = references_grouped.get_group((decreto, articolo))

                for _, ref_row in reference_group.iterrows():
                    riferimento = ref_row["Riferimento"].removesuffix(".txt")
                    testo_riferimento = ref_row["Testo_Contenuto"]

                    if riferimento in chunk:
                        references_content.append(f"Riferimento a {riferimento}:\n  {testo_riferimento}\n\n")


            ### RIFERIMENTI INTERNI

            internal_references = extract_references(chunk, False)


            if internal_references:
                references_content_internal = []

                for wordList in internal_references:
                    articoli_commi = {"articolo": [], "comma": []}
                    allegati_trovati = []

                    for word in wordList:
                        if word[0].lower() in ["articolo", "articoli"]:
                            numero_articolo = word[1]
                            articoli_commi["articolo"].append(numero_articolo)
                        elif word[0].lower() in ["comma", "commi"]:
                            numero_comma = word[1]
                            articoli_commi["comma"].append(numero_comma)
                        elif word[0].lower() in ["allegato","allegati"]:
                            allegati_trovati.append(f"{word[0]} {word[1]}")

                    if len(articoli_commi["articolo"]) > 0:
                        for articolo_internal in articoli_commi["articolo"]:
                            try:
                                group_internal = grouped_commas.get_group((decreto, articolo_internal))
                            except KeyError:
                                print("gruppo non trovato\n\n")
                                continue

                            if len(articoli_commi["comma"]) >= 1:
                                for num_comma in articoli_commi["comma"]:
                                    filtered_group = group_internal[group_internal['Comma'] == num_comma]

                                    if not filtered_group.empty:
                                        references_content_internal.append(f"Riferimento ad articolo {articolo_internal} comma {num_comma} di questo decreto:\n {filtered_group['Testo_Contenuto'].to_string(index=False)}\n\n")
                            else:
                                testo_contenuto = group_internal['Testo_Contenuto'].tolist()
                                testo_concatenato = "\n".join(testo_contenuto)
                                references_content_internal.append(f"Riferimento ad articolo {articolo_internal} di questo decreto: \n{testo_concatenato}\n\n")

                        if len(allegati_trovati) > 0:
                            for allegato_trovato in allegati_trovati:
                                try:
                                    group_allegato = grouped_allegati.get_group((decreto, allegato_trovato))
                                except KeyError:
                                    print("Gruppo allegato non trovato per", allegato_trovato)
                                    continue
                                contenuti = group_allegato['Contenuto'].tolist()
                                testo_concatenato = "\n".join(contenuti)
                                references_content_internal.append(
                                    f"Riferimento ad {allegato_trovato} di questo decreto: \n{testo_concatenato}\n\n"
                                )
                        
                references_content.extend(references_content_internal)
            
            references_content = ''.join(references_content)
            
            input_prompt = constructPrompt(article_text,references_content,chunk)

            if(isPhi4):
                result=microsoft_phi_4_generation(llm,config,input_prompt)
                generated_chunks.append({
                    "id": i,
                    "decree": decreto,
                    "article": articolo,
                    "chunk": chunk,
                    "context_generated": result,
                    "article_title" : titolo_articolo_associato,
                    "titolo_allegato":None,
                    "allegato" : None
                })
                i=i+1
            else:
                # Generate the context using the language model
                gen_ctx = pipeline_generation(llm,config,tokenizer,input_prompt)
                
                # Append the result to the generated chunks list
                generated_chunks.append({
                    "id": i,
                    "decree": decreto,
                    "article": articolo,
                    "chunk": chunk,
                    "context_generated": gen_ctx,
                    "article_title" : titolo_articolo_associato,
                    "titolo_allegato":None,
                    "allegato" : None
                })
                i=i+1
                
    
    for (decreto, allegato), group in grouped_allegati:

        allegato_text = text_allegati.get((decreto, allegato), "")

        if not allegato_text:
            print(f"No text found for Decreto: {decreto}, Allegato: {allegato}. Skipping.")
            continue

        for chunk in group["Testo_Contenuto"]:

            riga_associata = group[group["Testo_Contenuto"] == chunk]
    
            # Verifica se la riga è stata trovata
            if not riga_associata.empty:
                # Estrai titolo e articolo dalla riga trovata
                titolo_articolo_associato = riga_associata["titolo_art"].values[0]
                articolo_associato = riga_associata["Articolo"].values[0]
                allegato_associato = riga_associata["Allegato"].values[0]
                titolo_allegato_associato = riga_associata["TitoloAllegato"].values[0]
                
                
            ### RIFERIMENTI INTERNI
            references_content = []

            internal_references = extract_references(chunk, False)

            if internal_references:
                references_content_internal = []

                for wordList in internal_references:
                    articoli_commi = {"articolo": [], "comma": []}
                    allegati_trovati = []

                    for word in wordList:
                        if word[0].lower() in ["articolo", "articoli"]:
                            numero_articolo = word[1]
                            articoli_commi["articolo"].append(numero_articolo)
                        elif word[0].lower() in ["comma", "commi"]:
                            numero_comma = word[1]
                            articoli_commi["comma"].append(numero_comma)
                        elif word[0].lower() in ["allegato","allegati"]:
                            allegati_trovati.append(f"{word[0]} {word[1]}")

                    if len(articoli_commi["articolo"]) > 0:
                        for articolo_internal in articoli_commi["articolo"]:
                            try:
                                group_internal = grouped_commas.get_group((decreto, articolo_internal))
                            except KeyError:
                                print("gruppo non trovato\n\n")
                                continue

                            if len(articoli_commi["comma"]) >= 1:
                                for num_comma in articoli_commi["comma"]:
                                    filtered_group = group_internal[group_internal['Comma'] == num_comma]

                                    if not filtered_group.empty:
                                        references_content_internal.append(f"Riferimento ad articolo {articolo_internal} comma {num_comma} di questo decreto:\n {filtered_group['Testo_Contenuto'].to_string(index=False)}\n\n")
                            else:
                                testo_contenuto = group_internal['Testo_Contenuto'].tolist()
                                testo_concatenato = "\n".join(testo_contenuto)
                                references_content_internal.append(f"Riferimento ad articolo {articolo_internal} di questo decreto: \n{testo_concatenato}\n\n")

                        if len(allegati_trovati) > 0:
                            for allegato_trovato in allegati_trovati:
                                try:
                                    group_allegato = grouped_allegati.get_group((decreto, allegato_trovato))
                                except KeyError:
                                    print("Gruppo allegato non trovato per", allegato_trovato)
                                    continue
                                contenuti = group_allegato['Contenuto'].tolist()
                                testo_concatenato = "\n".join(contenuti)
                                references_content_internal.append(
                                    f"Riferimento ad {allegato_trovato} di questo decreto: \n{testo_concatenato}\n\n"
                                )
                        
                references_content.extend(references_content_internal)

            references_content = ''.join(references_content)
            input_prompt = constructPrompt(allegato_text,references_content,chunk)

            if(isPhi4):
                result=microsoft_phi_4_generation(llm,config,input_prompt)
                generated_chunks.append({
                    "id": i,
                    "decree": decreto,
                    "article": articolo_associato,
                    "chunk": chunk,
                    "context_generated": result,
                    "article_title" : titolo_articolo_associato,
                    "titolo_allegato":titolo_allegato_associato,
                    "allegato" : allegato_associato
                })
                i=i+1
                                
            else:
                # Generate the context using the language model
                gen_ctx = pipeline_generation(llm,config,tokenizer,input_prompt)
                
                # Append the result to the generated chunks list
                generated_chunks.append({
                    "id": i,
                    "decree": decreto,
                    "article": articolo_associato,
                    "chunk": chunk,
                    "context_generated": result,
                    "article_title" : titolo_articolo_associato,
                    "titolo_allegato": titolo_allegato_associato,
                    "allegato" : allegato_associato
                })
                i=i+1            
                
    
    return generated_chunks



def generation_with_commas_and_correttivo(llm,config,tokenizer,grouped_commas,references_grouped,text_articles,isPhi4,dataset_correttivo,grouped_allegati,text_allegati):

    generated_chunks = []
    
    i=1

    for (decreto, articolo), group in grouped_commas:

        article_text = text_articles.get((decreto, articolo), "")

        if not article_text:
            print(f"No text found for Decreto: {decreto}, Articolo: {articolo}. Skipping.")
            continue

        for chunk in group["Testo_Contenuto"]:
            
            references_content = []
            
            articolo_normalizzato = normalize_articolo(articolo)

            articolo_rows = dataset_correttivo[dataset_correttivo['article_reference'].apply(normalize_articolo) == articolo_normalizzato]
            
            # Estraiamo Testo_Contenuto per ogni riga
            for _, row in articolo_rows.iterrows():
                testo_contenuto = row['Testo_Contenuto']
                references_content.append(f"Riferimento a articolo {articolo} del codice correttivo:\n {testo_contenuto}\n\n")

            ### RIFERIMENTI INTERNI

            internal_references = extract_references(chunk, False)

            if internal_references:
                references_content_internal = []

                for wordList in internal_references:
                    articoli_commi = {"articolo": [], "comma": []}
                    allegati_trovati = []

                    for word in wordList:
                        if word[0].lower() in ["articolo", "articoli"]:
                            numero_articolo = word[1]
                            articoli_commi["articolo"].append(numero_articolo)
                        elif word[0].lower() in ["comma", "commi"]:
                            numero_comma = word[1]
                            articoli_commi["comma"].append(numero_comma)
                        elif word[0].lower() in ["allegato","allegati"]:
                            allegati_trovati.append(f"{word[0]} {word[1]}")

                    if len(articoli_commi["articolo"]) > 0:
                        for articolo_internal in articoli_commi["articolo"]:
                            try:
                                group_internal = grouped_commas.get_group((decreto, articolo_internal))
                            except KeyError:
                                print("gruppo non trovato\n\n")
                                continue

                            if len(articoli_commi["comma"]) >= 1:
                                for num_comma in articoli_commi["comma"]:
                                    filtered_group = group_internal[group_internal['Comma'] == num_comma]

                                    if not filtered_group.empty:
                                        references_content_internal.append(f"Riferimento ad articolo {articolo_internal} comma {num_comma} di questo decreto:\n {filtered_group['Testo_Contenuto'].to_string(index=False)}\n\n")
                            else:
                                testo_contenuto = group_internal['Testo_Contenuto'].tolist()
                                testo_concatenato = "\n".join(testo_contenuto)
                                references_content_internal.append(f"Riferimento ad articolo {articolo_internal} di questo decreto: \n{testo_concatenato}\n\n")

                        if len(allegati_trovati) > 0:
                            for allegato_trovato in allegati_trovati:
                                try:
                                    group_allegato = grouped_allegati.get_group((decreto, allegato_trovato))
                                except KeyError:
                                    print("Gruppo allegato non trovato per", allegato_trovato)
                                    continue
                                contenuti = group_allegato['Contenuto'].tolist()
                                testo_concatenato = "\n".join(contenuti)
                                references_content_internal.append(
                                    f"Riferimento ad {allegato_trovato} di questo decreto: \n{testo_concatenato}\n\n"
                                )
                        
                references_content.extend(references_content_internal)

            references_content = ''.join(references_content)
            input_prompt = constructPrompt(article_text,references_content,chunk)
            
            if(isPhi4):
                result=microsoft_phi_4_generation(llm,config,input_prompt)
                generated_chunks.append({
                    "id": i,
                    "decree": decreto,
                    "article": articolo,
                    "chunk": chunk,
                    "context_generated": result,
                    "article_title" : group["titolo_art"]

                })
                i=i+1
            else:
                # Generate the context using the language model
                gen_ctx = pipeline_generation(llm,config,tokenizer,input_prompt)
                
                # Append the result to the generated chunks list
                generated_chunks.append({
                    "id": i,
                    "decree": decreto,
                    "article": articolo,
                    "chunk": chunk,
                    "context_generated": gen_ctx,
                    "article_title" : group["titolo_art"]
                })
                i=i+1
     
     
    for (decreto, allegato), group in grouped_allegati:

        allegato_text = text_allegati.get((decreto, allegato), "")

        if not allegato_text:
            print(f"No text found for Decreto: {decreto}, Allegato: {allegato}. Skipping.")
            continue

        for chunk in group["Testo_Contenuto"]:

            riga_associata = group[group["Testo_Contenuto"] == chunk]
    
            # Verifica se la riga è stata trovata
            if not riga_associata.empty:
                # Estrai titolo e articolo dalla riga trovata
                titolo_articolo_associato = riga_associata["titolo_art"].values[0]
                articolo_associato = riga_associata["Articolo"].values[0]
                allegato_associato = riga_associata["Allegato"].values[0]
                titolo_allegato_associato = riga_associata["TitoloAllegato"].values[0]
            
                
            ### RIFERIMENTI INTERNI
            references_content = []

            articolo_normalizzato = normalize_articolo(articolo)

            articolo_rows = dataset_correttivo[dataset_correttivo['article_reference'].apply(normalize_articolo) == articolo_normalizzato]
            
            # Estraiamo Testo_Contenuto per ogni riga
            for _, row in articolo_rows.iterrows():
                testo_contenuto = row['Testo_Contenuto']
                references_content.append(f"Riferimento a articolo {articolo} del codice correttivo:\n {testo_contenuto}\n\n")

            internal_references = extract_references(chunk, False)

            if internal_references:
                references_content_internal = []

                for wordList in internal_references:
                    articoli_commi = {"articolo": [], "comma": []}
                    allegati_trovati = []

                    for word in wordList:
                        if word[0].lower() in ["articolo", "articoli"]:
                            numero_articolo = word[1]
                            articoli_commi["articolo"].append(numero_articolo)
                        elif word[0].lower() in ["comma", "commi"]:
                            numero_comma = word[1]
                            articoli_commi["comma"].append(numero_comma)
                        elif word[0].lower() in ["allegato","allegati"]:
                            allegati_trovati.append(f"{word[0]} {word[1]}")

                    if len(articoli_commi["articolo"]) > 0:
                        for articolo_internal in articoli_commi["articolo"]:
                            try:
                                group_internal = grouped_commas.get_group((decreto, articolo_internal))
                            except KeyError:
                                print("gruppo non trovato\n\n")
                                continue

                            if len(articoli_commi["comma"]) >= 1:
                                for num_comma in articoli_commi["comma"]:
                                    filtered_group = group_internal[group_internal['Comma'] == num_comma]

                                    if not filtered_group.empty:
                                        references_content_internal.append(f"Riferimento ad articolo {articolo_internal} comma {num_comma} di questo decreto:\n {filtered_group['Testo_Contenuto'].to_string(index=False)}\n\n")
                            else:
                                testo_contenuto = group_internal['Testo_Contenuto'].tolist()
                                testo_concatenato = "\n".join(testo_contenuto)
                                references_content_internal.append(f"Riferimento ad articolo {articolo_internal} di questo decreto: \n{testo_concatenato}\n\n")

                        if len(allegati_trovati) > 0:
                            for allegato_trovato in allegati_trovati:
                                try:
                                    group_allegato = grouped_allegati.get_group((decreto, allegato_trovato))
                                except KeyError:
                                    print("Gruppo allegato non trovato per", allegato_trovato)
                                    continue
                                contenuti = group_allegato['Contenuto'].tolist()
                                testo_concatenato = "\n".join(contenuti)
                                references_content_internal.append(
                                    f"Riferimento ad {allegato_trovato} di questo decreto: \n{testo_concatenato}\n\n"
                                )
                        
                references_content.extend(references_content_internal)

            references_content = ''.join(references_content)
            input_prompt = constructPrompt(allegato_text,references_content,chunk)

            if(isPhi4):
                result=microsoft_phi_4_generation(llm,config,input_prompt)
                generated_chunks.append({
                    "id": i,
                    "decree": decreto,
                    "article": articolo_associato,
                    "chunk": chunk,
                    "context_generated": result,
                    "article_title" : titolo_articolo_associato,
                    "titolo_allegato":titolo_allegato_associato,
                    "allegato" : allegato_associato
                })
                i=i+1
                                
            else:
                # Generate the context using the language model
                gen_ctx = pipeline_generation(llm,config,tokenizer,input_prompt)
                
                # Append the result to the generated chunks list
                generated_chunks.append({
                    "id": i,
                    "decree": decreto,
                    "article": articolo_associato,
                    "chunk": chunk,
                    "context_generated": result,
                    "article_title" : titolo_articolo_associato,
                    "titolo_allegato": titolo_allegato_associato,
                    "allegato" : allegato_associato
                })
                i=i+1
                
    return generated_chunks


def microsoft_phi_4_generation(llm,config,user_prompt):
        
    # Prepara la richiesta con il prompt
    prompt = [{"role": "user", "content": user_prompt}]
    
    # Esegui l'inferenza per ottenere la risposta
    responses = llm.chat(prompt,config)
    for response in responses:
        generated_text=response.outputs[0].text
    return generated_text

    
def pipeline_generation(llm,config,tokenizer,user_prompt):
    chat_formatted_template = tokenizer.apply_chat_template([
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
    ], tokenize=False, add_generation_prompt=True)

    # Generate the context using the language model
    gen_ctx = llm(chat_formatted_template, **config)[0]["generated_text"].strip()
    return gen_ctx

def normalize_articolo(articolo):
    """
    Normalizza l'articolo, estraendo la parte numerativa se contiene il prefisso 'ALLEGATO'.
    """
    if isinstance(articolo, str) and articolo.upper().startswith("ALLEGATO"):
        # Estrai tutto ciò che segue "ALLEGATO" e rimuovi eventuali spazi
        return articolo.split("ALLEGATO", 1)[-1].strip()
    return str(articolo)