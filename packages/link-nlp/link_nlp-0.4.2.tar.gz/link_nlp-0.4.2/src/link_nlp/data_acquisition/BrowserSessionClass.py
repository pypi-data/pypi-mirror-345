import os
import locale
from selenium.webdriver.firefox.service import Service
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException


class BrowserSession:
    """Manages a Firefox WebDriver session for downloading elements from Normattiva.

    This class handles the initialization and management of a headless Firefox browser 
    session, ensuring that downloads are saved to a specified dataset folder. 
    It also sets up browser preferences and manages session restarts.
    """

    def __init__(self):
        """Initializes the browser session settings.

        Sets up the Firefox WebDriver with headless mode, defines download directories, 
        and configures locale settings for Italian dates.
        """
        self.driver = None
        self.service = Service()
        self.options = Options()
        self.options.add_argument("--headless")
        self.desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        self.dataset_folder = os.path.join(self.desktop_path, 'Dataset')
        self.normattiva_links_file = os.path.join(self.dataset_folder, 'NormattivaLinks.txt')

        locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')

        self._setup_folders()
        self._setup_firefox_profile()

    def _setup_folders(self):
        """Creates the necessary dataset folders if they do not already exist.

        Ensures that the `Dataset` folder and `NormattivaLinks.txt` file are present 
        in the user's Desktop directory.
        """
        if not os.path.exists(self.dataset_folder):
            os.makedirs(self.dataset_folder)
            print(f"Cartella 'Dataset' creata in {self.dataset_folder}")
        else:
            print(f"Cartella 'Dataset' già presente in {self.dataset_folder}")

        if not os.path.isfile(self.normattiva_links_file):
            open(self.normattiva_links_file, 'w').close()

    def _setup_firefox_profile(self):
        """Configures the Firefox profile for automatic file downloads.

        Sets preferences to disable the download prompt and directly save PDF and 
        binary files into the specified dataset folder.
        """
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser.download.dir", self.dataset_folder)
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf,application/octet-stream")
        self.options.profile = profile

    def start_or_reset_session(self):
        """Starts a new Firefox session or resets an existing one.

        If a session is already running, it will be closed before starting a new session.
        """
        if self.driver is not None:
            try:
                self.driver.quit()
                print("Sessione esistente chiusa.")
            except WebDriverException:
                print("Nessuna sessione aperta da chiudere.")

        self.driver = webdriver.Firefox(service=self.service, options=self.options)
        print("Nuova sessione avviata.")

    def close_session(self):
        """Closes the current WebDriver session if it is active.

        This method properly shuts down the browser instance and clears the driver reference.
        """
        if self.driver is not None:
            self.driver.quit()
            self.driver = None
            print("Sessione chiusa.")
            
            