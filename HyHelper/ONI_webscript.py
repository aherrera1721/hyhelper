from mechanize import Browser
from bs4 import BeautifulSoup

def get_data():
    """
    Gets the Running 3-Month Mean ONI values table from: https://ggweather.com/enso/oni.htm
    """
    br = Browser()
    url = 'https://ggweather.com/enso/oni.htm'
    webpage = br.open(url)
    html = webpage.read()

    bs = BeautifulSoup(html, features="html5lib")
    table = bs.find(lambda tag: tag.name=='table' and tag.has_attr('width') and tag['width']=='930')
    rows = table.findAll('tr')

    data_table = []
    for row in rows:
        cols = row.findAll('td')
        cols = [ele.text.strip() for ele in cols]
        data_table.append([ele for ele in cols])
    
    return data_table

class ONI_Season():
    """
    Class to represent a season of 3-month mean ONI values. An ONI season starts in July and ends in June.
    """
    def __init__(self, data):
        """
        Initializes a new instance of `ONI_Season` to have the following key attributes:
            * `enso_type`
            * `season`
            * `oni_vals`

        Parameters:
            * data (list): a row from the Running 3-Month Mean ONI values table from: https://ggweather.com/enso/oni.htm
        """
        self.enso_type = data[0] if data[0] else "N"
        self.season = (float(data[1]), float(data[3]))
        self.oni_vals = {
            "JJA": float(data[4]) if data[4] else None,
            "JAS": float(data[5]) if data[5] else None,
            "ASO": float(data[6]) if data[6] else None,
            "SON": float(data[7]) if data[7] else None,
            "OND": float(data[8]) if data[8] else None,
            "NDJ": float(data[9]) if data[9] else None,
            "DJF": float(data[10]) if data[10] else None,
            "JFM": float(data[11]) if data[11] else None,
            "FMA": float(data[12]) if data[12] else None,
            "MAM": float(data[13]) if data[13] else None,
            "AMJ": float(data[14]) if data[14] else None,
            "MJJ": float(data[15]) if data[15] else None,
        }

def get_oni_seasons():
    """
    Gets the Running 3-Month Mean ONI values from: https://ggweather.com/enso/oni.htm as instances of ONI_Season.
    Returns a dictionary mapping season years (e.g., (1950, 1951)) to its respective ONI_Season instance.
    """
    data_table = get_data()
    oni_seasons = dict()
    for data in data_table[2::]:
        oni_season = ONI_Season(data)
        oni_seasons[oni_season.season] = oni_season
    return oni_seasons
