import pandas as pd
import json




def downloadDataset(dataset):

    data = pd.read_csv(dataset, sep=",", encoding="utf-8")
    data_filtered = data[(data["Comma"].notna()) & (pd.isna(data["Allegato"]))]

    grouped = data_filtered.groupby(["Decreto", "Articolo"])

    references_grouped = data[(data["Comma"].isna()) & (pd.isna(data["Allegato"]))].groupby(["Decreto", "Articolo"])

    allegati_grouped = data[pd.notna(data["Allegato"])].groupby(["Decreto", "Allegato"])
    
    return grouped,references_grouped,allegati_grouped


def downloadReferencesJsonl(grouped_commas, references_grouped, output_filename="references_appalti.jsonl"):

    with open(output_filename, "w") as output_file:
        for (decreto, articolo), group in grouped_commas:
            if (decreto, articolo) in references_grouped.groups:
                reference_group = references_grouped.get_group((decreto, articolo))

                for _, ref_row in reference_group.iterrows():
                    riferimento = ref_row["Riferimento"].removesuffix(".txt")
                    testo_riferimento = ref_row["Testo_Contenuto"]

                    # Crea il dizionario con i campi desiderati
                    reference_data = {
                        "articolo": articolo,
                        "riferimento": riferimento,
                        "contenuto_riferimento": testo_riferimento
                    }

                    # Scrivi il dizionario come JSON nel file in formato JSONL
                    output_file.write(json.dumps(reference_data,ensure_ascii=False) + "\n")
       

def main():
     dataset = "data_appalti_v5.csv"
     grouped,references_grouped,_ = downloadDataset(dataset)
     downloadReferencesJsonl(grouped,references_grouped)
             
                    
                    
if __name__ == "__main__":
    main()