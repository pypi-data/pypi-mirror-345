"""
This is the main application script that demonstrates creating contextual chunks for a document.
It uses a language model to generate contextual information for each chunk, which can then
be used for improved information retrieval in a RAG (Retrieval Augmented Generation) system.
"""

import pandas as pd
import numpy as np
import os
from transformers import pipeline
from transformers import AutoTokenizer
from tqdm import tqdm


PATH = '/llms'
os.environ['TRANSFORMERS_CACHE'] = PATH
os.environ['HF_HOME'] = PATH
os.environ['HF_DATASETS_CACHE'] = PATH
os.environ['TORCH_HOME'] = PATH

text = """
In base all’art 11 commi 3 e 4 del Dlgs 36/2023, il ribasso inserito nell’offerta non può essere ottenuto in danno dei lavoratori mediante l’applicazione di un CCNL che, essendo incoerente rispetto alle lavorazioni, comporti minori tutele economiche e normative.
La suddetta norma provoca una limitazione della libertà di organizzazione aziendale, e dunque non può essere interpretata in senso eccessivamente restrittivo. Occorre infatti evitare di introdurre freni non necessari alla concorrenza, che potrebbero ostacolare il raggiungimento della massima partecipazione.
Si ritiene pertanto che un’impresa possa mantenere il proprio CCNL anche in una gara che in base alle ripartizioni della contrattazione collettiva si collocherebbe in un altro settore economico, purché, secondo una valutazione complessiva, giuridica ed economica, sussistano i seguenti requisiti:
(i) il trattamento dei lavoratori impiegati in tale gara non sia eccessivamente inferiore a quello dei CCNL individuati dalla stazione appaltante;
(ii) vi sia corrispondenza, o almeno confrontabilità, tra le mansioni del CCNL applicato e le lavorazioni oggetto dell’appalto.
L’equivalenza dei CCNL non richiede la parità di retribuzione. Una simile condizione sarebbe impossibile, data la varietà di contenuti normalmente osservabile nei diversi settori della contrattazione collettiva, e anche discriminatoria, avendo quale risultato l’imposizione dei soli CCNL presi come riferimento negli atti di gara. A sua volta, il numero chiuso dei CCNL determinerebbe effetti anticoncorrenziali, deprimendo la partecipazione.
D’altra parte, questa non sembra essere l’impostazione seguita dalla stazione appaltante. Gli stessi CCNL indicati nel disciplinare di gara contengono infatti significative differenze di retribuzione, una volta raffrontati i livelli di inquadramento. Occorre quindi ammettere una fascia di oscillazione, nella quale, o attorno alla quale, possano inserirsi anche i CCNL non nominati.
""".strip().replace("\n", "")

chunks = text.split(".")
chunks = [chunk.strip() + "." for chunk in chunks if len(chunk) > 0]

system_prompt = """
You are an able AI assistant that generate a contextual information of an input document considering the missing information when taken only one of its parts.
You task is to define an header for a chunk of this document to preserve the contexual information of the whole text
once this chunk is provided to a RAG system. Please give a short succinct context for the purposes of improving search retrieval of the chunk.
Answer only with the succinct context and nothing else. You MUST use a correct italian language.
"""

context_generation_prompt = """
Here's the document:
<document>
{{WHOLE_DOCUMENT}}
</document>

Here is the chunk:
<chunk>
{{CHUNK_CONTENT}}
</chunk>

Now produce a short context without adding any prehamble or comment. Use italian.
""".strip()
context_generation_prompt = context_generation_prompt.replace("{{WHOLE_DOCUMENT}}", text)

llm = pipeline("text-generation",
               model="microsoft/Phi-3.5-mini-instruct",
               model_kwargs={
                   "device_map" : "cuda",
                   "torch_dtype" : "bfloat16"
                   }
               )

tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3.5-mini-instruct")


contextual_chunks = []
for chunk in tqdm(chunks):
    input_prompt = context_generation_prompt.replace("{{CHUNK_CONTENT}}", chunk)

    chat_formatted_template = tokenizer.apply_chat_template([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": input_prompt}
    ], tokenize=False, add_generation_prompt=True)


    gen_config = {
        "max_new_tokens" : 128,
        "do_sample" : True,
        "temperature" : 0.2,
        "top_k" : 30,
        "num_return_sequences" : 1,
        "return_full_text" : False
    }
    gen_ctx = llm(chat_formatted_template, **gen_config)[0]["generated_text"].strip()

    contextual_chunks.append(gen_ctx + "\n" + "-"*20 + "\n" + chunk)


output_path = "contextual_chunks_output.txt"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("Contextual chunks:\n")
    f.write("-" * 100 + "\n")
    for chunk in contextual_chunks:
        f.write(chunk + "\n")
        f.write("*" * 100 + "\n\n")