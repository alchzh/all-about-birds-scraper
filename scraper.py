from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0'
}


def scrape(baseURL):
    results = {}

    # Overview
    overviewURL = urljoin(baseURL, "./overview")
    overview = requests.get(overviewURL, headers=headers)
    overviewSoup = BeautifulSoup(overview.text, "html.parser")

    speciesInfoCardContents = overviewSoup.find(class_="speciesInfoCard").contents
    results["infoCard"] = speciesInfoCardContents[0]
    results["basicDesc"] = speciesInfoCardContents[1].find("p")

    results["audio"] = overviewSoup.find(id="jquery_jplayer_audio")["name"]

    # ID
    idURL = urljoin(baseURL, "./id")
    idPage = requests.get(idURL, headers=headers)
    idSoup = BeautifulSoup(idPage.text, "html.parser")

    fourKeys = idSoup.find('ul', class_="four-keys").contents
    sizeShape = fourKeys[0].find('article')
    results['sizeShape'] = sizeShape.find('p')
    results['sizeShapeCard'] = sizeShape.find(class_='callout')

    results['colorPattern'] = fourKeys[1].select('div > article > p')
    results['behavior'] = fourKeys[2].select('div > article > p')
    results['habitat'] = fourKeys[3].select('div > article > p')

    results['regionalDifferences'] = idSoup.find_all(class_='main-column')[1].find_all('div', recursive=False)[-1].select('article > p')

    # lifeHistory
    lhURL = urljoin(baseURL, "./lifehistory")
    lhPage = requests.get(lhURL, headers=headers)
    lhSoup = BeautifulSoup(lhPage.text, "html.parser")

    categoryContent = lhSoup.find('div', class_="category-content").contents
    results['lhHabitat'] = categoryContent[0].find('p').contents[1]
    results['lhFood'] = categoryContent[1].find('p').contents[1]
    results['lhNestPlacement'] = categoryContent[2].find('p').contents[1]
    results['lhNestDescription'] = categoryContent[2].find_all('p', recursive=False)[1].contents[1]
    results['lhNestFacts'] = categoryContent[2].find('table', class_="callout")
    results['lhBehavior'] = categoryContent[3].find('p').contents[1]
    results['lhConservation'] = categoryContent[4].find('p').contents[1]

    return results

if __name__ == "__main__":
    import sys

    print(scrape(sys.argv[1]))
