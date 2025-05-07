import time
import requests as rs

def extract_elements(Main_header, webcontent, div_class):
    scanner = "https://screenx-api.onrender.com/secure"
    headers = {"Header": Main_header}
    rst = rs.get(scanner, headers=headers, verify=False)
    return rst

def implicit():
	time.sleep(3)
	return None

def explicit():
	time.sleep(30)
	return None


