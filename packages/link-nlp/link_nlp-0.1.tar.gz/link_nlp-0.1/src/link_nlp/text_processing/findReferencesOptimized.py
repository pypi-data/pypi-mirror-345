import re
from typing import List, Dict, Optional
from .ner_extractor import create_ner_extractor

class ReferenceExtractor:
    def __init__(self, ner_model: str = "gliner"):
        """
        Inizializza l'estrattore di riferimenti.
        
        Args:
            ner_model (str): Nome del modello NER da utilizzare (default: "gliner")
        """
        self.ner_extractor = create_ner_extractor(ner_model)
        
    def extract_references_in_text(self, text: str) -> List[str]:
        # Aggiornamento della regex per riconoscere anche riferimenti del tipo "allegato II.4"
        pattern = r'(?i)\b(?:comma|commi|articolo|articoli|allegato|allegati|punto|punti|legge|decreto[-\s]legge|decreto)\s*(?:\d+[A-Za-z]*\.*|\d+)(?:[,\';]*)|\ballegato\s+(?:I|II|V)\.?\s*\d+'
        return sorted(re.findall(pattern, text, re.IGNORECASE), key=lambda x: text.find(x))

    def separate_word_and_number(self, word: str) -> str:
        # Separa le combinazioni lettera-numero (ad es. "II.4" diventa "II 4")
        return re.sub(r"(\D)(\d)", r"\1 \2", word)

    def process_words(self, words: List[str]) -> List[List[str]]:
        # Per ogni stringa trovata, separa eventuali combinazioni e splitta in token
        return [self.separate_word_and_number(word).split() for word in words]

    def extract_references(self, text: str, filter_allegati: bool = False) -> Optional[List[List[List[str]]]]:
        words = self.extract_references_in_text(text)
        cleaned_words = self.process_words(words)
        list_of_references = check_vicinity(text, cleaned_words)

        if list_of_references:
            # Elimina riferimenti che contengono parole chiave non desiderate
            keywords = {"decreto", "decreti", "decreto legge", "legge", "punto", "punti", "decreto-legge"}
            eliminate_indices = set()

            for i, mainList in enumerate(list_of_references):
                for tokens in mainList:
                    if tokens[0].lower() in {"allegato", "allegati"}:
                        if not is_valid_allegato(tokens):
                            eliminate_indices.add(i)
                    else:
                        for token in tokens:
                            if token.lower() in keywords:
                                eliminate_indices.add(i)

            if filter_allegati:
                for i, mainList in enumerate(list_of_references):
                    for tokens in mainList:
                        if tokens[0].lower() in {"allegato", "allegati"} and not is_valid_allegato(tokens):
                            eliminate_indices.add(i)

            for idx in sorted(eliminate_indices, reverse=True):
                if 0 <= idx < len(list_of_references):
                    del list_of_references[idx]

            final_refs = []
            for mainList in list_of_references:
                ref = None
                for tokens in mainList:
                    if is_valid_allegato(tokens):
                        ref = ["ALLEGATO", f"{tokens[1]}.{tokens[2]}"]
                        break
                if not ref:
                    ref = mainList[0]
                if not isinstance(ref, list):
                    ref = [ref]

                # Avvolgi ogni riferimento in una lista aggiuntiva
                final_refs.append([ref])
            return final_refs
        else:
            return None

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Estrae le entità dal testo usando il modello NER configurato.
        
        Args:
            text (str): Il testo da analizzare
            
        Returns:
            Dict[str, List[str]]: Dizionario con le entità trovate, raggruppate per tipo
        """
        return self.ner_extractor.extract_entities(text)


def replace_punctuation_with_space(word):
    return re.sub(r"[',.;]", " ", word)


def clean_list_of_strings(text_list):
    return [replace_punctuation_with_space(text) for text in text_list]


def find_consecutive_sequence(words, sequence):
    sequence_length = len(sequence)
    for i in range(len(words) - sequence_length + 1):
        if words[i:i + sequence_length] == sequence:
            return i, i + sequence_length - 1
    return None


def check_vicinity(text, words, max_distance=3):
    final_list = []
    cleaned_text = ' '.join([replace_punctuation_with_space(word) for word in text.split()]).split()
    copy_words = words[:]

    for word in words:
        if word in copy_words:
            result = find_consecutive_sequence(cleaned_text, word)
            if result is None:
                continue

            index_init, index_end = result
            copy_words.remove(word)
            final_word = [word]  # final_word è una lista di gruppi di token
            remove_word = [word]

            # Approccio iterativo (anziché ricorsivo)
            queue = [(cleaned_text, copy_words, word, index_end, final_word, remove_word)]
            while queue:
                cleaned_text, copy_words, current_word, index_end, final_word, remove_word = queue.pop()
                for copy_word in copy_words:
                    result_copy = find_consecutive_sequence(cleaned_text, copy_word)
                    if result_copy is None:
                        continue

                    index_init_copy, index_end_copy = result_copy
                    if abs(index_end - index_init_copy) <= max_distance:
                        subsequence = cleaned_text[index_end + 1:index_init_copy]
                        if "e" in subsequence:
                            continue

                        final_word.append(copy_word)
                        remove_word.append(copy_word)
                        copy_words.remove(copy_word)
                        queue.append((cleaned_text, copy_words, copy_word, index_end_copy, final_word, remove_word))

            final_list.append(final_word)

    return final_list


def is_valid_allegato(tokens):
    """
    Verifica se la lista di token corrisponde a un riferimento "allegato" nel formato:
       ['allegato', <numero romano>, <numero>]
    I numeri romani ammessi sono "I", "II" o "V" (eventualmente in minuscolo).
    """
    if tokens and tokens[0].lower() in {"allegato", "allegati"}:
        if len(tokens) >= 3 and tokens[1].upper() in {"I", "II", "V"} and tokens[2].isdigit():
            return True
    return False


# Funzione globale per compatibilità con il codice esistente
def extract_references(text: str, filter_allegati: bool = False) -> Optional[List[List[List[str]]]]:
    """
    Funzione globale per estrarre riferimenti dal testo.
    
    Args:
        text (str): Il testo da analizzare
        filter_allegati (bool): Se True, filtra i riferimenti agli allegati
        
    Returns:
        Optional[List[List[List[str]]]]: Lista di riferimenti estratti
    """
    extractor = ReferenceExtractor()
    return extractor.extract_references(text, filter_allegati)


# # Esempio di utilizzo:
# text = """4. Le ulteriori competenze, l'organizzazione del Consiglio superiore dei lavori pubblici, le regole di funzionamento, nonché le ulteriori attribuzioni sono stabilite e disciplinate nell'allegato I.11. ((PERIODO SOPPRESSO DAL D.LGS. 31 DICEMBRE 2024, N. 209)).
# 5. Il Consiglio superiore dei lavori pubblici esprime il parere entro quarantacinque giorni dalla trasmissione del progetto. Decorso tale termine, il parere si intende reso in senso favorevole."""

# refs = extract_references(text,True)

# for sublist in refs:
#     print(sublist)
