import threading


def generate_segment_coeffs(w0, w1):
    coeffs = None

    if w0.velocity == None or w1.velocity == None:
        c0 = w0.position
        c1 = 0.0
        c2 = ((3 * w1.position - 3 * w0.position) / ((w1.time - w0.time) ** 2) )
        c3 = - ((2 * w1.position - 2 * w0.position) / ((w1.time - w0.time) ** 3) )

        coeffs = [c0, c1, c2, c3]
    elif w0.acceleration == None or w1.acceleration == None:
        c0 = w0.position
        c1 = w0.velocity
        c2 = ((3 * w1.position - 3 * w0.position) / ((w1.time - w0.time) ** 2) ) - ((2 * w0.velcity) / (w1.time - w0.time) ) - ((w1.velocity) / (w1.time - w0.time) )
        c3 = - ((2 * w1.position - 2 * w0.position) / ((w1.time - w0.time) ** 3) ) + ((w1.velocity + w0.velocity) / ((w1.time - w0.time) ** 2) )

        coeffs = [c0, c1, c2, c3]
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
            if index >= 0 and index < len(self.waypoints)
                and self.waypoints[index].is_executing == False:
                return self.waypoints.pop(index)

    def generate_segment(self):
        with self.traj_lock:
            if len(self.waypoints) < 2:
                return None

            if self.waypoints[0].is_executing == True:
                self.waypoints[0].is_executing = False
                self.delete_waypoint(0)

            self.waypoints[0].is_executing = True
            self.waypoints[1].is_executing = True
            return generate_segment_coeffs(self.waypoints[0], self.waypoints[1])

    def register_contact_cb(self, func):
        with self.traj_lock:
            self.contact_cb = func


class JointTrajectory():

    def __init__(self, devices):
        self.lift = Trajectory()
        self.arm = Trajectory()
        self.base_translation = Trajectory()
        self.base_rotation = Trajectory()
        for joint in self.devices['head'].joints:
            setattr(self, joint, Trajectory())
        for joint in self.devices['end_of_arm'].joints:
            setattr(self, joint, Trajectory())

    def execute(self):
        pass

    def cancel(self):
        pass
