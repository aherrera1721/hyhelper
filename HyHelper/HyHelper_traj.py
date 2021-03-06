import os, shutil, datetime
from .WebWIMP_webscript import *

"""
HyHelper (Hysplit Helper) is a Python framework designed to make understanding and organizing Hysplit trajectory endpoint files easy.
(See: https://www.ready.noaa.gov/HYSPLIT_traj.php for more info.)
The goal of HyHelper is to provide a workflow foundation for effective trajectory file manipulation and management.
HyHelper reads trajectory files and stores their information in simple and intuitive objects.
"""

class Point():
    """
    Class to represent the points that make up a trajectory.
    """
    def __init__(self, traj, line, data_dict):
        """
        Initializes a new instance of `Point` to have the following attributes:
            * `traj`, `line`, `data_dict`
            * `traj_num`, `grid_num`
            * `year`, `month`, `day`, `hour`, `minute`, `datetime`
            * `forecast_hour`, `traj_age`
            * `lat`, `lon`, `coords`, `height`
            * `data`

        Parameters:
            traj (Traj): The trajectory to which the point belongs to.
            line (list): The components of the trajectory file line that corresponds to this point.
            data_dict (dict): A dictionary mapping indices to the variable trajectory data.
        """
        ## init params ##
        self.traj = traj
        self.line = line
        self.data_dict = data_dict
        
        ## misc ##
        self.traj_num = line[0]
        self.grid_num = line[1]

        ## time ##
        self.year = int(line[2]) + 2000
        self.month = int(line[3])
        self.day = int(line[4])
        self.hour = int(line[5])
        self.minute = int(line[6])
        self.datetime = datetime.datetime(self.year, self.month, self.day, self.hour, self.minute)
        self.forecast_hour = int(line[7])
        self.traj_age = float(line[8])
    
        ## geo / meteo ##
        self.lat = float(line[9])
        self.lon = float(line[10])
        self.coords = (float(line[9]), float(line[10]))
        self.height = float(line[11])

        ## data, including height ##
        self.data = {data_dict[ind]: float(val) for ind, val in enumerate(line[12::])}
    
    def __str__(self):
        return "{} {}".format(self.coords, self.datetime)
    
    def __repr__(self):
        return "Point({}, {}, {})".format(self.traj, self.line, self.data_dict)

class Traj():
    """
    Class to interpret and represent a trajectory file generated by Hysplit. No information from the trajectory files is lost.
    For more information, reference: https://www.ready.noaa.gov/hypub/trajinfo.html#FORMAT
    """
    def __init__(self, traj_path):
        """
        Initializes a new instance of `Traj` to have the following attributes:
            * `traj_path`, `traj_name`
            * `num_grids`, `format_type`
            * `file_ids`
            * `num_trajs`, `direction`, `method`
            * `starting_info`
            * `num_vars`, `vars`
            * `points`, `coords_to_point`, `num_points`
            * `start_point`, `end_point`, `target_point`
            * `min_vals`, `max_vals`, `total_vals`
        
        Parameters:
            traj_path (raw str): The trajectory file path.
        """
        self.traj_path = traj_path
        self.traj_name = os.path.basename(os.path.normpath(traj_path))

        with open(traj_path, 'r') as traj_file:

            ## record 1 ##
            r1_line = traj_file.readline().split()
            self.num_grids= int(r1_line[0])
            self.format_type = "old" if len(r1_line) == 1 else "new"

            ## record 2 ##
            self.file_ids = []
            for g in range(self.num_grids):
                r2_line = traj_file.readline().split()
                self.file_ids.append(r2_line)
            
            ## record 3 ##
            r3_line = traj_file.readline().split()
            self.num_trajs = int(r3_line[0])
            self.direction = r3_line[1]
            self.method = r3_line[2]
            
            ## record 4 ##
            self.starting_info = []
            for t in range(self.num_trajs):
                r4_line = traj_file.readline().split()
                self.starting_info.append(r4_line)
            
            ## record 5 ##
            r5_line = traj_file.readline().split()
            self.num_vars = int(r5_line[0])
            self.vars = r5_line[1::]
            data_dict = {ind: var for ind, var in enumerate(self.vars)}
    
            ## record 6 ##
            self.points = []
            self.coords_to_point = dict() ## we assume each point along the trajectory has a unique location (safe assumption) ##
            for line in traj_file:
                r6_line = line.split()
                point = Point(self, r6_line, data_dict)
                self.points.append(point)
                self.coords_to_point[(point.lat, point.lon)] = point
            self.num_points = len(self.points)
            
        ## other ##
        self.start_point = self.points[0]
        self.end_point = self.points[-1]
        self.target_point = self.start_point if self.direction == "BACKWARD" else self.end_point

        self.min_vals, self.max_vals = {var: self.start_point.data[var] for var in self.vars}, {var: self.start_point.data[var] for var in self.vars}
        self.total_vals = {var: 0 for var in self.vars}
        for point in self.points:
            for var in self.vars:
                val = point.data[var]
                if val < self.min_vals[var]:
                    self.min_vals[var] = val
                if val > self.max_vals[var]:
                    self.max_vals[var] = val
                self.total_vals[var] += val
    
    def __str__(self):
        return "Traj '{}' ({} points)".format(self.traj_name, self.num_points)

    def __repr__(self):
        return "Traj({})".format(self.traj_path)

    def __iter__(self):
        """
        Traj iterates through Point instances that make it up.
        """
        return iter(self.points)

    def __eq__(self, other):
        if not isinstance(other, Traj):
            return NotImplemented
        return self.traj_path == other.traj_path

    def get_total(self, var):
        """
        Gets the total value of the given variable along the trajectory.
        """
        return self.total_vals[var]
    
    def get_point_from_loc(self, coords):
        lat, lon = coords[0], coords[1]
        return self.coords_to_point[(lat, lon)]
    
    def nonzero_points(self, var):
        """
        Returns the points that have a non-zero value for the given variable.
        """
        nonzero_points = []
        for point in self.points:
            if point.data[var] != 0:
                nonzero_points.append(point)
        return nonzero_points

class Traj_Group():
    """
    Class to represent a group of trajectories generated by Hysplit.
    """
    def __init__(self, group_name, group_members):
        """
        Initializes a new instance of `Traj_Group` to have the following attributes:
            * `group_name`, `group_members`
            * `trajs`, `traj_count`
        
        Parameters:
            group_name (str): The trajectory group name.
            group_members: Possible arguments are a raw string denoting a trajectory filepath/directory, a Traj instance, or a Traj_Group instance. Or any combination of these in a list.
        """
        self.group_name = group_name
        if not isinstance(group_members, list):
            self.group_members = [group_members]
        else:
            self.group_members = group_members

        def get_trajs(path):
            if os.path.isfile(path):
                try:
                    trajs = [Traj(path)]
                except:
                    print("File at [{}] not identified as a valid trajectory.".format(path))
            
            elif os.path.isdir(path):
                trajs = []
                for file_name in os.listdir(path):
                    sub_path = os.path.join(path, file_name)
                    if os.path.isfile(sub_path):
                        try:
                            trajs.append(Traj(sub_path))
                        except:
                            print("File at [{}] not identified as a valid trajectory.".format(sub_path))
            
            return trajs

        self.trajs = []
        for member in self.group_members:
            if isinstance(member, Traj):
                traj = member
                if traj not in self.trajs:
                    self.trajs.append(member)
    
            elif isinstance(member, Traj_Group):
                for traj in member.trajs:
                    if traj not in self.trajs:
                        self.trajs.append(traj)
            else:
                new_trajs = get_trajs(member)
                for traj in new_trajs:
                    if traj not in self.trajs:
                        self.trajs.append(traj)

        self.traj_count = len(self.trajs)

        self.min_vals, self.max_vals, self.total_vals = dict(), dict(), dict()
        for traj in self.trajs:
            for var, val in traj.min_vals.items():
                if var not in self.min_vals:
                    self.min_vals[var] = val
                elif val < self.min_vals[var]:
                    self.min_vals[var] = val

            for var, val in traj.max_vals.items():
                if var not in self.max_vals:
                    self.max_vals[var] = val
                elif val > self.max_vals[var]:
                    self.max_vals[var] = val
            
            for var, val in traj.total_vals.items():
                if var not in self.total_vals:
                    self.total_vals[var] = val
                else:
                    self.total_vals[var] += val
    
    def __str__(self):
        return "Traj_Group '{}' ({} trajectories).".format(self.group_name, self.traj_count)
    
    def __repr__(self):
        return "Traj_Group({}, {})".format(self.group_name, self.group_members)

    def __iter__(self):
        """
        Traj_Group iterates through the Traj instances that make it up.
        """
        return iter(self.trajs)

    def __add__(self, other):
        if not isinstance(other, Traj_Group):
            return NotImplemented
        new_name = "_".join([self.group_name, "plus", other.group_name])
        new_members = self.trajs + other.trajs
        return Traj_Group(new_name, new_members)

    
    def __sub__(self, other):
        if not isinstance(other, Traj_Group):
            return NotImplemented
        new_name = "_".join([self.group_name, "minus", other.group_name])
        new_members = list(self.trajs)
        

        for traj in other.trajs:
            if traj in new_members:
                new_members.remove(traj)

        return Traj_Group(new_name, new_members)
        
    def __eq__(self, other):
        if not isinstance(other, Traj_Group):
            return NotImplemented
        if len(self.trajs) != len(other.trajs):
            return False
        self_traj_paths = [traj.traj_path for traj in self.trajs]
        other_traj_paths = [traj.traj_path for traj in other.trajs]
        self_traj_paths.sort()
        other_traj_paths.sort()
        return self_traj_paths == other_traj_paths

    def set_name(self, name):
        self.group_name = name
        return self.group_name

    def save_group(self, location, name=None):
        """
        Save the trajectories in a trajectory group to the given location.
        Returns `save_path`, the new save directory.
        """
        if not name:
            name = self.group_name

        save_path = os.path.join(location, name)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
    
        for traj in self.trajs:
            shutil.copy(traj.traj_path, save_path)
        
        return save_path
    
    def filter_group(self, traj_group_filter, location, filter_name=None, diff=False, move=False, filter_args=list(), filter_kwargs=dict()):
        """
        Creates a folder at the given `location` directory with the trajectories in the group that satisfy the `traj_group_filter` function.
        Parameter `diff` can be set to True to generate the difference trajectory group at the given `location` directory.
        Parameter `move` can be set to True to move the files to the new directories instead of copying them over.
        Create your own filter and use it here!

        Working on support for a cache in case a filter requires heavy computation (like generating a data table every time).
        
        Returns instances of `Traj_Group` with the filtered and difference trajectories (if both are generated).

        **NOTE** It is very important to ensure the `traj` is the first argument in your `traj_group_filter` function
        """

        if filter_name == None:
            filter_name = traj_group_filter.__name__
        
        if filter_name == "webwimp_filter":
            webwimp_data = get_webwimp(filter_args[0])
        
        filter_group_name = "_".join([self.group_name, filter_name])
        filter_dir = os.path.join(location, filter_group_name)
        if not os.path.exists(filter_dir):
            os.makedirs(filter_dir)

        if diff:
            diff_group_name = "_".join([filter_group_name, "diff"])
            diff_dir = os.path.join(location, diff_group_name)
            if not os.path.exists(diff_dir):
                os.makedirs(diff_dir)
        
        for traj in self.trajs:
            if filter_name == "webwimp_filter":
                filter_kwargs["webwimp_data"] = webwimp_data
            if traj_group_filter(traj, *filter_args, **filter_kwargs):
                if move:
                    shutil.move(traj.traj_path, filter_dir)
                else:
                    shutil.copy(traj.traj_path, filter_dir)
            elif diff:
                if move:
                    shutil.move(traj.traj_path, diff_dir)
                else:
                    shutil.copy(traj.traj_path, diff_dir)
        
        if not diff:
            return (Traj_Group(filter_group_name, filter_dir), None)

        return (Traj_Group(filter_group_name, filter_dir), Traj_Group(diff_group_name, diff_dir))
    
    def get_total(self, var):
        """
        Gets the total value of the given variable along all trajectories in the trajectory group.
        """
        return self.total_vals[var]
