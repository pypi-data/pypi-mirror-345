from transformers import AutoTokenizer, pipeline
import pandas as pd
from tqdm import tqdm
import os

test_rows = 100

# Caricamento dei dati
data = pd.read_csv("data.csv", sep=",", encoding="utf-8").head(test_rows)

# Pipeline del modello
llm = pipeline("text-generation",
               model="meta-llama/Meta-Llama-3-8B-instruct",
               device=0,
               model_kwargs={
                   "torch_dtype": "bfloat16"
               })

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-instruct")

print(f"Limite di token del modello: {tokenizer.model_max_length}")

# Prompt di sistema
system_prompt = """
You are an able AI assistant that generates contextual information of an input article considering the missing information when taken only one of its parts.
Your task is to define a header for a chunk of this article to preserve the contextual information of the whole text once this chunk is provided to a RAG system.
Answer only with the succinct context and nothing else. You MUST use a correct Italian language.
"""

# Prompt di generazione
context_generation_prompt = """
Here's the article:
<article>
{{SPECIFIC_ARTICLE}}
</article>

<chunk>
{{CHUNK_CONTENT}}
</chunk>
""".strip()

# Generazione dei gruppi per Decreto e Articolo
grouped = data.groupby(["Decreto", "Articolo"])

# Lista finale dei chunks
contextual_chunks = []

# Loop sui chunks
for index, row in tqdm(data.iterrows(), total=len(data)):
    # Chunk corrente
    content = row["Testo_Contenuto"]
    decreto = row["Decreto"]
    articolo = row["Articolo"]

    # Ottieni tutti i contenuti dello stesso decreto e articolo, formattati per <article>
    specific_article_group = grouped.get_group((decreto, articolo))
    specific_article_group = specific_article_group[specific_article_group["Comma"].notna()]

    specific_article = f"Articolo {articolo}\n"
    specific_article += "\n".join([f"Comma {row['Comma']}: {row['Testo_Contenuto']}" for _, row in specific_article_group.iterrows()])

    # Suddividi il chunk corrente in sotto-chunks
    chunks = content.split(".")
    chunks = [chunk.strip() + "." for chunk in chunks if len(chunk.strip()) > 0]

    # Processa ogni sotto-chunk
    for chunk in chunks:
        # Sostituzione nel prompt
        input_prompt = context_generation_prompt.replace("{{SPECIFIC_ARTICLE}}", specific_article)
        input_prompt = input_prompt.replace("{{CHUNK_CONTENT}}", chunk)

        # Creazione del template formattato per il modello
        chat_formatted_template = tokenizer.apply_chat_template([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_prompt}
        ], tokenize=False, add_generation_prompt=True)

        # Configurazione per la generazione
        gen_config = {
            "max_new_tokens": 128,
            "do_sample": True,
            "temperature": 0.2,
            "top_k": 30,
            "num_return_sequences": 1,
            "return_full_text": False
        }

        # Generazione del contesto
        gen_ctx = llm(chat_formatted_template, **gen_config)[0]["generated_text"].strip()

        # Salvataggio del risultato
        contextual_chunks.append({"decree": decreto, "article": articolo, "chunk": chunk, "context_generated": gen_ctx})

# Creazione del DataFrame
df_ctx = pd.DataFrame(contextual_chunks)

# Salvataggio su file CSV
df_ctx.to_csv('contextual_chunks.csv', sep=",", encoding="utf-8", index=False)

# Stampa dei risultati
print("Contextual chunks:")
print("-" * 100)
for chunk in contextual_chunks:
    print(f"Chunk Content: {chunk['chunk']}")
    print(f"Generated Context: {chunk['context_generated']}")
    print("*" * 100)
    print("\n\n")
