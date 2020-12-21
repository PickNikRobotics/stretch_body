import threading


def generate_segment_coeffs(w0, w1):
    coeffs = []

    if w0.velocity == None or w1.velocity == None:
        pass
    elif w0.acceleration == None or w1.acceleration == None:
        pass
    else:
        c0 = w0.position
        c1 = w0.velocity
        c2 = w0.acceleration / 2
        c3 = (20 * w1.position - 20 * w0.position - (8 * w1.velocity + 12 * w0.velocity) * (w1.time - w0.time) - (3 * w0.acceleration - w1.acceleration) * ((w1.time - w0.time) ** 2) ) / (2 * ((w1.time - w0.time) ** 3) )
        c4 = (30 * w0.position - 30 * w1.position + (14 * w1.velocity + 16 * w0.velocity) * (w1.time - w0.time) + (3 * w0.acceleration - 2 * w1.acceleration) * ((w1.time - w0.time) ** 2) ) / (2 * ((w1.time - w0.time) ** 4) )
        c5 = (12 * w1.position - 12 * w0.position - (6 * w1.velocity + 6 * w0.velocity) * (w1.time - w0.time) - (w0.acceleration - w1.acceleration) * ((w1.time - w0.time) ** 2) ) / (2 * ((w1.time - w0.time) ** 5) )

        coeffs = [c0, c1, c2, c3, c4, c5]

    return coeffs


class Waypoint():

    def __init__(self, time, position, velocity=None, acceleration=None, effort_threshold=None):
        self.is_executing = False
        self.time = time
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration
        self.effort_threshold = effort_threshold


class Trajectory():

    def __init__(self):
        self.traj_lock = threading.RLock()
        self.waypoints = []
        self.contact_cb = None

    def add_waypoint(self, time, position, velocity=None, acceleration=None, effort_threshold=None):
        with self.traj_lock:
            self.waypoints.append(Waypoint(time, position, velocity, acceleration, effort_threshold))

    def dequeue_waypoint(self):
        with self.traj_lock:
            return self.waypoint.pop(0)

    def get_waypoint(self, index):
        with self.traj_lock:
            return self.waypoints[index]

    def delete_waypoint(self, index):
        with self.traj_lock:
            if index >= 0 and index < len(self.waypoints):
                return self.waypoints.pop(index)

    def generate_segment(self):
        with self.traj_lock:
            if len(self.waypoints) < 2:
                return None

            if self.waypoints[0].is_executing == True:
                self.delete_waypoint(0)

            self.waypoints[0].is_executing = True
            self.waypoints[1].is_executing = True
            return generate_segment_coeffs(self.waypoints[0], self.waypoints[1])

    def register_contact_cb(self, func):
        with self.traj_lock:
            self.contact_cb = func


class JointTrajectory():

    def __init__(self, devices):
        pass

    def active_joints(self):
        pass

    def execute_trajectories(self):
        pass

    def cancel_trajectories(self):
        pass
