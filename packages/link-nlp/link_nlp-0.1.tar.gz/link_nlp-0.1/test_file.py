"""

"pip install -e ." per installare il pacchetto in locale

# Installa con supporto per GLiNER
pip install -e ".[gliner]"

# Installa con supporto per Transformers
pip install -e ".[transformers]"

# Installa con entrambi i supporti
pip install -e ".[gliner,transformers]"

# Da riga di comando
python -m link_nlp.text_processing.ner_extractor --model "dbmdz/bert-base-italian-xxl-uncased" --text "L'articolo 15 del decreto legislativo 36/2023 stabilisce che..." --custom-entities decreto articolo allegato
"""
 
"""
from link_nlp.text_processing.ner_extractor import create_ner_extractor
from
# Crea un estrattore NER
extractor = create_ner_extractor("dbmdz/bert-base-italian-xxl-uncased")
text = "L'articolo 15 del decreto legislativo 36/2023 stabilisce che..."
custom_entities = ["decreto", "articolo", "allegato"]
entities = extractor.extract_all(text, custom_entities)
print(entities)
"""



#  "pip install -e ." per installare il pacchetto in locale e relative dipendenze

from link_nlp.text_processing.text_generation_unified import TextGenerator

# Inizializza il generatore di testo con use_llm=False per utilizzare la pipeline invece di vllm
# Impostiamo esplicitamente device="cpu" per evitare errori con CUDA
generator = TextGenerator(model_name="Qwen/Qwen2.5-1.5B-Instruct", use_llm=False, device="cpu")

# Prepara il prompt
prompt = "Parlami in breve del codice degli appalti italiano"

# Genera il testo utilizzando il metodo generate_with_pipeline
generated_text = generator.generate_with_pipeline(prompt) 

#generated_text = generator.generate_with_llm(prompt) 

#utilizzo il metodo generate_with_pipeline perchè uso cpu del macbook
#se dispongo di una gpu, posso utilizzare il metodo generate_with_llm

# Stampa il testo generato
print(generated_text)