import os

from selenium.webdriver import Chrome, ChromeOptions

class ChromeDriver(Chrome):
    def __init__(self, profile_dir = None, port=0, service_args=None, desired_capabilities=None, service_log_path=None, chrome_options=None, keep_alive=True):

        if os.environ.get('selenium_driver'):
            executable_path = os.environ.get('selenium_driver')
        else:
            executable_path='chromedriver'

        options = ChromeOptions()

        if profile_dir:
            pathnya = os.path.abspath(profile_dir)
            if not os.path.exists(pathnya):
                os.makedirs(pathnya)
            
            options.add_argument("user-data-dir={}".format(pathnya))

        options.add_argument("start-maximized")
        if os.environ.get('headless'):
            options.add_argument("--headless")

        prefs = { "download.default_directory" : os.path.abspath("./")}
        options.add_experimental_option("prefs",prefs)

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        super().__init__(executable_path=executable_path, port=port, options=options, service_args=service_args, desired_capabilities=desired_capabilities, service_log_path=service_log_path, chrome_options=chrome_options, keep_alive=keep_alive)