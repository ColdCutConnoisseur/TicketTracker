




from selenium import webdriver
from selenium.webdriver.firefox.options import Options



def create_and_return_driver():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    return driver



if __name__ == "__main__":
    d = create_and_return_driver()
    print("Driver returned successfully!")
