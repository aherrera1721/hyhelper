from mechanize import Browser
from bs4 import BeautifulSoup

def get_webwimp(coords):
    """
    Gets the data table produced by WebWIMP (http://climate.geog.udel.edu/~wimp/) at the given coordinates.
    """
    br = Browser()
    url = 'http://climate.geog.udel.edu/~wimp/'

    br.open(url)

    br["yname"] = "Auto WebWimp"

    br.submit()

    br["long"] = str(coords[1])
    br["lati"] = str(coords[0])

    br.submit()

    br.select_form(action="wimp_calc.php")

    webpage = br.submit()

    html = webpage.read()

    bs = BeautifulSoup(html, features="html5lib")
    table = bs.findAll(lambda tag: tag.name == 'table')[2]

    rows = table.findAll('tr')

    data_table = []
    for row in rows:
            cols = row.findAll('td')
            cols = [ele.text.strip() for ele in cols]
            data_table.append([ele for ele in cols if ele])

    return data_table
