import yaml
import math
import os
import time


def print_stretch_re_use():
    print("For use with S T R E T C H (TM) RESEARCH EDITION from Hello Robot Inc.\n")

def create_time_string():
    t = time.localtime()
    time_string = str(t.tm_year) + str(t.tm_mon).zfill(2) + str(t.tm_mday).zfill(2) + str(t.tm_hour).zfill(2) + str(t.tm_min).zfill(2) + str(t.tm_sec).zfill(2)
    return time_string


def deg_to_rad(x):
    return math.pi*x/180.0

def rad_to_deg(x):
    return 180.0*x/math.pi


def get_fleet_id():
    return os.environ['HELLO_FLEET_ID']

def set_fleet_id(id):
    os.environ['HELLO_FLEET_ID']=id

def get_fleet_directory():
    return os.environ['HELLO_FLEET_PATH']+'/'+get_fleet_id()+'/'

def read_fleet_yaml(fn):
    s = file(get_fleet_directory()+fn, 'r')
    p = yaml.load(s,Loader=yaml.FullLoader)
    if p is None:
        return {}
    else:
        return p

def write_fleet_yaml(fn,rp):
    with open(get_fleet_directory()+fn, 'w') as yaml_file:
        yaml.dump(rp, yaml_file, default_flow_style=False)

class TimerStats():
    def __init__(self):
        self.av = None
        self.mx = None
        self.count = 0


    def update(self, duration):
        if self.av is None:
            self.av = duration
        else:
            self.av = ((self.count * self.av) + duration) / (self.count + 1)
            
        if self.mx is None:
            self.mx = duration
        elif self.mx < duration:
            self.mx = duration

        self.count = self.count + 1

    def output_string(self):
        out = 'timer: av = ' + str(self.av) + ' , max = ' + str(self.mx)
        return out

    def pretty_print(self):
        print 'Timer Stat -- Avg: ', str(self.av), 'Max: ', str(self.mx)

    
class ThreadServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass


#Signal handler, must be set from main thread
def thread_service_shutdown(signum, frame):
    print('Caught signal %d' % signum)
    raise ThreadServiceExit


def generate_quintic_spline_coeffs(waypoints):
    coeffs = np.empty([waypoints.shape[0] - 1, 6])
    for j in range(waypoints.shape[0] - 1):
        i = waypoints[j]
        f = waypoints[j+1]
        coeffs[j][0] = i[1]
        coeffs[j][1] = i[2]
        coeffs[j][2] = i[3] / 2
        coeffs[j][3] = (20 * f[1] - 20 * i[1] - (8 * f[2] + 12 * i[2]) * (f[0] - i[0]) - (3 * i[3] - f[3]) * ((f[0] - i[0]) ** 2) ) / (2 * ((f[0] - i[0]) ** 3) )
        coeffs[j][4] = (30 * i[1] - 30 * f[1] + (14 * f[2] + 16 * i[2]) * (f[0] - i[0]) + (3 * i[3] - 2 * f[3]) * ((f[0] - i[0]) ** 2) ) / (2 * ((f[0] - i[0]) ** 4) )
        coeffs[j][5] = (12 * f[1] - 12 * i[1] - (6 * f[2] + 6 * i[2]) * (f[0] - i[0]) - (i[3] - f[3]) * ((f[0] - i[0]) ** 2) ) / (2 * ((f[0] - i[0]) ** 5) )

    return coeffs
