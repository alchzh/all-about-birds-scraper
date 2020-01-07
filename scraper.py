from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from markupsafe import Markup

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
    species_info = results["infoCard"].find(class_='species-info')
    species_info.insert(len(species_info.contents), speciesInfoCardContents[1].find("p"))

    results["audio"] = overviewSoup.find(id="jquery_jplayer_audio")["name"]

    # ID
    idURL = urljoin(baseURL, "./id")
    idPage = requests.get(idURL, headers=headers)
    idSoup = BeautifulSoup(idPage.text, "html.parser")

    track = idSoup.find(class_="slider").contents
    results['imgs'] = [{'annotation': Markup(slide.select('.annotation-txt > a')[0]), 'url': processInterchange(slide.find('img')['data-interchange'])} for slide in track]

    try:
        fourKeys = idSoup.find('ul', class_="four-keys").contents
        sizeShape = fourKeys[0].find('article')
        results['sizeShape'] = sizeShape.find('p')
        results['sizeShapeCard'] = removeImg(sizeShape.find(class_='callout'))

        results['colorPattern'] = fourKeys[1].select('div > article > p')[0]
        results['behavior'] = fourKeys[2].select('div > article > p')[0]
        results['habitat'] = fourKeys[3].select('div > article > p')[0]

        results['oldIdForm'] = False
    except AttributeError:
        results['oldIdForm'] = True
        results['idContent'] = removeImg(idSoup.find_all('div', class_='main-column')[-1].find('span'))

    try:
        results['regionalDifferences'] = idSoup.find_all(class_='main-column')[1].find_all('div', recursive=False)[-1].select('article > p')[0]
    except IndexError:
        results['regionalDifferences'] = None

    # lifeHistory
    lhURL = urljoin(baseURL, "./lifehistory")
    lhPage = requests.get(lhURL, headers=headers)
    lhSoup = BeautifulSoup(lhPage.text, "html.parser")

    categoryContent = lhSoup.find('div', class_="category-content").contents
    results['lhHabitat'] = categoryContent[0].find('p').contents[1]
    results['lhFood'] = categoryContent[1].find('p').contents[1]
    try:
        results['lhNestPlacement'] = categoryContent[2].find('p').contents[1]
    except IndexError:
        results['lhNestPlacement'] = None
    results['lhNestDescription'] = categoryContent[2].find_all('p', recursive=False)[1].contents[0]
    results['lhNestFacts'] = categoryContent[2].find('table', class_="callout")
    results['lhBehavior'] = categoryContent[3].find('p').contents[1]
    results['lhConservation'] = categoryContent[4].find('p').contents[1]

    return results

if __name__ == "__main__":
    from jinja2 import Template

    def safeResult(soup):
        return Markup(str(soup))

    with open('birdlist', 'r') as f:
        birds = [(l.split(',')[0], l.split(',')[1].strip().replace("'", '').replace(' ', '_')) for l in f.readlines()]

        for (i, bird) in birds:
            print('scraping', bird)
            url = 'https://www.allaboutbirds.org/guide/{}/'.format(bird)
            
            try:
                arguments = { k: safeResult(v) if isinstance(v, BeautifulSoup) else v for k, v in scrape(url).items() }
                arguments['baseURL'] = url
                output = Template(open('template.html').read()).render(arguments)

                with open('birds/{:03d}_{}.html'.format(int(i), bird), 'w') as outfile:
                    outfile.write(output)
                    print('finished scraping', bird)
            except AttributeError:
                print("Error on {}", bird)


    # print(arguments['imgs'])