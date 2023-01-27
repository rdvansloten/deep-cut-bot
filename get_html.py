import requests
from bs4 import BeautifulSoup

def get_weapon_description(url):
  soup = BeautifulSoup(requests.get(url).text, 'html.parser')
  content = soup.find("div", {"id": "mw-content-text"})
  message = ""

  for p in content.find_all("p")[:2]:
      message += p.text

  return f"{message[:128]}..."  