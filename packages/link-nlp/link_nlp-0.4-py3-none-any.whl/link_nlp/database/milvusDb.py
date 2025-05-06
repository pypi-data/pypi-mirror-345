"""
This module provides an interface for interacting with the Milvus vector database for semantic search.
It contains classes for managing connections to the database, creating collections with different schemas,
and providing standard methods for inserting, querying, and managing vector-based data.
Classes:
    - MilvusConnectionManager: Handles connections to the Milvus server
    - BaseCollection: Abstract base class for all collection types
    - ContextCollection: Collection designed for contextual information 
    - ArticoliCollection: Collection designed for legal articles
    - CorrettivoCollection: Collection designed for legal amendments (correttivo)
    - CorrettivoContextCollection: Collection for contextual information related to amendments
"""

from pymilvus import connections, utility, Collection, CollectionSchema, FieldSchema, DataType
from transformers import AutoModel
from milvus import default_server
import pandas as pd
import logging
import torch
import re
import json

logging.basicConfig(
    format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO
)

logger = logging.getLogger(__name__)

logger.info("Caricamento del modello di embedding...")
embedder_model = AutoModel.from_pretrained("jinaai/jina-embeddings-v3", trust_remote_code=True, use_flash_attn=False).cuda()
logger.info("Caricamento completato")

def get_qa_test_from_jsonl(file_path):
    lista_elementi = []

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            elemento = json.loads(line)
            lista_elementi.append(elemento)
    return lista_elementi


context_generated_genie = get_qa_test_from_jsonl("legal_genie_cod_app.jsonl")

dframe = pd.DataFrame(context_generated_genie)

def extract_article(title):
    
    # Cerca "ALLEGATO I.11", "ALLEGATO II.2", "ALLEGATO V2", "ALLEGATO X"
    match = re.search(r"(ALLEGATO [IVXLCDM\d]+\.*\d*)", title)  
    if match:
        return match.group(1)
    
    # Cerca "Art. 12"
    match = re.search(r"Art\. (\d+)", title)
    if match:
        return match.group(1)
    
    return ""

# Applica la funzione alla colonna article_title
dframe["article"] = dframe["article_title"].apply(extract_article)


dim = 1024

field_schemas = {
    "articoli": [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
        FieldSchema(name="article", dtype=DataType.INT64),
        FieldSchema(name="chunk_id", dtype=DataType.INT64),
        FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="article_title",dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="allegato",dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="titolo_allegato",dtype=DataType.VARCHAR, max_length=512),        
        FieldSchema(name="chunk", dtype=DataType.VARCHAR, max_length=55000)
    ],
    "context": [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
        FieldSchema(name="article", dtype=DataType.INT64),
        FieldSchema(name="chunk_id", dtype=DataType.INT64),
        FieldSchema(name="context_generated", dtype=DataType.VARCHAR, max_length=4096),
        FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="article_title",dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="allegato",dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="titolo_allegato",dtype=DataType.VARCHAR, max_length=512),        
        FieldSchema(name="chunk", dtype=DataType.VARCHAR, max_length=55000)
    ],
    "correttivo": [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
        FieldSchema(name="article", dtype=DataType.INT64),
        FieldSchema(name="comma", dtype=DataType.FLOAT),
        FieldSchema(name="rel_type", dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="article_reference", dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="Testo_Contenuto", dtype=DataType.VARCHAR, max_length=10000)
    ],
    "context_correttivo": [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
        FieldSchema(name="chunk_id", dtype=DataType.INT64),
        FieldSchema(name="article", dtype=DataType.INT64),
        FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="context_generated", dtype=DataType.VARCHAR, max_length=10000),
        FieldSchema(name="article_title",dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="allegato",dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="titolo_allegato",dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="chunk", dtype=DataType.VARCHAR, max_length=55000)
    ],
}

### FUNZIONI GENERALI

def embed_texts(texts, batch_size=1):

    if isinstance(texts, str):
        texts = [texts]

    embeddings = []

    # Suddividi i testi in batch
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        with torch.no_grad():
            batch_embeddings = embedder_model.encode(
                sentences=batch,
                device="cuda",
                normalize_embeddings=True,
                task="retrieval.passage",
            )

        # Aggiungi gli embedding del batch alla lista principale
        embeddings.extend(batch_embeddings)

    return embeddings

def chunk_text(text, max_length=1000):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

### ELIMINAZIONE COLLECTIONS

def drop_all_collections():
    try:
        MilvusConnectionManager.get_connection()
        # Ottieni l'elenco di tutte le collezioni
        collections = utility.list_collections()
        if collections:
            for collection in collections:
                # Droppa ogni collezione
                utility.drop_collection(collection)
                print(f"La collezione '{collection}' è stata droppata con successo.")
        else:
            print("Non ci sono collezioni da droppare.")
    except Exception as e:
        print(f"Errore durante il drop delle collezioni: {e}")

def drop_collection_by_name(collection_name):
    try:
        MilvusConnectionManager.get_connection()
        # Verifica se la collezione esiste
        if utility.has_collection(collection_name):
            # Droppa la collezione
            utility.drop_collection(collection_name)
            print(f"La collezione '{collection_name}' è stata droppata con successo.")
        else:
            print(f"La collezione '{collection_name}' non esiste.")
    except Exception as e:
        print(f"Errore durante il drop della collezione '{collection_name}': {e}")

### CREAZIONE TABELLA ASSOCIAZIONI ARTICOLI VECCHI CON ARTICOLI CORRETTIVO

def create_association_table(collection_old, collection_new):
    """
    Crea una tabella di associazione tra due collezioni Milvus.
    Restituisce una lista di dizionari con id associati.
    """
    association_list = []

    # Estrarre i dati da collection_new
    new_entities = collection_new.query(
        expr="id >= 0",  # Puoi usare un'espressione di query se necessario
        output_fields=["id", "article_reference"],
        limit = 16383
    )

    # Estrarre i dati da collection_old
    old_entities = collection_old.query(
        expr="id >= 0",  # Puoi usare un'espressione di query se necessario
        output_fields=["id", "article"],
        limit = 16383
    )

    article_to_old_id = {str(entity['article']).strip().lower(): entity['id'] for entity in old_entities}
    
    for new_entity in new_entities:
        new_id = new_entity['id']
        article_reference = new_entity['article_reference']
        old_id = article_to_old_id.get(article_reference)
        if old_id is not None:
            association_list.append({"articolo_id": old_id,"correttivo_id": new_id})

    return association_list

### CLASSI PRINCIPALI PER MANIPOLAZIONE DB MILVUS

class MilvusConnectionManager:
    _connection = None

    @staticmethod
    def get_connection(alias="default", host="127.0.0.1", port="19530",first_attempt = False):
        """
        Ritorna una connessione aperta a Milvus. Se non esiste, la crea.
        """
        if not connections.has_connection(alias):
            if(first_attempt):
                default_server.start()
            connections.connect(alias, host=host, port=port)
            logger.info(f"Connessione a Milvus aperta con alias '{alias}'.")

    @staticmethod
    def close_connection(alias="default"):
        """
        Chiude la connessione a Milvus.
        """
        if connections.has_connection(alias):
            connections.disconnect(alias)
            logger.info(f"Connessione a Milvus chiusa con alias '{alias}'.")

class BaseCollection:
    
    def prepare_data(self,df):
        """
        Prepara gli embedding e i metadati da un DataFrame.
        """
        raise NotImplementedError("La funzione prepare_data deve essere implementata nelle classi derivate.")

    def insert_data(self, collection, data, batch_size=1000):
        """
        Funzione per inserire i dati nella collezione in batch per ridurre il consumo di memoria.
        """
        total_inserted = 0

        # Inserimento a batch
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            _ = collection.insert(batch)
            total_inserted += len(batch)

            # Flush per scrivere i dati su disco
            collection.flush()

        return total_inserted   
    
    def create_collection(self,name,fields):
        """
        Crea una collezione Milvus con il nome e schema specificati.
        """

        if utility.has_collection(name):
            logger.info(f"La collezione '{name}' esiste già. Droppandola...")
            utility.drop_collection(name)
        
        schema = CollectionSchema(fields, description="Schema per Codice Appalti")
        collection = Collection(name=name, schema=schema)
        ("CREATA COLLEZIONE COME SCHEMA")
        return collection

    def get_collection(self,collection_name,fields,csv_path):
        try:
            MilvusConnectionManager.get_connection()

            if utility.has_collection(collection_name):
                collection = Collection(name=collection_name)
                collection.load()

                logger.info(f"La collezione '{collection_name}' esiste già e è stata recuperata.")
                df = None
                index_params = None
                
            else:
                # Crea la collezione se non esiste                
                collection = self.create_collection(collection_name,fields)
                logger.info(f"La collezione '{collection_name}' è stata creata con successo.")

                # Caricamento dati dal CSV e preparazione
                logger.info(f"Caricamento dati da {csv_path}...")
                df = pd.read_csv(csv_path, sep=",", encoding="utf-8")
                
                # Creazione di un indice
                logger.info("Creazione dell'indice...")
                index_params = {
                    "index_type": "IVF_FLAT",
                    "metric_type": "IP",
                    "params": {"nlist": 128}
                }

            return df,index_params,collection
        
        except Exception as e:
            logger.error(f"Errore durante la creazione o il popolamento della collezione: {e}")
            return None

class ContextCollection(BaseCollection):
    
    def prepare_data(self,df):
        """
        Prepara gli embedding e i metadati da un DataFrame.
        """
        texts = df["chunk"].tolist()
        
        # texts_with_generations = [
        # f"{row['chunk']}\n{row['context_generated']}" if not pd.isna(row['context_generated']) else row['chunk']
        # for _, row in df.iterrows()
        # ]
        
        texts_with_generations = [
        f"{row['context_generated']}" if not pd.isna(row['context_generated']) else row['chunk']
        for _, row in df.iterrows()
        ]
        
        metadata_list = []
        for _, row in df.iterrows():
            
            article = row['article']
            if isinstance(article, str):
                article_num = 0
                
            else:
                article_num = int(article)
            
            metadata = {
                "source": "Codice Appalti D.Lgs. 36/2023",
                "article": article_num, 
                "chunk_id": row['id'],
                "context_generated": str(row['context_generated']) if not pd.isna(row['context_generated']) else '',
                "article_title": str(row['article_title']) if not pd.isna(row['article_title']) else "",
                "allegato": str(row['allegato']) if not pd.isna(row['allegato']) else "",
                "titolo_allegato": str(row['titolo_allegato']) if not pd.isna(row['titolo_allegato']) else ""
            }
            metadata_list.append(metadata)
        return texts,texts_with_generations,metadata_list
    
    def insert_data(self,collection, embeddings, metadata_list, chunks):
        """
        Inserisce i dati nella collezione per il tipo 'context'.
        """
        # Crea gli ID univoci
        ids = [i for i in range(len(embeddings))]

        # Prepara i dati specifici per 'context'
        data = [
            ids,                      
            embeddings,        
            [meta["article"] for meta in metadata_list],  
            [meta["chunk_id"] for meta in metadata_list], 
            [meta.get("context_generated", "") for meta in metadata_list], 
            [meta["source"] for meta in metadata_list],
            [meta["article_title"] for meta in metadata_list],
            [meta["allegato"] for meta in metadata_list],
            [meta["titolo_allegato"] for meta in metadata_list],
            chunks
        ]
        
        # Passa i dati alla funzione madre per l'inserimento
        super().insert_data(collection, data)

    def create_collection(self,name, fields):
        return super().create_collection(name,fields)
    
    def get_collection(self,collection_name,csv_path):
                
        try:
            
            MilvusConnectionManager.get_connection()

            df,index_params,collection = super().get_collection(collection_name,field_schemas["context"],csv_path)
            
            if df is None or index_params is None:
                return collection
            
            chunks,chunks_with_generations, metadata_list = self.prepare_data(df)

            logger.info("Calcolo degli embedding...")
            embeddings = embed_texts(chunks_with_generations)

            logger.info("Inserimento dati nella collezione...")
            self.insert_data(collection, embeddings, metadata_list, chunks)

            collection.create_index(field_name="embedding", index_params=index_params)
            collection.load()
            logger.info("Inserimento e indicizzazione completati con successo.")
            
            return collection
            
        except Exception as e:
            logger.error(f"Errore durante la creazione o il popolamento della collezione: {e}")
            return None         

class ArticoliCollection(BaseCollection):
    
    def prepare_data(self,df):
        """
        Prepara gli embedding e i metadati da un DataFrame.
        """
        texts = df["Testo_Contenuto"].tolist()
        
        metadata_list = []
        for _, row in df.iterrows():
            
            article = row['Articolo']
            if isinstance(article, str):
                print(article)
                article_num = 0
            else:
                article_num = int(article)

            metadata = {
                "source": "Codice Appalti D.Lgs. 36/2023",
                "article": article_num, 
                "chunk_id": row['id'],
                "article_title": str(row['titolo_art']) if not pd.isna(row['titolo_art']) else "",
                "allegato": str(row['Allegato']) if not pd.isna(row['Allegato']) else "",
                "titolo_allegato": str(row['TitoloAllegato']) if not pd.isna(row['TitoloAllegato']) else ""
            }
            metadata_list.append(metadata)
        return texts,metadata_list
    
    def insert_data(self, collection, embeddings, metadata_list, chunks):
        """
        Inserisce i dati nella collezione per il tipo 'articles'.
        """

        ids = [i for i in range(len(embeddings))]

        # Prepara i dati per l'inserimento
        data = [
            ids,                          # Colonna 1: ID
            embeddings,          # Colonna 2: Embeddings
            [meta["article"] for meta in metadata_list],  # Colonna 3: Metadati articolo
            [meta["chunk_id"] for meta in metadata_list],       # Colonna 4: Metadati chunk ID
            [meta["source"] for meta in metadata_list],  # Colonna 5: Fonte
            [meta["article_title"] for meta in metadata_list],
            [meta["allegato"] for meta in metadata_list],
            [meta["titolo_allegato"] for meta in metadata_list],
            chunks
        ]
    
        # Passa i dati alla funzione madre per l'inserimento
        super().insert_data(collection, data)
    
    def create_collection(self,name, fields):
        return super().create_collection(name,fields)
    
    def get_collection(self,collection_name,csv_path):
        try:
            MilvusConnectionManager.get_connection()
            df,index_params,collection = super().get_collection(collection_name,field_schemas["articoli"],csv_path)

            if df is None or index_params is None:
                return collection

            # Prepara i dati (testi e metadati)
            texts, metadata_list = self.prepare_data(df)

            # Calcolo degli embedding
            logger.info("Calcolo degli embedding...")
            embeddings = embed_texts(texts)

            # Inserimento dati nella collezione
            logger.info("Inserimento dati nella collezione...")
            self.insert_data(collection, embeddings, metadata_list, texts)
        
        
            collection.create_index(field_name="embedding", index_params=index_params)
            collection.load()
            logger.info("Inserimento e indicizzazione completati con successo.")

            return collection
        
        except Exception as e:
            logger.error(f"Errore durante la creazione o il popolamento della collezione: {e}")
            return None
    
class CorrettivoCollection(BaseCollection):
    
    def prepare_data(self,df):
        """
        Prepara gli embedding e i metadati da un DataFrame, troncando e dividendo testi troppo lunghi.
        """
        texts = []  
        metadata_list = []
        id_counter = 0 

        for _, row in df.iterrows():
            if len(row['Testo_Contenuto']) > 1000:
                chunks = chunk_text(row['Testo_Contenuto'])
                for chunk in chunks:
                    metadata = {
                        "source": "Correttivo Codice Appalti D.Lgs. 36/2023",
                        "article": row['Articolo'],
                        "comma": row['Comma'],
                        "rel_type": str(row['rel_type']),
                        "article_reference": row['article_reference'],
                    }
                    texts.append(chunk)
                    metadata_list.append(metadata)
                    id_counter += 1  
            else:
                texts.append(row['Testo_Contenuto'])
                metadata = {
                    "source": "Correttivo Codice Appalti D.Lgs. 36/2023",
                    "article": row['Articolo'],
                    "comma": row['Comma'],
                    "rel_type": str(row['rel_type']),
                    "article_reference": row['article_reference'],
                }
                metadata_list.append(metadata)
                id_counter += 1

        return texts, metadata_list  
    
    def insert_data(self, collection, embeddings, metadata_list, texts):
        """
        Inserisce i dati nella collezione per il tipo 'correttivo'.
        """
        # Associa ID univoci a ogni embedding
        ids = [i for i in range(len(embeddings))]

        # Prepara i dati per l'inserimento
        data = [
            ids,                          # Colonna 1: ID
            embeddings,          # Colonna 2: Embeddings
            [meta["article"] for meta in metadata_list],  # Colonna 3: Metadati articolo
            [meta["comma"] for meta in metadata_list],       # Colonna 4: Metadati comma
            [meta["rel_type"] for meta in metadata_list],  # Colonna 5: Metadati tipo relazione
            [meta["article_reference"] for meta in metadata_list],  # Colonna 5: Metadati articolo riferito
            [meta["source"] for meta in metadata_list],  # Colonna 6: Fonte
            texts
        ]
        
        # Passa i dati alla funzione madre per l'inserimento
        super().insert_data(collection, data)

    def create_collection(self,name, fields):
        return super().create_collection(name,fields)
    
    def get_collection(self,collection_name,csv_path):
        
        try:
            MilvusConnectionManager.get_connection()
            df,index_params,collection = super().get_collection(collection_name,field_schemas["correttivo"],csv_path)    
            
            if df is None or index_params is None:
                return collection
            
            logger.info("preparazione dati...")
            texts, metadata_list = self.prepare_data(df)

            logger.info("Calcolo degli embedding...")
            embeddings = embed_texts(texts)

            logger.info("Inserimento dati nella collezione...")
            self.insert_data(collection, embeddings, metadata_list, texts)
            
            collection.create_index(field_name="embedding", index_params=index_params)
            collection.load()
            logger.info("Inserimento e indicizzazione completati con successo.")

            return collection
        
        except Exception as e:
            logger.error(f"Errore durante la creazione o il popolamento della collezione: {e}")
            return None

class CorrettivoContextCollection(BaseCollection):
    
    def prepare_data(self, df):
        """
        Prepara gli embedding e i metadati da un DataFrame.
        """        
        # Testi da embedare
        texts = df["chunk"].tolist()
        
        # Combina chunk con contesto generato (se presente)
        texts_with_generations = [
            f"{row['chunk']}\n{row['context_generated']}" if not pd.isna(row['context_generated']) else row['chunk']
            for _, row in df.iterrows()
        ]
        
        metadata_list = []

        # Creazione dei metadati
        for _, row in df.iterrows():
            article = row['article']
            if isinstance(article, str):
                article_num = 0
            else:
                article_num = int(article)

            metadata = {
                "source": "Codice Appalti D.Lgs. 36/2023",
                "article": article_num,
                "chunk_id": row['id'],
                "context_generated": str(row['context_generated']),
                "article_title": str(row['article_title']) if not pd.isna(row['article_title']) else "",
                "allegato": str(row['allegato']) if not pd.isna(row['allegato']) else "",
                "titolo_allegato": str(row['titolo_allegato']) if not pd.isna(row['titolo_allegato']) else ""
            }
            metadata_list.append(metadata)
        
        return texts, texts_with_generations, metadata_list
    
    def insert_data(self, collection, embeddings, metadata_list, texts):
        """
        Inserisce i dati nella collezione per il tipo 'correttivo'.
        """
        # Associa ID univoci a ogni embedding
        ids = [i for i in range(len(embeddings))]

        # Prepara i dati per l'inserimento
        data = [
            ids, 
            embeddings, 
            [meta["chunk_id"] for meta in metadata_list],
            [meta["article"] for meta in metadata_list],
            [meta["source"] for meta in metadata_list],
            [meta.get("context_generated", "") for meta in metadata_list],
            [meta["article_title"] for meta in metadata_list],
            [meta["allegato"] for meta in metadata_list],
            [meta["titolo_allegato"] for meta in metadata_list],
            texts
        ]
        
        # Passa i dati alla funzione madre per l'inserimento
        super().insert_data(collection, data)

    def create_collection(self,name, fields):
        return super().create_collection(name,fields)
    
    def get_collection(self,collection_name,csv_path):
        
        try:
            MilvusConnectionManager.get_connection()
            df,index_params,collection = super().get_collection(collection_name,field_schemas["context_correttivo"],csv_path)    
            
            if df is None or index_params is None:
                return collection
            
            logger.info("preparazione dati...")
            chunks,chunks_with_generations, metadata_list = self.prepare_data(df)
            
            logger.info("Calcolo degli embedding...")
            embeddings = embed_texts(chunks_with_generations)

            logger.info("Inserimento dati nella collezione...")
            self.insert_data(collection, embeddings, metadata_list, chunks)
            
            collection.create_index(field_name="embedding", index_params=index_params)
            collection.load()
            logger.info("Inserimento e indicizzazione completati con successo.")

            return collection
        
        except Exception as e:
            logger.error(f"Errore durante la creazione o il popolamento della collezione: {e}")
            return None
