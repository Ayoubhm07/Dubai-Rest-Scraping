Project: Real Estate Transaction Retrieval

Description:
This project is designed to automate the weekly retrieval of real estate transactions from the DXB Interacts and Dubai Rest websites. The automation process includes converting PDF data into CSV format (specifically for data from the DXB Interacts site), followed by the cleansing and structuring of the data in an Excel spreadsheet. The automation is performed asynchronously to optimize efficiency and resource management. Additionally, the project is containerized using Docker to facilitate deployment and ensure a consistent runtime environment.

Technologies Used:

Python: The primary programming language for scripting and automating tasks.
Selenium: Automation tool used to simulate user interactions on the target website and download PDF files.
Pandas: Python library for manipulating and cleaning CSV data.
OpenPyXL: Python library for creating and modifying Excel files.
Docker: Containerization platform to encapsulate and deploy the application across different environments.
Flask: Web framework used for building backend APIs.
Celery: Manages asynchronous and scheduled tasks.
Redis: Acts as a broker server for Celery and stores task results.
Webdriver Manager: Automatically manages browser drivers.
Prerequisites:

Docker installed on your machine.
Internet access to retrieve data from the DXB Interacts site.
Installation of dependencies.
Project Structure:

/sweetchome-scrapping
|-- app/
| |-- init.py
| |-- celery_instance.py
| |-- celery_utils.py
| |-- tasks.py
| |-- views.py
|
|-- data_converter/
| |-- pdf-fetch.py
  |-- amount-avrg.py
|
|
|-- selenium_scripts/
| |-- scrapper.py
| |-- dr-scrapper.py
|
|
|-- main.py
|-- config.py
|-- Dockerfile
|-- requirements.txt

Installation:

bash
Copy code
pip install -r requirements.txt
python main.py