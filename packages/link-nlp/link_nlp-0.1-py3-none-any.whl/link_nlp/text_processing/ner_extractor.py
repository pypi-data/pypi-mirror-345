from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline
import argparse
import json
import sys
import re

class NERExtractorBase(ABC):
    """Classe base astratta per l'estrazione NER."""
    
    @abstractmethod
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Estrae le entità dal testo."""
        pass
    
    @abstractmethod
    def find_custom_entities(self, text: str, entities_to_find: List[str]) -> Dict[str, List[str]]:
        """Cerca entità specifiche nel testo."""
        pass
    
    def extract_all(self, text: str, custom_entities: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """
        Estrae tutte le entità dal testo, incluse quelle personalizzate se specificate.
        
        Args:
            text (str): Il testo da analizzare
            custom_entities (List[str], optional): Lista di entità personalizzate da cercare
            
        Returns:
            Dict[str, List[str]]: Dizionario con le entità estratte
        """
        # Estrai le entità standard
        results = self.extract_entities(text)
        
        # Se sono specificate entità personalizzate, cerca anche quelle
        if custom_entities:
            custom_results = self.find_custom_entities(text, custom_entities)
            # Aggiungi i risultati personalizzati a quelli standard
            for entity_type, entities in custom_results.items():
                if entity_type in results:
                    results[entity_type].extend(entities)
                else:
                    results[entity_type] = entities
        
        return results

class GLiNERExtractor(NERExtractorBase):
    """Implementazione dell'estrattore NER usando GLiNER."""
    
    def __init__(self):
        print("Inizializzazione di GLiNER (simulazione)")
        # Qui andrebbe l'inizializzazione reale di GLiNER
        # Per ora simuliamo il comportamento
        
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        print(f"Estrazione entità con GLiNER dal testo: {text[:50]}...")
        
        # Implementazione di base che estrae alcuni pattern comuni
        entities = {
            "ARTICOLO": [],
            "DECRETO": [],
            "ANNO": [],
            "ALLEGATO": []
        }
        
        # Estrai articoli (es. "articolo 15")
        articoli = re.findall(r'articolo\s+(\d+)', text, re.IGNORECASE)
        if articoli:
            entities["ARTICOLO"] = [f"articolo {a}" for a in articoli]
        
        # Estrai decreti (es. "decreto legislativo 36/2023")
        decreti = re.findall(r'decreto\s+legislativo\s+(\d+)', text, re.IGNORECASE)
        if decreti:
            entities["DECRETO"] = [f"decreto legislativo {d}" for d in decreti]
        
        # Estrai anni (es. "2023")
        anni = re.findall(r'\b(19|20)\d{2}\b', text)
        if anni:
            entities["ANNO"] = anni
        
        # Estrai allegati (es. "allegato I")
        allegati = re.findall(r'allegato\s+([IVX]+)', text, re.IGNORECASE)
        if allegati:
            entities["ALLEGATO"] = [f"allegato {a}" for a in allegati]
        
        # Rimuovi le chiavi vuote
        entities = {k: v for k, v in entities.items() if v}
        
        print(f"Entità estratte: {entities}")
        return entities
    
    def find_custom_entities(self, text: str, entities_to_find: List[str]) -> Dict[str, List[str]]:
        """
        Cerca entità specifiche nel testo.
        
        Args:
            text (str): Il testo da analizzare
            entities_to_find (List[str]): Lista di entità da cercare
            
        Returns:
            Dict[str, List[str]]: Dizionario con le entità trovate
        """
        print(f"Ricerca di entità personalizzate: {entities_to_find}")
        
        results = {"CUSTOM": []}
        
        for entity in entities_to_find:
            # Cerca l'entità nel testo (case insensitive)
            matches = re.findall(rf'\b{re.escape(entity)}\b', text, re.IGNORECASE)
            if matches:
                results["CUSTOM"].extend(matches)
        
        # Rimuovi le chiavi vuote
        results = {k: v for k, v in results.items() if v}
        
        print(f"Entità personalizzate trovate: {results}")
        return results

class TransformersExtractor(NERExtractorBase):
    """Implementazione dell'estrattore NER usando modelli Hugging Face."""
    
    def __init__(self, model_name: str):
        print(f"Inizializzazione di Transformers con modello: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)
        self.pipe = pipeline("ner", model=self.model, tokenizer=self.tokenizer)
        
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        print(f"Estrazione entità con Transformers dal testo: {text[:50]}...")
        results = self.pipe(text)
        entities = {}
        for result in results:
            label = result['entity']
            if label not in entities:
                entities[label] = []
            entities[label].append(result['word'])
        print(f"Entità estratte: {entities}")
        return entities
    
    def find_custom_entities(self, text: str, entities_to_find: List[str]) -> Dict[str, List[str]]:
        """
        Cerca entità specifiche nel testo.
        
        Args:
            text (str): Il testo da analizzare
            entities_to_find (List[str]): Lista di entità da cercare
            
        Returns:
            Dict[str, List[str]]: Dizionario con le entità trovate
        """
        print(f"Ricerca di entità personalizzate: {entities_to_find}")
        
        results = {"CUSTOM": []}
        
        for entity in entities_to_find:
            # Cerca l'entità nel testo (case insensitive)
            matches = re.findall(rf'\b{re.escape(entity)}\b', text, re.IGNORECASE)
            if matches:
                results["CUSTOM"].extend(matches)
        
        # Rimuovi le chiavi vuote
        results = {k: v for k, v in results.items() if v}
        
        print(f"Entità personalizzate trovate: {results}")
        return results

def create_ner_extractor(model_name: str) -> NERExtractorBase:
    """
    Factory function per creare l'estrattore NER appropriato.
    
    Args:
        model_name (str): Nome del modello da utilizzare
        
    Returns:
        NERExtractorBase: Un'istanza dell'estrattore NER appropriato
    """
    print(f"Creazione estrattore NER per modello: {model_name}")
    if model_name.lower() == "gliner":
        return GLiNERExtractor()
    else:
        # Per default, assume che sia un modello Hugging Face
        return TransformersExtractor(model_name)

def main():
    """Funzione principale per l'interfaccia a riga di comando."""
    parser = argparse.ArgumentParser(description="Estrai entità da un testo usando diversi modelli NER")
    parser.add_argument("--model", type=str, default="gliner",
                      help="Modello NER da utilizzare (gliner o nome modello Hugging Face)")
    parser.add_argument("--text", type=str, help="Testo da analizzare")
    parser.add_argument("--file", type=str, help="File contenente il testo da analizzare")
    parser.add_argument("--output", type=str, help="File di output per i risultati (JSON)")
    parser.add_argument("--custom-entities", type=str, nargs="+", 
                      help="Lista di entità personalizzate da cercare nel testo")
    
    args = parser.parse_args()
    
    # Ottieni il testo da analizzare
    text = args.text
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
    
    if not text:
        print("Errore: è necessario fornire un testo da analizzare (--text o --file)")
        sys.exit(1)
    
    # Crea l'estrattore e analizza il testo
    extractor = create_ner_extractor(args.model)
    
    # Estrai tutte le entità, incluse quelle personalizzate se specificate
    results = extractor.extract_all(text, args.custom_entities)
    
    # Output dei risultati
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main() 