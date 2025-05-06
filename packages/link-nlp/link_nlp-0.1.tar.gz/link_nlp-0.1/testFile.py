import pandas as pd

# Carica il CSV
df = pd.read_csv("generazione_contesti_correttivi_v4.csv")

# Funzione per pulire il titolo
def pulisci_titolo(titolo):
    if pd.isna(titolo):
        return ""
    # Prendi la prima riga prima di un eventuale "Name:"
    prima_riga = titolo.split("\n")[0]
    # Rimuovi numeri, punti e spazi iniziali
    titolo_pulito = prima_riga.lstrip("0123456789. ").strip()
    return titolo_pulito

# Applica la funzione alla colonna article_title
df['article_title'] = df['article_title'].apply(pulisci_titolo)

# Salva il CSV aggiornato
df.to_csv("generazione_contesti_correttivi_v4_modificato.csv", index=False)

print("Modifica completata. Il file aggiornato è stato salvato.")