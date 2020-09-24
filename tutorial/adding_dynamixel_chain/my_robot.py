from serial import SerialException
from stretch_body.robot import Robot
from stretch_body.hello_utils import *
import my_dxl

class MyRobot(Robot):
    def __init__(self):
        Robot.__init__(self)
        self.my_dxl=None
        self.status = {'my_dxl': {}}
        if self.params['use_my_dxl']:
                self.my_dxl = my_dxl.MyDxl()
                self.status['my_dxl'] = self.my_dxl.status
        self.devices['my_dxl']=self.my_dxl

    def _pull_status_dynamixel(self):
        Robot._pull_status_dynamixel(self)
        try:
            if self.my_dxl is not None:
                self.my_dxl.pull_status()
        except SerialException:
            print 'Serial Exception on Robot _pull_status_dynamixel'

    def home(self):
        if self.my_dxl is not None:
            print '--------- Homing MyDXL ----'
            self.my_dxl.home()
        Robot.home(self)

    def stow(self):
        if self.my_dxl is not None:
            self.my_dxl.stow()
        Robot.stow(self)

    def is_calibrated(self):
        ready = True
        if self.my_dxl is not None:
            for j in self.my_dxl.joints:
                req = self.my_dxl.motors[j].params['req_calibration'] and not self.my_dxl.motors[j].is_calibrated
                ready = ready and not req
        return ready and Robot.home(self)