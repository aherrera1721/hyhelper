from HyHelper import ONI_webscript, WebWIMP_webscript, KNMI_webscript

def traj_name_filter(traj, string):
    """
    Filter out trajectories that have the given `string` in the `traj.traj_name`
    """
    return string in traj.traj_name

def oni_filter(traj, enso_type="N"):
    """
    Filter out trajectories that have the given ENSO type(s).
    Valid ENSO types include: "WE" (Weak El Niño), "ME" (Moderate El Niño), "SE" (Strong El Niño), "VSE" (Very Strong El Niño),
    "WL" (Weak La Niña), "ML" (Moderate La Niña), "SL" (Strong La Niña), "N" (Neither El Niño or La Niña)
    Data gathered from: https://ggweather.com/enso/oni.htm
    """
    if not isinstance(enso_type, list):
        enso_type = [enso_type]
    
    oni_seasons = ONI_webscript.get_oni_seasons()

    def get_season(traj):
        if traj.target_point.month in range(6, 13):
            season = (traj.target_point.year, traj.target_point.year+1)
        else:
            season = (traj.target_point.year-1, traj.target_point.year)
        return season

    season = get_season(traj)
    oni_season_enso = oni_seasons[season].enso_type

    return oni_season_enso in enso_type

def webwimp_filter(traj, coords, var='SURP'):
    """
    Filter out trajectories that have a non-zero value for the given variable at the given (lon, lat) coordinates.
    Data gathered from: http://climate.geog.udel.edu/~wimp/
    """
    var_to_ind = {
            'TEMP': 1,
            'UPE': 2,
            'APE': 3,
            'PREC': 4,
            'DIFF': 5,
            'ST': 6,
            'DST': 7,
            'AE': 8,
            'DEF': 9,
            'SURP': 10,
            'SMT': 11,
            'SST': 12
        }
    
    webwimp_data = WebWIMP_webscript.get_webwimp(coords)
    return int(webwimp_data[traj.target_point.month][var_to_ind[var]]) != 0
