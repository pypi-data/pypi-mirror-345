from transformers import AutoTokenizer, pipeline
import pandas as pd
import os
import spacy

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

# Prompt di sistema
system_prompt = """
You are an able AI assistant that generates contextual information of an input article considering the missing information when taken only one of its parts.
Your task is to define a header for a chunk of this article to preserve the contextual information of the whole text once this chunk is provided to a RAG system.
Please give a short succinct context for the purposes of improving search retrieval of the chunk.
Answer only with the succinct context and nothing else. You MUST use a correct italian language.
"""

# Prompt di generazione
context_generation_prompt = """
Here's the article:
<article>

{SPECIFIC_ARTICLE}
</article>

Here is the chunk:
<chunk>
{CHUNK}
</chunk>
Now produce a short context without adding any prehamble or comment. Use italian.
""".strip()

# Caricamento dei dati e processing di questi ultimi
data = pd.read_csv("data_appalti.csv", sep=",", encoding="utf-8")
data_filtered = data[data["Comma"].notna()]

# Raggruppa i dati per Decreto e Articolo
grouped = data_filtered.groupby(["Decreto", "Articolo"])

# Salviamo i vari articoli completi
text_articles = {}

for (decreto, articolo), group in grouped:

    sorted_group = group.sort_values(by="Comma")

    testo_contenuto = " ".join(sorted_group["Testo_Contenuto"].tolist())

    text_articles[(decreto, articolo)] = testo_contenuto

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-instruct")

llm = pipeline("text-generation",
               model="meta-llama/Meta-Llama-3-8B-instruct",
               model_kwargs={
                   "device_map" : "cuda",
                   "torch_dtype" : "bfloat16"
                   }
               )

# Configurazione per la generazione
gen_config = {
    "max_new_tokens" : 128,
    "do_sample" : True,
    "temperature" : 0.2,
    "top_k" : 30,
    "num_return_sequences" : 1,
    "return_full_text" : False
}

generated_chunks = []

for key, value in text_articles.items():
    # Splitta il testo in chunks
    chunks = split_with_spacy(value)

    # Unisci i chunks troppo corti
    merged_chunks = merge_short_chunks(chunks, min_length=45)

    for chunk in merged_chunks:

        input_prompt = context_generation_prompt.format(
            SPECIFIC_ARTICLE=value, CHUNK=chunk
        )

        chat_formatted_template = tokenizer.apply_chat_template([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_prompt}
        ], tokenize=False, add_generation_prompt=True)
        
        # Generazione del contesto
        gen_ctx = llm(chat_formatted_template, **gen_config)[0]["generated_text"].strip()

        # Aggiungi il risultato alla lista dei chunks generati
        generated_chunks.append({
            "decree": key[0],
            "article": key[1],
            "chunk": chunk,
            "context_generated": gen_ctx
        })
        
        print(f"\nGenerated Response:\n -CHUNK:\n {chunk} \n ************ \n -CONTESTO GENERATO:\n {gen_ctx}\n\n\n")
        print("-"*50)

# Creazione del DataFrame con i risultati
result_df = pd.DataFrame(generated_chunks)

# Salva i risultati in un file CSV
result_df.to_csv('contextual_chunks_alternative.csv', sep=",", encoding="utf-8", index=False)

# Salva i risultati in un file TXT
with open('contextual_chunks_alternative.txt', 'w', encoding="utf-8") as txt_file:
    for _, row in result_df.iterrows():
        txt_file.write(f"Decree: {row['decree']}, Article: {row['article']}\n")
        txt_file.write(f"Chunk Content: {row['chunk']}\n")
        txt_file.write(f"Generated Context: {row['context_generated']}\n")
        txt_file.write("*" * 100 + "\n\n")

# Stampa dei risultati
print("Contextual chunks saved to CSV and TXT.")