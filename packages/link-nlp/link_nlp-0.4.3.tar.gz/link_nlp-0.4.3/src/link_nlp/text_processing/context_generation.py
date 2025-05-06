import pandas as pd
import generationUtils as gu

# GLOBAL VARIABLES FOR GENERATION
PHI4=True
file_name = "generatione_contesti_correttivi_v4.csv"
dataset = "data_appalti_v5.csv"

# INIZIALIZE ENVIROMENT
llm,config,tokenizer = gu.inizializeModel("",PHI4)
grouped, references_grouped, allegati_grouped, text_articles, text_allegati = gu.downloadDataset(dataset)


dataset_correttivo = pd.read_csv("codice_appalti_correttivo.csv", sep=",", encoding="utf-8")

# GENERATE RESPONSE

# result = gu.generation_with_commas(llm,config,tokenizer,grouped,allegati_grouped,references_grouped, text_articles, text_allegati,PHI4)
result = gu.generation_with_commas_and_correttivo(llm,config,tokenizer,grouped,references_grouped,text_articles,PHI4,dataset_correttivo, allegati_grouped,text_allegati)

result_df = pd.DataFrame(result)
result_df.to_csv(file_name+".csv", sep=",", encoding="utf-8", index=False)

print("Contextual chunks saved to CSV and TXT.")