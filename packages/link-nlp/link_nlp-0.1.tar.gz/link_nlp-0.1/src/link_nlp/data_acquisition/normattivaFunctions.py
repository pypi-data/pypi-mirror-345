import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import locale
import datetime
from selenium.webdriver.firefox.service import Service
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from lxml import etree
from BrowserSessionClass import BrowserSession

namespaces = {
    'akn': 'http://docs.oasis-open.org/legaldocml/ns/akn/3.0',
    'eli': 'http://data.europa.eu/eli/ontology#',
    'fo': 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0',
    'gu': 'http://www.gazzettaufficiale.it/eli/',
    'html': 'http://www.w3.org/1999/xhtml',
    'na': 'http://www.normattiva.it/eli/',
    'nakn': 'http://normattiva.it/akn/vocabulary',
    'nrdfa': 'http://www.normattiva.it/rdfa/',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfa': 'http://www.w3.org/1999/xhtml#'
}

MAX_DEPTH = 1

browser = None

def set_browser(b : BrowserSession):
    global browser
    browser = b

def correct_link_scheme(url, base_url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = urljoin(base_url, url)
    return url

def extract_details_from_urn(href):
    urn_start = href.find("urn:nir:")
    if urn_start == -1:
        print("URN non trovato nel link.")
        return None, None, None

    urn = href[urn_start:]  
    print(f"URN estratto: {urn}")
    
    parts = urn.split(':')

    if len(parts) >= 5:
        tipo_documento = parts[3].replace('.', ' ').upper()  # Decreto o altro

        try:
            data_documento, numero_documento = parts[4].split(';')  # data e numero separati da ;
        except ValueError:
            print("Errore nel formato dei dettagli (data e numero).")
            return None, None, None

        try:
            # Controlla il formato della data e parsala
            if '-' not in data_documento:  # Solo anno
                date_obj = datetime.datetime.strptime(data_documento, '%Y')
                formatted_date = date_obj.strftime('%Y')
            elif data_documento.count('-') == 1:  # Anno e mese
                date_obj = datetime.datetime.strptime(data_documento, '%Y-%m')
                formatted_date = date_obj.strftime('%B %Y')  # Es. "November 2024"
            elif data_documento.count('-') == 2:  # Anno, mese e giorno
                date_obj = datetime.datetime.strptime(data_documento, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d %B %Y')  # Es. "19 November 2024"
            else:
                print("Formato data non riconosciuto.")
                return None, None, None
        except Exception as e:
            print(f"Errore nella formattazione della data: {e}")
            return None, None, None

        return tipo_documento, formatted_date, numero_documento

    print("Formato dell'URN non valido.")
    return None, None, None

def find_most_recent_file(folder_path):
    files = os.listdir(folder_path)
    if not files:
        return None
    try:
        most_recent_file = max(
            (os.path.join(folder_path, f) for f in files),
            key=os.path.getmtime
        )
    except Exception as e:
        print(f"Errore durante la ricerca del file più recente: {e}")
        return None
    return most_recent_file

def extract_text_from_p(p):
    text = ""
    
    if p.text:
        text += p.text.replace('\n', ' ') + " "
    
    for element in p.iter():
        if element.tag == '{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}ins':
            text += (element.text or "").replace('\n', ' ') + " "
            if element.tail:
                text += element.tail.replace('\n', ' ') + " "
        elif element.tag == '{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}ref':
            text += (element.text or "").replace('\n', ' ') + " "
            if element.tail:
                text += element.tail.replace('\n', ' ') + " "
    
    if p.tail:
        text += p.tail.replace('\n', ' ') + " "
    
    return text.strip()

def dividi_in_commi(testo):
    testo = " " + testo
    
    pattern = r'(?<=\s)(\d+\.\s)'
    
    parti = re.split(pattern, testo)

    print(parti)
    
    commi = []
    numero_precedente = 0
    for i in range(1, len(parti), 2):
        numero_puntato = parti[i].strip()
        
        if i + 1 < len(parti):
            testo_comma = parti[i + 1].strip()
        else:
            testo_comma = ""
        
        numero_comma = int(numero_puntato.split('.')[0])
        
        if numero_comma == numero_precedente + 1:
            commi.append(numero_puntato + testo_comma)
            numero_precedente = numero_comma
        else:
            commi[-1] += numero_puntato + testo_comma
    
    return commi

def format_article_number(text):
    return text.lower().replace(" ", "-")

def save_main_text_to_file(main_text, article_folder):
    file_name = f'main_text.txt'
    with open(os.path.join(article_folder, file_name), 'w', encoding='utf-8') as file:
        file.write(main_text.strip() + '\n')
    print(f"Salvato {file_name} in {article_folder}")

def analyze_file(file_path,folder_path):
    retries = 3
    while retries > 0:
        if os.access(file_path, os.R_OK):
            break
        else:
            print(f"File non accessibile, tentativo in corso. Tentativi rimanenti: {retries}")
            time.sleep(2)
            retries -= 1
    if retries == 0:
        print("Impossibile accedere al file dopo diversi tentativi.")
        return False
    try:
        tree = etree.parse(file_path)
    except OSError as e:
        print(f"Errore durante la lettura del file '{file_path}': {e}")
        return False
    except etree.XMLSyntaxError as e:
        print(f"Errore XML: il file '{file_path}' potrebbe essere vuoto o malformato: {e}")
        return False
    root = tree.getroot()
    # Trova tutti gli elementi <article> all'interno del file XML
    articles = root.findall('.//akn:article', namespaces)
    # print(f"Numero di articoli trovati: {len(articles)}")
    # Estrai e scrivi il testo di ciascun comma (paragrafo) all'interno degli articoli
    for article_index, article in enumerate(articles, start=1):
        # Ottieni l'eId dell'articolo
        article_eid = article.get('eId')
        # print(f"{article_eid}")
        # Crea una cartella per l'articolo
        article_folder = os.path.join(folder_path, article_eid)
        os.makedirs(article_folder, exist_ok=True)
        # Trova tutti gli elementi <paragraph> all'interno dell'articolo
        paragraphs = article.findall('.//akn:paragraph', namespaces)
        paragraph_counter = 1  # Inizializza il contatore dei paragrafi
        for paragraph in paragraphs:
            # Controlla se il paragrafo ha un elemento <num>
            # num = paragraph.find('.//akn:num', namespaces)
            # if num is None:
            #     continue  # Salta il paragrafo se non ha un elemento <num>
            # Inizializza il testo del paragrafo
            paragraph_text = ""
            # Verifica se è una lista o no
            lists = paragraph.findall('.//akn:list', namespaces)
            # Se è una lista, salva il contenuto in maniera diversa
            if lists:
                for lst in lists:
                    list_text = ""
                    intro = lst.find('.//akn:intro', namespaces)
                    if intro is not None:
                        ps = intro.findall('.//akn:p', namespaces)
                        for p in ps:
                            list_text += extract_text_from_p(p)
                    points = lst.findall('.//akn:point', namespaces)
                    for point in points:
                        point_num = point.find('.//akn:num', namespaces)
                        point_content = point.find('.//akn:content', namespaces)
                        if point_num is not None:
                            list_text += (point_num.text or "") + " "
                        if point_content is not None:
                            ps = point_content.findall('.//akn:p', namespaces)
                            for p in ps:
                                list_text += extract_text_from_p(p)
                    paragraph_text += list_text
            else:
                # Trova tutti gli elementi <p> all'interno del <content> del paragrafo
                content = paragraph.find('.//akn:content', namespaces)
                if content is not None:
                    ps = content.findall('.//akn:p', namespaces)
                    for p in ps:
                        paragraph_text += extract_text_from_p(p)

            # Se il paragrafo non è vuoto, scrivi il testo completo nel file
            if paragraph_text.strip():
                commi = dividi_in_commi(paragraph_text.strip())
                # Crea un file per ciascun comma
                for comma in commi:
                    file_name = f'comma_{paragraph_counter}.txt'  # Aggiungi un identificatore progressivo
                    with open(os.path.join(article_folder, file_name), 'w', encoding='utf-8') as file:
                        file.write(comma + '\n')
                    paragraph_counter += 1  # Incrementa il contatore solo se il file è stato creato
        # Trova tutti gli elementi <authorialNote> all'interno dell'articolo
        authorial_notes = article.findall('.//akn:authorialNote', namespaces)
        for note_index, note in enumerate(authorial_notes, start=1):
            note_text = ""
            note_ps = note.findall('.//akn:p', namespaces)
            for p in note_ps:
                note_text += extract_text_from_p(p)
            # Scrivi la nota in un file separato
            note_file_name = f'nota_articolo_{note_index}.txt'
            with open(os.path.join(article_folder, note_file_name), 'w', encoding='utf-8') as note_file:
                note_file.write(note_text.strip() + '\n')
    return True

def save_recursive_content(text, folder, content_reference):
    content_reference = content_reference.replace("/", "-")
    
    try:
        os.makedirs(folder, exist_ok=True)
    except OSError as e:
        print(f"Errore nella creazione della cartella {folder}: {e}. Skipping...")
        return
    
    # Costruisci il percorso del file
    file_path = os.path.join(folder, f"{content_reference}.txt")
    
    # Salva il testo nel file
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(text)
        print(f"Contenuto salvato in: {file_path}")
    except OSError as e:
        print(f"Errore durante il salvataggio del file '{file_path}': {e}. Skipping...")
        return  # Salta il salvataggio e prosegui

def recursive_find(href, folder, depth, max_depth, content_reference):
    if depth > max_depth:
        return

    # Fai la richiesta HTTP per ottenere l'HTML della pagina
    response = requests.get(href)
    if response.status_code != 200:
        print(f"Errore nel caricamento della pagina: {href}")
        start_or_reset_session()
        response = requests.get(href)
        if response.status_code != 200:
            print(f"Errore nel caricamento della pagina. di nuovo: {href}")
            return

    # Usa BeautifulSoup per analizzare l'HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Estrai il div 'bodyTesto' principale
    body_testo_div = soup.find('div', class_="bodyTesto")
    if body_testo_div:
        print(f"{folder}")
        article_name = folder.split("/")[-1]  # Estrai il nome dell'articolo
        print(f"\nEstrazione contenuti per l'articolo: {article_name}")

        # Salva il testo dell'articolo
        save_recursive_content(content_reference + "\n" + body_testo_div.get_text(strip=True), folder, content_reference)
        
        # Trova tutti i link nel bodyTesto che contengono "~art"
        href_links = [
            {'href': a['href'], 'content': a.get_text(strip=True)} 
            for a in body_testo_div.find_all('a', href=True) 
            if "~art" in a['href']
        ]
        print(f"Trovati {len(href_links)} link nell'articolo {article_name}")

        # Per ogni link, chiamerai ricorsivamente la funzione
        for link in href_links:   
            full_link = urljoin("https://www.normattiva.it", link['href'])  # Costruisci il link completo
            recursive_find(full_link, folder, depth + 1, max_depth, link['content'])

def find_reference(href, main_folder, max_depth):
    article_links = []  # Lista per salvare i link degli articoli
    # Carica la pagina principale (href) con Selenium per la navigazione iniziale
    driver.get(href)
    time.sleep(2)  # Attendi il caricamento della pagina

    # Ottieni il contenuto della pagina
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Trova il div con id "albero"
    albero_div = soup.find('div', id="albero")
    if not albero_div:
        print("Div con id 'albero' non trovato.")
        return

    # Trova il primo ul all'interno del div
    ul = albero_div.find('ul')
    if not ul:
        print("Nessun <ul> trovato all'interno del div 'albero'.")
        return

    # Lista per salvare i dati estratti
    lista_articoli = []

    # Trova ogni <li> all'interno dell'<ul> e controlla se contiene un <a class="numero_articolo">
    for li in ul.find_all('li'):
        a_tag = li.find('a', class_="numero_articolo")
        if a_tag and 'onclick' in a_tag.attrs:
            # Estrai il link dall'attributo onclick
            onclick_content = a_tag['onclick']
            match = re.search(r"return showArticle\('([^']+)", onclick_content)
            if match:
                link_articolo = urljoin("https://www.normattiva.it", match.group(1))

                # Format articolo e aggiungi alla lista
                articolo_formattato = a_tag.text.lower().replace(" ", "-")
                lista_articoli.append({'link': link_articolo, 'articolo': articolo_formattato})

    # Apre una finestra secondaria all'inizio
    driver.execute_script("window.open('');")
    window_handles = driver.window_handles
    main_window = window_handles[0]  # Salva l'handle della finestra principale
    secondary_window = window_handles[-1]  # Salva l'handle della finestra secondaria

    # Per ogni articolo nella lista, usa la finestra secondaria per raccogliere i link e avviare la ricerca
    for articolo in lista_articoli:

        # Passa alla finestra secondaria per caricare l'articolo
        driver.switch_to.window(secondary_window)

        # Usa la finestra secondaria per caricare la pagina dell'articolo
        driver.get(articolo['link'])
        time.sleep(2)  # Attendi il caricamento della pagina

        # Ottieni il contenuto dell'articolo
        soup_articolo = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Estrai i link dal bodyTesto dell'articolo e inizia la ricerca ricorsiva
        body_testo_div = soup_articolo.find('div', class_="bodyTesto")
        if body_testo_div:
            print(f"\nInizio ricerca ricorsiva per l'articolo: {articolo['articolo']}")
        # Trova tutti i link dentro il bodyTesto e avvia la funzione ricorsiva per ciascun link
        href_links = [
            {'href': a['href'], 'content': a.get_text(strip=True)} 
            for a in body_testo_div.find_all('a', href=True) 
            if "~art" in a['href']
        ]
        article_links.append({'article': f"art_{articolo['articolo']}",
                                  'links': href_links})    
    
    driver.close() # Chiudi la finestra secondaria e torna alla finestra principale

    start_or_reset_session()

    article_links.sort(key=lambda x: x['article'])

    print("Inizio ricerca ricorsiva per i riferimenti trovati.")
    print(f"Numero di articoli trovati: {len(article_links)}")

    for elem in article_links:
        article_folder = os.path.join(main_folder, elem['article'])
        for link in elem['links']:
            full_link = urljoin("https://www.normattiva.it", link['href'])
            recursive_find(full_link, article_folder, 0, max_depth, link['content'])
    
    start_or_reset_session()

def save_commas_to_files(commas_data, article_folder):
    for i, comma_data in commas_data:
        file_name = f'comma_{i}.txt'
        with open(os.path.join(article_folder, file_name), 'w', encoding='utf-8') as file:
            file.write(comma_data + '\n')
    print(f"Salvati {len(commas_data)} commi in {article_folder}")

def download_article_without_akn_file(href, main_folder,method_alternative):
    start_or_reset_session()
    base_url = "https://www.normattiva.it"
    article_links = {}

    # Carica la pagina principale e attende che si carichi completamente
    print(f"Caricamento della pagina principale: {href}")
    for attempt in range(4):
        try:
            print(f"Tentativo {attempt + 1} di caricare la pagina: {href}")
            driver.get(href)
            time.sleep(1)  # Puoi rimuoverlo o ridurlo se hai attese più specifiche con WebDriverWait
            break
        except (TimeoutException, WebDriverException) as e:
            print(f"Errore durante il caricamento: {e}. Ritento tra 5 secondi...")
            time.sleep(5)
    if attempt == 3:
        print("Impossibile caricare la pagina dopo vari tentativi.")
        start_or_reset_session()
        download_article_without_akn_file(href, main_folder)
        return


    # Analizza la pagina con BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    albero_div = soup.find("div", id="albero")
    if not albero_div:
        print("Errore: div con id 'albero' non trovato.")
        return article_links

    # Trova e filtra gli <li> che contengono un <a> con classe 'numero_articolo'
    list_items = albero_div.find("ul").find_all("li")
    filtered_items = [
        li for li in list_items 
        if li.find("a", class_="numero_articolo") and 
        not any(x in li.find("a", class_="numero_articolo").text for x in ["orig.", "agg."])
    ]
    
    print(f"Numero di elementi trovati con 'numero_articolo': {len(filtered_items)}")

    # Ottieni l'handle della finestra principale
    main_window = driver.current_window_handle

    for i, li in enumerate(filtered_items):
        article_element = li.find("a", class_="numero_articolo")

        if not article_element or 'onclick' not in article_element.attrs:
            print(f"Elemento {i} saltato: manca un link valido o l'attributo 'onclick'.")
            continue

        # Estrai il testo del numero articolo e formattalo
        article_number_text = article_element.text.strip()
        formatted_article_number = format_article_number(article_number_text)

        # Estrai il parametro dell'URL dall'attributo onclick
        onclick_text = article_element['onclick']
        match = re.search(r"showArticle\('([^']*)'", onclick_text)
        if not match:
            print(f"Elemento {i}: URL non trovato nell'onclick.")
            continue
        
        relative_url = match.group(1)
        article_url = base_url + relative_url
        print(f"Elemento {i} - URL dell'articolo: {article_url}")

        # Chiudi la scheda secondaria se già esistente
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[1])
            driver.close()

        # Apri una nuova scheda e passa a essa
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])  # Passa alla scheda secondaria
        driver.get(article_url)

        # Attendi che il div bodyTesto sia presente
        try:
            body_text_div = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "bodyTesto"))
            )
            article_soup = BeautifulSoup(driver.page_source, 'html.parser')
            body_text_div = article_soup.find("div", class_="bodyTesto")

            article_folder = os.path.join(main_folder, f"art_{formatted_article_number}")
            os.makedirs(article_folder, exist_ok=True)

            if method_alternative:
                commas_data = []
                alternative_text_formatted = None
                full_text = None
                # Trova tutti gli elementi span con classe "art_text_in_comma"
                commas = body_text_div.find_all(class_="art-comma-div-akn")

                if commas:
                    # Itera su ogni elemento e crea la lista incrementale
                    for i, comma in enumerate(commas, start=1):
                        text_comma = comma.get_text(strip=True)  # Ottieni il testo del comma
                        commas_data.append((i, text_comma))
                else:
                    # Se non ci sono "art_text_in_comma", cerca "art-just-text-akn"
                    alternative_text = body_text_div.find(class_="art-just-text-akn")
                    if alternative_text:
                        # Salva il testo come stringa
                        alternative_text_formatted = alternative_text.get_text(separator=" ").strip()
                    else:
                        # Se nessuno dei due casi è soddisfatto, imposta a None
                        commas_data = None
            else:
                # Estrai tutto il testo dal bodyTesto
                full_text = body_text_div.get_text(separator=" ").strip()


            if method_alternative:
                if commas_data and len(commas_data) > 0:
                    save_commas_to_files(commas_data, article_folder)
                elif alternative_text_formatted is not None:
                    file_name = f'alternativeText.txt'
                    with open(os.path.join(article_folder, file_name), 'w', encoding='utf-8') as file:
                        file.write(alternative_text_formatted + '\n')
                else:
                    print("Nessun testo trovato.")
            else:
                save_main_text_to_file(full_text, article_folder,method_alternative)

        except TimeoutException:
            print(f"Elemento {i}: div con classe 'bodyTesto' non trovato dopo attesa.")
            driver.close()
            driver.switch_to.window(main_window)
            continue

        # Chiudi la scheda secondaria e torna alla finestra principale
        driver.close()
        driver.switch_to.window(main_window)

    print("Download e salvataggio completati per tutti gli articoli.")
     
     
     
     
     
     
     
     
def inizialize_folder(href):
    tipo_documento, formatted_date, numero_documento = extract_details_from_urn(href)
    if tipo_documento and formatted_date and numero_documento:
        # Formatta la cartella principale
        folder_name = f"{tipo_documento} {formatted_date},n. {numero_documento}"

        # Leggi il contenuto attuale del file per controllare duplicati
        with open(normattiva_links_file, 'r') as f:
            existing_links = f.readlines()
        
        # Verifica se il link è già presente
        new_entry = f"{href};{folder_name}\n"
        if new_entry not in existing_links:
            # Aggiungi il link e il nome della cartella al file NormattivaLinks
            with open(normattiva_links_file, 'a') as f:
                f.write(new_entry)
        
        print(f"Cartella da creare: {folder_name}")
        # Crea la cartella principale per il documento
        main_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'Dataset', folder_name)
        os.makedirs(main_folder, exist_ok=True)
        return main_folder, folder_name
    
def download_file_and_articles(href,main_folder,timeout=20, poll_interval=1):
    try:
        driver.get(href)
        start_time = time.time()
        download_link = None
        
        # Ciclo di polling per cercare l'elemento senza bloccare il codice
        while (time.time() - start_time) < timeout:
            download_buttons = driver.find_elements(By.XPATH, "//a[contains(@href, '/do/atto/caricaAKN?')]")
            if download_buttons:
                download_link = download_buttons[0]
                break
            # Attesa breve prima di riprovare
            time.sleep(poll_interval)
        

        if download_link:
            # Se il pulsante è stato trovato, procedi con il download
            file_url = download_link.get_attribute('href')
            print(f"Link per il download trovato: {file_url}")
            download_link.click()

            recent_file = wait_for_recent_xml(dataset_folder)
            if recent_file:
                response = analyze_file(recent_file, main_folder)
                if response is False:
                    print("Errore durante l'analisi del file XML. Provo con un altro metodo.")
                    download_article_without_akn_file(href, main_folder)
                # Elimina il file XML scaricato dopo averlo elaborato
                os.remove(recent_file)
                print(f"File XML eliminato: {recent_file}")
            else:
                download_article_without_akn_file(href, main_folder)
                
        else:
            # Se il pulsante non è stato trovato entro il tempo limite, esegui la funzione alternativa
            print("Non c'è il pulsante per il download. Provo con un altro metodo.")
            download_article_without_akn_file(href, main_folder)
            
        
    finally: 
        print("Download completato")
 
def carica_links_da_file(percorso_file):
    links = []  # Lista per memorizzare i dati
    with open(percorso_file, "r", encoding="utf-8") as file:
        for linea in file:
            # Rimuove newline e spazi inutili
            linea = linea.strip()
            if ": " in linea:  # Verifica che il formato sia corretto
                href, testo = linea.split(": ", 1)  # Divide la stringa in href e testo
                links.append({"link": href, "testo": testo})  # Aggiunge un dizionario alla lista
    return links


def download_element(query):
    final_query = query + " normattiva"
    query_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    
    # Invia la richiesta HTTP alla pagina di ricerca di Google
    response = requests.get(url, headers=browser.headers)
    soup = BeautifulSoup(response.text, 'html.parser')
