from selenium.webdriver.chrome import options, service
from webdriver_manager.chrome import ChromeDriverManager

# Chrome Driver Service and Options
OPTIONS = options.Options()
OPTIONS.add_argument("--disable-dev-shm-usage")
SERVICE = service.Service(ChromeDriverManager().install())
