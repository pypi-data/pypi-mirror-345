"""
This module provides the main interface for downloading legal documents from the Normattiva.it website.
It manages browser sessions and delegates the actual scraping work to normattivaFunctions.
Functions:
    - download_normattiva_element: Downloads a legal document based on a search query
"""

from .BrowserSessionClass import BrowserSession
from . import normattivaFunctions as nf

_initialized = False


def _init_browser():
    """
    Initilize the browser session for the download of the normattiva elements.
    """
    global _initialized
    if not _initialized:
        _initialized = True
        global browser
        browser = BrowserSession()
        nf.set_browser(browser)

def download_normattiva_element(query:str):
    """Downloads an element from Normattiva and saves it in the dataset folder and a csv file.

    Args:
        query (str): The request element to download from normattiva.it.
    
    Returns:
        None
    """
    
    # Initialize browser session if not already done
    if not _initialized:
        _init_browser()
    
    # Start browser session
    browser.start_or_reset_session()
    
    # Donwload element
    nf.download_element(query)
    
    # Close browser session
    browser.close_session()
























# start_or_reset_session()
# download_link_references()
# # Percorso relativo al Desktop
# percorso_file = os.path.expanduser("~/Desktop/linksTrovati.txt")

# # Carica i link dal file
# lista_links = carica_links_da_file(percorso_file)
    
# print(f"numero di elementi: {len(lista_links)}")

# for elemento in lista_links:
#     # main_function_download(elemento["testo"],elemento["link"])
#     folder = os.path.join(dataset_references_folder, elemento["testo"])
#     os.makedirs(folder, exist_ok=True)
#     find_reference("https://www.normattiva.it/"+elemento["link"],folder,MAX_DEPTH)
#     time.sleep(3)

# main_function_download("TITOLI_DA_INSERIRE","https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2024-12-31;209!vig",True)

# folder = os.path.join(dataset_folder, "DECRETO LEGISLATIVO 31 dicembre 2024, n. 209")
# find_reference("https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2024-12-31;209!vig",folder,MAX_DEPTH)
# driver.quit()








