import os, urllib
from mechanize import Browser

def get_link(br, chars):
    """
    Returns the Link object that contains the given `chars` characters.
    """
    for link in br.links():
        if chars in link.url:
            correct_link = link
            break
    return correct_link

def get_knmi(coords, name, image_dump, pmin=10, offset=5, fields=["cru4_pre", "era5_tp"], months=["0", "1:12"]):
    """
    Gets the KNMI Climate Explorer generated field correlation pdfs.
    Parameters:
        * `name`: the name of the image set to be used when saving the pdfs
        * `image_dump`: the directory to which to save the pdfs to
        * `pmin`: the cutoff p-value for the correlation
        * `offset`: how much to offset the corners of the correlation grid box from the original input coordinates
        * `fields`: the field(s) used for the correlations ("cru4_pre" is CRU TS 4.03 (land) 0.5; "era5_tp" is ERA5 surface precipitation)
        * `months`: the month(s) for which to correlate over ("1:12" is all months separately; "0" is all months together)
    """
    
    if not os.path.exists(image_dump):
        os.makedirs(image_dump)

    url = "https://climexp.knmi.nl/start.cgi"
    br = Browser()

    br.open(url)

    for field in fields:
        if "cru4" in field:
            br.follow_link(get_link(br, "selectfield_obs2.cgi"))
            br.follow_link(get_link(br, "field={}".format(field)))

        elif "era5" in field:
            br.follow_link(get_link(br, "selectfield_rea.cgi"))
            br.select_form(action="select.cgi")
            br["field"] = [field]
            br.submit()

        br.select_form(action="get_index.cgi")

        br["lat1"] = str(coords[0])
        br["lon1"] = str(coords[1])

        br.submit()

        correlate_link = get_link(br, "corfield.cgi")

        total, count = 0, 1
        for month in months:
            if month == "1:12":
                total += 12
            else:
                total += 1

        for month in months:
            br.follow_link(correlate_link)

            br.select_form(action="correlate.cgi")
            
            br["field"] = [field]

            br["lat1"] = str(coords[0]-offset)
            br["lat2"] = str(coords[0]+offset)
            br["lon1"] = str(coords[1]-offset)
            br["lon2"] = str(coords[1]+offset)

            br["month"] = [month]

            br["pmin"] = str(pmin)

            br.submit()

            pdf_links = []
            for link in br.links():
                if "pdf" in link.url:
                    pdf_links.append(link)
            
            for pdf_link in pdf_links:
                br.follow_link(pdf_link)
                print("Generating {} image # {}/{}".format(field, count, total))
                file_path = os.path.join(image_dump, "_".join([name, field, str(count)]))
                for link in br.links():
                    if "pdf" in link.url:
                        pdf = link
                        break
            
                urllib.request.urlretrieve("https://climexp.knmi.nl/" + pdf.url, file_path)
                count += 1

    return "Complete! Find files at {}".format(image_dump)