from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient

def test_setup():
    print("Testing dependencies...")
    
    # Test MongoDB connection
    try:
        client = MongoClient('localhost', 27017)
        print("MongoDB connection successful!")
    except Exception as e:
        print(f"MongoDB connection failed: {str(e)}")
        print("Make sure MongoDB is installed and running.")
    
    # Test Selenium/ChromeDriver
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.get("https://www.python.org")
        print(f"Selenium working! Page title: {driver.title}")
        driver.quit()
    except Exception as e:
        print(f"Selenium setup failed: {str(e)}")
    
    print("Setup test complete!")

if __name__ == "__main__":
    test_setup()
