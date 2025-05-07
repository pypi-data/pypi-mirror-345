import requests
from ._dividentifiers import extract_elements


def div_identifier(header,content, div_class):
    try:
        element = extract_elements(Main_header = header, webcontent=content, div_class=div_class).json()['webpage_elements']
        return element
    except Exception as e:
        print(f"Error: {e}")
        return None

def element_miner(header, content, xpath, selector):
    try:
        element = extract_elements(Main_header = header, webcontent=content, div_class=xpath).json()[selector]
        return element
    except Exception as e:
        print(f"Error: {e}")
        return None

##################### Old packages ############################
def Romulus(header, html, div_class):
    if html is None:
        element_name = extract_elements(Main_header = header, webcontent=html, div_class=div_class).json()['webpage_elements']
        return element_name['div5']
    else:
        raise ValueError("Invalid HTML content")

def Marcius(header, webelements, div_class):
    if webelements is not None:
        element_name = extract_elements(Main_header = header, webcontent=webelements, div_class=div_class).json()['webpage_elements']
        return element_name['div6']
    else:
        raise ValueError("Invalid HTML content")
    
def navigator(header, elements, div_class):
    if elements is not None:
        element_name = extract_elements(Main_header = header, webcontent=elements, div_class=div_class).json()['webpage_elements']
        return element_name['div7']
    else:
        raise ValueError("Invalid HTML content")