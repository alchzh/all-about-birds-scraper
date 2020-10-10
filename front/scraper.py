from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from markupsafe import Markup

import requests_cache

requests_cache.install_cache('allaboutbirds_cache_10102020')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0'
}

def removeImg(soup):
    for img in soup.find_all('img'):
        img.decompose()
    for img in soup.find_all(class_='icon'):
        img.decompose()
    for img in soup.find_all(class_='silo-group'):
        img.decompose()
    return soup

def processInterchange(di):
    return di.split(", ")[0][1:]

def scrape(baseURL):
    results = {}

    # Overview
    overviewURL = urljoin(baseURL, "./overview")
    overview = requests.get(overviewURL, headers=headers)
    overviewSoup = BeautifulSoup(overview.text, "html.parser")

    speciesInfoCardContents = overviewSoup.find(class_="speciesInfoCard").contents
    results["infoCard"] = removeImg(speciesInfoCardContents[0])
    results["speciesInfo"] = results["infoCard"].find(class_='species-info')

    results["migMap"] = processInterchange(overviewSoup.select_one(".narrow-content > div > a > img")['data-interchange'])

    # ID
    idURL = urljoin(baseURL, "./id")
    idPage = requests.get(idURL, headers=headers)
    idSoup = BeautifulSoup(idPage.text, "html.parser")

    track = idSoup.find(class_="slider").contents
    results['imgs'] = [{'annotation': Markup(slide.select_one('.annotation-txt h3')), 'url': processInterchange(slide.find('img')['data-interchange'])} for slide in track[:3]]

    return results

if __name__ == "__main__":
    import sys
    sys.setrecursionlimit(10000)

    from jinja2 import Environment, FileSystemLoader
    import json

    with open("template.html") as f:
        template_str = f.read()
    template = Environment(loader=FileSystemLoader(".")).from_string(template_str)

    def safeResult(soup):
        return Markup(str(soup))

    with open('birds.json', 'r') as f:
        birds = json.load(f)

        for bird in birds["species"].values():
            print('scraping', bird["commonName"])
            url = 'https://www.allaboutbirds.org/guide/{}/'.format(bird["commonName"].replace(" ", "_").replace("'",""))
            
            bird["templateData"] = { k: safeResult(v) if isinstance(v, BeautifulSoup) else v for k, v in scrape(url).items() }
    
        import pickle

        pickle.dump(birds, open("birds.p", "wb"))

        with open('index.html', 'w') as outfile:
            outfile.write(template.render(birds))


    # print(arguments['imgs'])