from mechanize import Browser
from bs4 import BeautifulSoup

def get_webwimp(coords): ## coords is (lat, lon)
    """
    Gets the data table produced by WebWIMP (http://climate.geog.udel.edu/~wimp/) at the given coordinates.
    """
    br = Browser()
    url = 'http://climate.geog.udel.edu/~wimp/'

    webpage = br.open(url)
    br.select_form(action='http://climate.geog.udel.edu/~wimp/wimp_map.php')
    br["yname"] = "Auto WebWimp"

    webpage = br.submit()
    br.select_form('wimp_lonlat')
    br["long"] = str(coords[1])
    br["lati"] = str(coords[0])

    webpage = br.submit()

    html = webpage.read()
    if b'This location falls on a large body of water' in html:
        raise ValueError('This location falls on a large body of water!')
    else:
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
