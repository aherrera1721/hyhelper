import urllib, os, datetime
from mechanize import Browser

def newpage(br):
    print("Currently at: " + br.geturl())
    br.select_form(nr=0)
    br.set_all_readonly(False)
    br.set_handle_robots(False)

class traj_request():
    """
    traj_request(): Trajectory request package to be used by the get_traj function.
    traj_name: name of the trajectory (string)

    """
    def __init__(self, traj_name, coords, dates, runtime, file_type="gdas1", alts=[500, 1000, 1500], get_reverse = False):
        self.traj_name = traj_name
        self.lat, self.lon = coords[0], coords[1]
        self.years, self.months, self.days, self.hours = dates[0], dates[1], dates[2], dates[3] #days can be in range format or a list of days
        self.runtime = runtime
        self.alts = alts
        self.direction = "Forward" if runtime > 0 else "Backward"
        self.get_reverse = get_reverse
        self.file_type = file_type
    
    def traj_dates(self):
        traj_dates = []
        for y in self.years:
            for m in self.months:
                for d in self.days:
                    for h in self.hours:
                        try:
                            traj_dates.append(datetime.datetime(y, m, d, h))
                        except:
                            pass
        return traj_dates

def week_no(dt):
    return str((int(dt.strftime("%d"))-1)//7 + 1)

def get_season(dt):
    month = dt.strftime("%b")
    if month in ["Jan", "Feb", "Dec"]: return "winter"
    elif month in ["Mar", "Apr", "May"]: return "spring"
    elif month in ["Jun", "Jul", "Aug"]: return "summer"
    elif month in ["Sep", "Oct", "Nov"]: return "autumn"

def get_id(link_url):
    parts = link_url.split(".")
    return parts[1]


def get_traj(traj_req, traj_dump):
    """
    Generates the HySplit trajectory files for the given trajectory request at the given location.
    Will also generate reverse trajectories if the trajectory request says to.
    Uses the web version of HySplit so you do not have to have the GDAS (or other file type) files downloaded.

    **TODO** Fix the reverse trajectory counter.
    """
    count, total = 1, len(traj_req.alts)*len(traj_req.traj_dates()) 
    if not os.path.exists(traj_dump):
        os.makedirs(traj_dump)
    
    if traj_req.get_reverse:
        reverse_traj_requests = []
    
    for alt in traj_req.alts:
        for traj_date in traj_req.traj_dates():
            print("Working on traj #: " + str(count) + "/" + str(total))

            br = Browser()
            br.open("https://www.ready.noaa.gov/hypub-bin/trajtype.pl?runtype=archive")

            newpage(br)

            br["nsrc"] = ["1"] # user input
            br["trjtype"] = ["1"] # user input

            br.submit()
            newpage(br)

            br["SOURCELOC"] = ["decdegree"] # user input
            br["Lat"] = str(traj_req.lat) # user input
            br["Lon"] = str(traj_req.lon) # user input

            br.submit()
            newpage(br)

            file = "gdas1."+traj_date.strftime("%b").lower()+traj_date.strftime("%y")+".w"+week_no(traj_date) # make a function to format file name to clean this up
            br["mfile"] = [file] # user input

            br.submit()
            newpage(br)

            br["direction"] = [traj_req.direction]
            br["Start day"] = [traj_date.strftime("%d")]
            br["duration"] = str(abs(traj_req.runtime))

            if traj_date.hour == 0:
                br["Start hour"] = ["00"]
            else:
                br["Start hour"] = [str(traj_date.hour)]
            br["Source hgt1"] = str(alt)
            br["rain"] = ["1"]

            br.submit()
            newpage(br)


            for link in br.links():
                if "tdump" in link.url:
                    id_ = get_id(link.url)

            alt_str = str(alt)

            while len(alt_str) < 4:
                alt_str = '0'+alt_str

            if not traj_req.traj_name.endswith("REVERSE"):
                filename = os.path.join(traj_dump, traj_req.traj_name +"m"+ traj_date.strftime("%m")+"d"+traj_date.strftime("%d")+"y"+traj_date.strftime("%Y")+"h"+traj_date.strftime("%H"))
            else:
                rev_traj_dump = traj_dump + '/reversetraj'
                if not os.path.exists(rev_traj_dump):
                    os.makedirs(rev_traj_dump)
                filename = os.path.join(rev_traj_dump, traj_req.traj_name)

            data = br.open("https://www.ready.noaa.gov/hypubout/tdump."+id_+".txt").read()
            save = open(filename, 'wb')
            save.write(data)
            save.close()
            
            
            if traj_req.get_reverse:
                f = open(filename, "r")
                for line in f:
                    last_line = line
                rev_coords = (last_line.split()[9], last_line.split()[10])
                rev_start_time = traj_date + datetime.timedelta(hours=traj_req.runtime)
                rev_traj_name = traj_req.traj_name +"m"+ traj_date.strftime("%m")+"d"+traj_date.strftime("%d")+"y"+traj_date.strftime("%Y")+"h"+traj_date.strftime("%H")+"REVERSE"
                rev_runtime = -traj_req.runtime
                rev_dates = [[rev_start_time.year],[rev_start_time.month],[rev_start_time.day],[rev_start_time.hour]]
                rev_file_type = traj_req.file_type
                rev_traj_request = traj_request(rev_traj_name, rev_coords, rev_dates, file_type=rev_file_type, runtime=rev_runtime, alts = [float(last_line.split()[11])])

                reverse_traj_requests.append(rev_traj_request)
            
            count+=1
    
    if traj_req.get_reverse:
        for tr in reverse_traj_requests:
            get_traj(tr, traj_dump)
    
    if not traj_req.get_reverse:
        print("complete")
