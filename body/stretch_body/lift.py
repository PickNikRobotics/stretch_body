from stretch_body.stepper import *
from stretch_body.device import Device
from stretch_body.trajectory_managers import StepperTrajectoryManager
import time

class Lift(Device, StepperTrajectoryManager):
    """
    API to the Stretch RE1 Lift
    """
    def __init__(self):
        Device.__init__(self)
        StepperTrajectoryManager.__init__(self)
        self.name='lift'
        self.params=self.robot_params[self.name]
        self.motor = Stepper('/dev/hello-motor-lift', self)
        self.status = {'timestamp_pc':0,'pos': 0.0, 'vel': 0.0, 'force':0.0,'motor': self.motor.status}
        # Default controller params
        self.stiffness = 1.0
        self.i_feedforward=self.params['i_feedforward']
        self.vel_r = self.translate_to_motor_rad(self.params['motion']['default']['vel_m'])
        self.accel_r = self.translate_to_motor_rad(self.params['motion']['default']['accel_m'])
        self.i_contact_neg = self.translate_force_to_motor_current(self.params['contact_thresh_N'][0])
        self.i_contact_pos = self.translate_force_to_motor_current(self.params['contact_thresh_N'][1])
        self.motor.set_motion_limits(self.translate_to_motor_rad(self.params['range_m'][0]), self.translate_to_motor_rad(self.params['range_m'][1]))
    # ###########  Device Methods #############

    def startup(self):
        self.motor.startup()

    def stop(self):
        self.motor.stop() #Maintain current mode

    def pull_status(self):
        self.motor.pull_status()
        self.status['timestamp_pc'] = time.time()
        self.status['pos']= self.motor_rad_to_translate(self.status['motor']['pos'])
        self.status['vel'] = self.motor_rad_to_translate(self.status['motor']['vel'])
        self.status['force'] = self.motor_current_to_translate_force(self.status['motor']['current'])

    def push_command(self):
        self.motor.push_command()

    def pretty_print(self):
        print '----- Lift ------ '
        print 'Pos (m): ', self.status['pos']
        print 'Vel (m/s): ', self.status['vel']
        print 'Force (N): ', self.status['force']
        print 'Timestamp PC (s):', self.status['timestamp_pc']
        #self.motor.pretty_print()

    # ###################################################

    def move_to(self,x_m,v_m=None, a_m=None, stiffness=None, contact_thresh_pos_N=None, contact_thresh_neg_N=None, req_calibration=True):
        """
        x_m: commanded absolute position (meters). x_m=0 is down. x_m=~1.1 is up
        v_m: velocity for trapezoidal motion profile (m/s)
        a_m: acceleration for trapezoidal motion profile (m/s^2)
        stiffness: stiffness of motion. Range 0.0 (min) to 1.0 (max)
        contact_thresh_pos_N: force threshold to stop motion (~Newtons, up direction)
        contact_thresh_neg_N: force threshold to stop motion (~Newtons, down direction)
        req_calibration: Disallow motion prior to homing
        """
        if req_calibration:
            if not self.motor.status['pos_calibrated']:
                print 'Lift not homed'
                return

        if stiffness is not None:
            stiffness = max(0, min(1.0, stiffness))
        else:
            stiffness = self.stiffness

        if v_m is not None:
            v_r=self.translate_to_motor_rad(min(abs(v_m), self.params['motion']['max']['vel_m']))
        else:
            v_r = self.vel_r

        if a_m is not None:
            a_r = self.translate_to_motor_rad(min(abs(a_m), self.params['motion']['max']['accel_m']))
        else:
            a_r = self.accel_r

        if contact_thresh_neg_N is not None:
            i_contact_neg = max(self.translate_force_to_motor_current(contact_thresh_neg_N),
                                self.params['contact_thresh_max_N'][0])
        else:
            i_contact_neg = self.i_contact_neg

        if contact_thresh_pos_N is not None:
            i_contact_pos = min(self.translate_force_to_motor_current(contact_thresh_pos_N),
                                self.params['contact_thresh_max_N'][1])
        else:
            i_contact_pos = self.i_contact_pos

        self.motor.set_command(mode = MODE_POS_TRAJ,
                                x_des=self.translate_to_motor_rad(x_m),
                                v_des=v_r,
                                a_des=a_r,
                                stiffness=stiffness,
                                i_feedforward=self.i_feedforward,
                                i_contact_pos=i_contact_pos,
                                i_contact_neg=i_contact_neg)

    def move_by(self,x_m,v_m=None, a_m=None, stiffness=None, contact_thresh_pos_N=None, contact_thresh_neg_N=None, req_calibration=True):
        """
        x_m: commanded incremental motion (meters).
        v_m: velocity for trapezoidal motion profile (m/s)
        a_m: acceleration for trapezoidal motion profile (m/s^2)
        stiffness: stiffness of motion. Range 0.0 (min) to 1.0 (max)
        contact_thresh_pos_N: force threshold to stop motion (~Newtons, up direction)
        contact_thresh_neg_N: force threshold to stop motion (~Newtons, down direction)
        req_calibration: Disallow motion prior to homing
        """
        if req_calibration:
            if not self.motor.status['pos_calibrated']:
                print 'Lift not calibrated'
                return

        if stiffness is not None:
            stiffness = max(0, min(1.0, stiffness))
        else:
            stiffness = self.stiffness

        if v_m is not None:
            v_r=self.translate_to_motor_rad(min(abs(v_m), self.params['motion']['max']['vel_m']))
        else:
            v_r = self.vel_r

        if a_m is not None:
            a_r = self.translate_to_motor_rad(min(abs(a_m), self.params['motion']['max']['accel_m']))
        else:
            a_r = self.accel_r

        if contact_thresh_neg_N is not None:
            i_contact_neg = max(self.translate_force_to_motor_current(contact_thresh_neg_N),
                                self.params['contact_thresh_max_N'][0])
        else:
            i_contact_neg = self.i_contact_neg

        if contact_thresh_pos_N is not None:
            i_contact_pos = min(self.translate_force_to_motor_current(contact_thresh_pos_N),
                                self.params['contact_thresh_max_N'][1])
        else:
            i_contact_pos = self.i_contact_pos

        #print('Lift %.2f , %.2f  , %.2f' % (x_m, self.motor_rad_to_translate(v_r), self.motor_rad_to_translate(a_r)))

        self.motor.set_command(mode = MODE_POS_TRAJ_INCR,
                                x_des=self.translate_to_motor_rad(x_m),
                                v_des=v_r,
                                a_des=a_r,
                                stiffness=stiffness,
                                i_feedforward=self.i_feedforward,
                                i_contact_pos=i_contact_pos,
                                i_contact_neg=i_contact_neg)

    # ######### Utility ##############################

    def motor_current_to_translate_force(self,i):
        #tq=self.motor.current_to_torque(i)
        #r = (self.params['pinion_t'] * self.params['belt_pitch_m'] / math.pi)/2
        if i is None:
            return
        return self.params['force_N_per_A']*(i-self.params['i_feedforward'])
        #return tq/r

    def translate_force_to_motor_current(self,f):
        if f is None:
            return
        return (f/self.params['force_N_per_A'])+self.params['i_feedforward']
        #r = (self.params['pinion_t'] * self.params['belt_pitch_m'] / math.pi) / 2
        #tq=f*r
        #return self.motor.torque_to_current(tq)

    def motor_rad_to_translate(self,ang): #input in rad
        if ang is None:
            return
        d=self.params['pinion_t']*self.params['belt_pitch_m']/math.pi
        lift_m = (rad_to_deg(ang)/180.0)*math.pi*(d/2)
        return lift_m

    def translate_to_motor_rad(self, lift_m):
        if lift_m is None:
            return
        d = self.params['pinion_t'] * self.params['belt_pitch_m'] / math.pi
        ang = 180*lift_m/((d/2)*math.pi)
        return deg_to_rad(ang)

    def __wait_for_contact(self, timeout=5.0):
        ts=time.time()
        while (time.time()-ts<timeout):
            self.pull_status()
            if self.motor.status['in_guarded_event']:
                return True
            time.sleep(0.01)
        return False


    def home(self, measuring=False):
        print 'Homing lift...'
        g0=self.motor.gains['enable_guarded_mode']
        s0=self.motor.gains['enable_sync_mode']
        self.motor.enable_guarded_mode()
        self.motor.disable_sync_mode()
        self.motor.reset_pos_calibrated()
        self.push_command()

        x_up=None
        #Up direction
        self.pull_status()
        xstart=self.status['pos']
        self.move_by(x_m=1.25, contact_thresh_pos_N=self.params['homing_force_N'][1], contact_thresh_neg_N=self.params['homing_force_N'][0], req_calibration=False)
        self.push_command()
        if self.__wait_for_contact(timeout=15.0): #self.__wait_for_contact(timeout=15.0):
            print 'Upward contact detected at motor position (rad)', self.motor.status['pos'],self.motor_rad_to_translate(self.motor.status['pos'])
            if not measuring:
                x = self.translate_to_motor_rad(self.params['range_m'][1])
                print 'Marking lift position to (m)', self.params['range_m'][1]
                self.motor.mark_position(x)
                self.motor.set_pos_calibrated()
                self.push_command()
            else:
                self.pull_status()
                x_up=self.status['pos']-xstart
        else:
            print 'Failed to detect contact'
            return
        #Allow to settle
        time.sleep(1.0)

        # Down direction
        self.move_by(x_m=-0.5, req_calibration=False)
        self.push_command()
        time.sleep(6.0)

        #Restore default
        if not g0:
            self.motor.disable_guarded_mode()
        if s0:
            self.motor.enable_sync_mode()
        self.push_command()

        return x_up