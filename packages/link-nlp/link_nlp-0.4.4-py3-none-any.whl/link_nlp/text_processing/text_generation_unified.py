import pandas as pd
import os
from tqdm import tqdm
from transformers import AutoTokenizer
from .findReferencesOptimized import extract_references
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
import spacy

class TextGenerator:
    """
    Classe per la generazione di contesti per frammenti di testo estratti da articoli di decreti legislativi.
    """
    
    def __init__(self, model_name="Qwen/Qwen2.5-1.5B-Instruct", device="cuda", use_llm=True, dtype="float16", enable_thinking=False):
        """
        Inizializza il generatore di testo.
        
        Args:
            model_name (str): Nome del modello da utilizzare
            device (str): Dispositivo su cui eseguire il modello (cuda o cpu)
            use_llm (bool): Se True, utilizza LLM invece di pipeline per l'inferenza
            dtype (str): Tipo di dati da utilizzare (float16 o bfloat16)
        """
        self.model_name = model_name
        self.device = device
        self.use_llm = use_llm
        self.dtype = dtype
        self.enable_thinking = enable_thinking
        self.system_prompt = """
        Sei un assistente AI specializzato nel diritto italiano, in particolare nel codice degli appalti.
        Il tuo compito è fornire risposte chiare, concise e dirette in italiano.
        NON devi mai mostrare il tuo processo di pensiero o utilizzare tag HTML.
        Rispondi sempre direttamente alla domanda, senza preamboli o commenti sul processo di pensiero.
        Usa un linguaggio chiaro e professionale, evitando gergo tecnico non necessario.
        """
        #self.system_prompt =
        #You are an AI assistant skilled at generating context and additional information for a provided chunk of text and his correttivo. When references to articles and paragraphs are included, you can explain and contextualize them using the provided references.
        #You task is to define a header for a chunk of this article to preserve the contexual information of the whole text without adding any prehamble or comment. this chunk is provided to a RAG system. use bullet list for expain better.
        #Please give a short succinct context for the purposes of improving search retrieval of the chunk. You MUST use a correct italian language.
      
        
        # Inizializza il modello e il tokenizer
        self._initialize_model()
        
        # Carica il modello spaCy per la tokenizzazione
        try:
            self.nlp = spacy.load("it_core_news_sm")
        except OSError:
            print("Modello spaCy 'it_core_news_sm' non trovato. Installalo con: python -m spacy download it_core_news_sm")
            self.nlp = None
    
    def _initialize_model(self):
        """Inizializza il modello di linguaggio e il tokenizer."""
        if self.use_llm:
            # Inizializza il tokenizer e il modello
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype="auto",
                device_map="auto"
            )
            
            # Configurazione per la generazione
            self.gen_config = {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "top_k": 50,
                "top_p": 0.95,
                "repetition_penalty": 1.1
            }
        else:
            # Configurazione per pipeline (legacy)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.gen_config = {
                "max_new_tokens": 128,
                "min_new_tokens": 16,
                "do_sample": True,
                "temperature": 0.2,
                "top_k": 30,
                "num_return_sequences": 1,
            }
            # Nota: la pipeline non è più utilizzata, ma mantenuta per compatibilità
    
    def load_dataset(self, dataset_path, test_rows=None):
        """
        Carica e prepara il dataset da un file CSV.
        
        Args:
            dataset_path (str): Percorso del file CSV
            test_rows (int, optional): Numero di righe da caricare per test. Se None, carica tutto il dataset.
            
        Returns:
            tuple: (data, grouped, references_grouped, allegati_grouped, text_articles, text_allegati)
        """
        # Caricamento dei dati
        data = pd.read_csv(dataset_path, sep=",", encoding="utf-8")
        if test_rows:
            data = data.head(test_rows)
        
        # Filtra i dati per i commi (esclude allegati e riferimenti)
        data_filtered = data[(data["Comma"].notna()) & (pd.isna(data["Allegato"]))]
        
        # Raggruppa i dati per Decreto e Articolo
        grouped = data_filtered.groupby(["Decreto", "Articolo"])
        
        # Raggruppa i riferimenti
        references_grouped = data[(data["Comma"].isna()) & (pd.isna(data["Allegato"]))].groupby(["Decreto", "Articolo"])
        
        # Raggruppa gli allegati
        allegati_grouped = data[pd.notna(data["Allegato"])].groupby(["Decreto", "Allegato"])
        
        # Salva i vari articoli completi
        text_articles = {}
        for (decreto, articolo), group in grouped:
            sorted_group = group.sort_values(by="Comma")
            testo_contenuto = " ".join(sorted_group["Testo_Contenuto"].tolist())
            text_articles[(decreto, articolo)] = testo_contenuto
        
        # Salva i vari allegati completi
        text_allegati = {}
        for (decreto, allegato), group in allegati_grouped:
            testo_contenuto = " ".join(group["Testo_Contenuto"].tolist())
            text_allegati[(decreto, allegato)] = testo_contenuto
        
        return data, grouped, references_grouped, allegati_grouped, text_articles, text_allegati
    
    def load_correttivo_dataset(self, dataset_path):
        """
        Carica il dataset dei correttivi.
        
        Args:
            dataset_path (str): Percorso del file CSV dei correttivi
            
        Returns:
            pd.DataFrame: DataFrame contenente i correttivi
        """
        return pd.read_csv(dataset_path, sep=",", encoding="utf-8")
    
    def split_with_spacy(self, text):
        """
        Suddivide il testo in frasi utilizzando spaCy.
        
        Args:
            text (str): Testo da suddividere
            
        Returns:
            list: Lista di frasi
        """
        if self.nlp is None:
            # Fallback se spaCy non è disponibile
            return [s.strip() for s in text.split(".") if s.strip()]
        
        doc = self.nlp(text)
        return [sent.text.strip() for sent in doc.sents]
    
    def merge_short_chunks(self, chunks, min_length=45):
        """
        Unisce i chunks troppo corti.
        
        Args:
            chunks (list): Lista di chunks
            min_length (int): Lunghezza minima per un chunk
            
        Returns:
            list: Lista di chunks uniti
        """
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
    
    def construct_prompt(self, article, references, chunk):
        """
        Costruisce il prompt per la generazione del contesto.
        
        Args:
            article (str): Testo dell'articolo completo
            references (str): Riferimenti a correttivi o altri articoli
            chunk (str): Chunk di testo per cui generare il contesto
            
        Returns:
            str: Prompt formattato
        """
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
        
        Nota che il testo è diretto, senza frasi iniziali o commenti.  
        
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
            SPECIFIC_ARTICLE=article,
            REFERENCES=references,
            CHUNK=chunk
        )
    
    def generate_with_llm(self, user_prompt, return_thinking=False):
        """
        Genera testo utilizzando LLM.
        
        Args:
            user_prompt (str): Prompt utente
            return_thinking (bool): Se True, restituisce anche il processo di pensiero
            
        Returns:
            str or tuple: Se return_thinking=False, restituisce solo la risposta.
                         Se return_thinking=True, restituisce (thinking_content, content)
        """
        try:
            # Prepara il prompt
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Applica il template di chat
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=True
            )
            
            # Prepara gli input del modello
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
            
            # Genera il testo
            generated_ids = self.model.generate(
                **model_inputs,
                **self.gen_config
            )
            
            # Estrai gli output
            output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
            
            # Parsing del contenuto
            try:
                # Trova l'indice del tag </think>
                index = len(output_ids) - output_ids[::-1].index(151668)
            except ValueError:
                index = 0
            
            # Decodifica il contenuto
            thinking_content = self.tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
            content = self.tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
            
            if return_thinking:
                return thinking_content, content
            else:
                return content
                
        except Exception as e:
            print(f"Errore durante la generazione: {e}")
            if return_thinking:
                return "", "Non è stato possibile generare una risposta."
            return "Non è stato possibile generare una risposta."
    
    def generate_with_pipeline(self, user_prompt):
        """
        Genera testo utilizzando pipeline (legacy).
        
        Args:
            user_prompt (str): Prompt utente
            
        Returns:
            str: Testo generato
        """
        try:
            from transformers import pipeline
            
            # Crea la pipeline di generazione del testo
            if not hasattr(self, 'text_pipeline'):
                # Assicurati che il dispositivo sia impostato correttamente
                device_map = "auto" if self.device == "cuda" else "cpu"
                print(f"Utilizzo dispositivo: {device_map}")
                
                self.text_pipeline = pipeline(
                    "text-generation", 
                    model=self.model_name, 
                    tokenizer=self.tokenizer,
                    device_map=device_map
                )
            
            # Prepara il prompt
            chat_formatted_template = self.tokenizer.apply_chat_template([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ], tokenize=False, add_generation_prompt=True)
            
            # Genera il testo
            outputs = self.text_pipeline(
                chat_formatted_template,
                max_new_tokens=self.gen_config["max_new_tokens"],
                min_new_tokens=self.gen_config["min_new_tokens"],
                do_sample=self.gen_config["do_sample"],
                temperature=self.gen_config["temperature"],
                top_k=self.gen_config["top_k"],
                num_return_sequences=self.gen_config["num_return_sequences"]
            )
            
            # Estrai il testo generato
            generated_text = outputs[0]["generated_text"]
            
            # Rimuovi il prompt originale dal testo generato
            if chat_formatted_template in generated_text:
                generated_text = generated_text.replace(chat_formatted_template, "").strip()
            
            return generated_text
        except Exception as e:
            print(f"Errore durante la generazione del testo: {e}")
            return "Non è stato possibile generare il testo richiesto."
    
    def normalize_articolo(self, articolo):
        """
        Normalizza l'articolo, estraendo la parte numerativa se contiene il prefisso 'ALLEGATO'.
        
        Args:
            articolo (str): Articolo da normalizzare
            
        Returns:
            str: Articolo normalizzato
        """
        if isinstance(articolo, str) and articolo.upper().startswith("ALLEGATO"):
            # Estrai tutto ciò che segue "ALLEGATO" e rimuovi eventuali spazi
            return articolo.split("ALLEGATO", 1)[-1].strip()
        return str(articolo)
    
    def generate_context_for_chunks(self, text_articles):
        """
        Genera contesti per chunks di articoli.
        
        Args:
            text_articles (dict): Dizionario contenente i testi degli articoli, indicizzati per (decreto, articolo)
            
        Returns:
            list: Lista di dizionari con i chunks generati e i loro contesti
        """
        generated_chunks = []
        
        for key, value in text_articles.items():
            # Splitta il testo in chunks
            chunks = self.split_with_spacy(value)
            
            # Unisci i chunks troppo corti
            merged_chunks = self.merge_short_chunks(chunks, min_length=45)
            
            for chunk in merged_chunks:
                input_prompt = self.construct_prompt(value, "", chunk)
                
                # Genera il contesto
                if self.use_llm:
                    gen_ctx = self.generate_with_llm(input_prompt)
                else:
                    gen_ctx = self.generate_with_pipeline(input_prompt)
                
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
    
    def generate_context_with_commas(self, grouped_commas, grouped_allegati, references_grouped, text_articles, text_allegati):
        """
        Genera contesti per commi di articoli.
        
        Args:
            grouped_commas (DataFrameGroupBy): Articoli raggruppati per Decreto e Articolo
            grouped_allegati (DataFrameGroupBy): Allegati raggruppati per Decreto e Allegato
            references_grouped (DataFrameGroupBy): Riferimenti raggruppati per Decreto e Articolo
            text_articles (dict): Dizionario contenente i testi degli articoli
            text_allegati (dict): Dizionario contenente i testi degli allegati
            
        Returns:
            list: Lista di dizionari con i chunks generati e i loro contesti
        """
        generated_chunks = []
        i = 1
        
        # Processa gli articoli
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
                
                # Riferimenti esterni
                references_content = []
                
                if (decreto, articolo) in references_grouped.groups:
                    reference_group = references_grouped.get_group((decreto, articolo))
                    
                    for _, ref_row in reference_group.iterrows():
                        riferimento = ref_row["Riferimento"].removesuffix(".txt")
                        testo_riferimento = ref_row["Testo_Contenuto"]
                        
                        if riferimento in chunk:
                            references_content.append(f"Riferimento a {riferimento}:\n  {testo_riferimento}\n\n")
                
                # Riferimenti interni
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
                            elif word[0].lower() in ["allegato", "allegati"]:
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
                input_prompt = self.construct_prompt(article_text, references_content, chunk)
                
                # Genera il contesto
                if self.use_llm:
                    gen_ctx = self.generate_with_llm(input_prompt)
                else:
                    gen_ctx = self.generate_with_pipeline(input_prompt)
                
                # Aggiungi il risultato alla lista dei chunks generati
                generated_chunks.append({
                    "id": i,
                    "decree": decreto,
                    "article": articolo,
                    "chunk": chunk,
                    "context_generated": gen_ctx,
                    "article_title": titolo_articolo_associato,
                    "titolo_allegato": None,
                    "allegato": None
                })
                i += 1
        
        # Processa gli allegati
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
                
                # Riferimenti interni
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
                            elif word[0].lower() in ["allegato", "allegati"]:
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
                input_prompt = self.construct_prompt(allegato_text, references_content, chunk)
                
                # Genera il contesto
                if self.use_llm:
                    gen_ctx = self.generate_with_llm(input_prompt)
                else:
                    gen_ctx = self.generate_with_pipeline(input_prompt)
                
                # Aggiungi il risultato alla lista dei chunks generati
                generated_chunks.append({
                    "id": i,
                    "decree": decreto,
                    "article": articolo_associato,
                    "chunk": chunk,
                    "context_generated": gen_ctx,
                    "article_title": titolo_articolo_associato,
                    "titolo_allegato": titolo_allegato_associato,
                    "allegato": allegato_associato
                })
                i += 1
        
        return generated_chunks
    
    def generate_context_with_commas_and_correttivo(self, grouped_commas, references_grouped, text_articles, dataset_correttivo, grouped_allegati, text_allegati):
        """
        Genera contesti per commi di articoli, includendo i correttivi.
        
        Args:
            grouped_commas (DataFrameGroupBy): Articoli raggruppati per Decreto e Articolo
            references_grouped (DataFrameGroupBy): Riferimenti raggruppati per Decreto e Articolo
            text_articles (dict): Dizionario contenente i testi degli articoli
            dataset_correttivo (pd.DataFrame): DataFrame contenente i correttivi
            grouped_allegati (DataFrameGroupBy): Allegati raggruppati per Decreto e Allegato
            text_allegati (dict): Dizionario contenente i testi degli allegati
            
        Returns:
            list: Lista di dizionari con i chunks generati e i loro contesti
        """
        generated_chunks = []
        i = 1
        
        # Processa gli articoli
        for (decreto, articolo), group in grouped_commas:
            article_text = text_articles.get((decreto, articolo), "")
            
            if not article_text:
                print(f"No text found for Decreto: {decreto}, Articolo: {articolo}. Skipping.")
                continue
            
            for chunk in group["Testo_Contenuto"]:
                references_content = []
                
                # Cerca correttivi per l'articolo
                articolo_normalizzato = self.normalize_articolo(articolo)
                articolo_rows = dataset_correttivo[dataset_correttivo['article_reference'].apply(self.normalize_articolo) == articolo_normalizzato]
                
                # Estrai Testo_Contenuto per ogni riga
                for _, row in articolo_rows.iterrows():
                    testo_contenuto = row['Testo_Contenuto']
                    references_content.append(f"Riferimento a articolo {articolo} del codice correttivo:\n {testo_contenuto}\n\n")
                
                # Riferimenti interni
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
                            elif word[0].lower() in ["allegato", "allegati"]:
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
                input_prompt = self.construct_prompt(article_text, references_content, chunk)
                
                # Genera il contesto
                if self.use_llm:
                    gen_ctx = self.generate_with_llm(input_prompt)
                else:
                    gen_ctx = self.generate_with_pipeline(input_prompt)
                
                # Aggiungi il risultato alla lista dei chunks generati
                generated_chunks.append({
                    "id": i,
                    "decree": decreto,
                    "article": articolo,
                    "chunk": chunk,
                    "context_generated": gen_ctx,
                    "article_title": group["titolo_art"]
                })
                i += 1
        
        # Processa gli allegati
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
                
                # Riferimenti interni
                references_content = []
                
                # Cerca correttivi per l'articolo
                articolo_normalizzato = self.normalize_articolo(articolo_associato)
                articolo_rows = dataset_correttivo[dataset_correttivo['article_reference'].apply(self.normalize_articolo) == articolo_normalizzato]
                
                # Estrai Testo_Contenuto per ogni riga
                for _, row in articolo_rows.iterrows():
                    testo_contenuto = row['Testo_Contenuto']
                    references_content.append(f"Riferimento a articolo {articolo_associato} del codice correttivo:\n {testo_contenuto}\n\n")
                
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
                            elif word[0].lower() in ["allegato", "allegati"]:
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
                input_prompt = self.construct_prompt(allegato_text, references_content, chunk)
                
                # Genera il contesto
                if self.use_llm:
                    gen_ctx = self.generate_with_llm(input_prompt)
                else:
                    gen_ctx = self.generate_with_pipeline(input_prompt)
                
                # Aggiungi il risultato alla lista dei chunks generati
                generated_chunks.append({
                    "id": i,
                    "decree": decreto,
                    "article": articolo_associato,
                    "chunk": chunk,
                    "context_generated": gen_ctx,
                    "article_title": titolo_articolo_associato,
                    "titolo_allegato": titolo_allegato_associato,
                    "allegato": allegato_associato
                })
                i += 1
        
        return generated_chunks
    
    def save_results(self, generated_chunks, output_file):
        """
        Salva i risultati in un file CSV.
        
        Args:
            generated_chunks (list): Lista di dizionari con i chunks generati e i loro contesti
            output_file (str): Nome del file di output
        """
        result_df = pd.DataFrame(generated_chunks)
        result_df.to_csv(output_file, sep=",", encoding="utf-8", index=False)
        print(f"Contextual chunks saved to {output_file}")


# Esempio di utilizzo
if __name__ == "__main__":
    # Inizializza il generatore di testo
    generator = TextGenerator(model_name="Qwen/Qwen2.5-1.5B-Instruct", use_llm=True)
    
    # Carica il dataset
    data, grouped, references_grouped, allegati_grouped, text_articles, text_allegati = generator.load_dataset("data_appalti_v5.csv", test_rows=100)
    
    # Carica il dataset dei correttivi
    dataset_correttivo = generator.load_correttivo_dataset("codice_appalti_correttivo.csv")
    
    # Genera contesti con commi e correttivi
    result = generator.generate_context_with_commas_and_correttivo(
        grouped, references_grouped, text_articles, dataset_correttivo, allegati_grouped, text_allegati
    )
    
    # Salva i risultati
    generator.save_results(result, "generatione_contesti_correttivi_v5.csv") 