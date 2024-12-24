"""
    RPocket: a library for Retroid Pocket (5/Mini)
    Author: Kdog
    Version: 0.1
    SPDX-License-Identifier: MIT
"""

from pathlib import Path
import sys

# Default value used when calibration is reset
# DEFAULT_AXIS_MAX : this one is not critical as it only
# impacts the SDL layer (truncate the value) and it will be
# updated during the calibration procedure with an optimal
# value
DEFAULT_AXIS_MAX=0x580
# DEFAULT_TRIGGER_MAX: this one is tricky because the reported value
# from the driver for a trigger is modified with it. The simplified 
# formula is trigger = max(TRIGGER_MAX - raw_value, 0)
# If the value is too low, the range of the trigger is decimated.
# It's better to chose a too big value which will be lowered during
# the calibration procedure.
DEFAULT_TRIGGER_MAX=0x755

PARAMETERS_DIR_PATH="/sys/module/retroid/parameters"

class RPCalibrationControl:
    def __init__(self, parameters_dir, name, default_max):
        self.name=name
        self.parameters_dir = Path(parameters_dir)
        self.default_max = default_max
        self.antideadzone = 0
        self.deadzone = 0
        self.max = 0

    def load_parameters(self):
        try:
            with open(self.parameters_dir / f"{self.name}_antideadzone","r") as fparam:
                self.antideadzone = int(fparam.readline())
            with open(self.parameters_dir / f"{self.name}_deadzone","r") as fparam:
                self.deadzone = int(fparam.readline())
            with open(self.parameters_dir / f"{self.name}_max","r") as fparam:
                self.max = int(fparam.readline())

        except IOError as e:
            print(f"I/O error({e.errno}): {e.strerror}")
            exit(1)
        except: #handle other exceptions such as attribute errors
            print(f"Unexpected error:{sys.exc_info()[0]}")
            exit(1)

    def save_configuration(self, savefile):
        
        savefile.write(f"echo {self.antideadzone} > {self.parameters_dir}/{self.name}_antideadzone\n")
        savefile.write(f"echo {self.deadzone} > {self.parameters_dir}/{self.name}_deadzone\n")
        savefile.write(f"echo {self.max} > {self.parameters_dir}/{self.name}_max\n")
    
    def write_parameters(self):
        
        try:
            with open(self.parameters_dir / f"{self.name}_antideadzone","w") as fparam:
                fparam.write(f"{self.antideadzone}")

            with open(self.parameters_dir / f"{self.name}_deadzone","w") as fparam:
                fparam.write(f"{self.deadzone}")
                    
            with open(self.parameters_dir / f"{self.name}_max","w") as fparam:
                fparam.write(f"{self.max}")

        except IOError as e:
            print(f"I/O error({e.errno}): {e.strerror}")
            exit(1)
        except: #handle other exceptions such as attribute errors
            print(f"Unexpected error:{sys.exc_info()[0]}")
            exit(1)
    
    def get_range(self):
        return self.max - self.antideadzone
    
    def reset(self):
        self.antideadzone = 0
        self.deadzone = 0
        self.max = self.default_max

    def __str__(self):
        result = f"{self.name}_antideadzone={self.antideadzone}\n"
        result += f"{self.name}_deadzone={self.deadzone}\n"
        result += f"{self.name}_max={self.max}\n"

        return result

class RPCalibrationAxis(RPCalibrationControl):
    def __init__(self, parameters_dir, name="axis_leftx", default_max=DEFAULT_AXIS_MAX):
        super().__init__(parameters_dir, name, default_max)
        self.min = -default_max
        self.center = 0
        self.load_parameters()

    def load_parameters(self):
        
        super().load_parameters()
        try:
            with open(self.parameters_dir / f"{self.name}_center","r") as fparam:
                self.center = int(fparam.readline())
            with open(self.parameters_dir / f"{self.name}_min","r") as fparam:
                self.min = int(fparam.readline())

        except IOError as e:
            print(f"I/O error({e.errno}): {e.strerror}")
            exit(1)
        except: #handle other exceptions such as attribute errors
            print(f"Unexpected error:{sys.exc_info()[0]}")
            exit(1)
    
    def save_configuration(self, savefile):
        super().save_configuration(savefile)
        savefile.write(f"echo {self.center} > {self.parameters_dir}/{self.name}_center\n")
        savefile.write(f"echo {self.min} > {self.parameters_dir}/{self.name}_min\n")
    
    def write_parameters(self):
        super().write_parameters()
        try:
            with open(self.parameters_dir / f"{self.name}_center","w") as fparam:
                fparam.write(f"{self.center}")
            with open(self.parameters_dir / f"{self.name}_min","w") as fparam:
                fparam.write(f"{self.min}")

        except IOError as e:
            print(f"I/O error({e.errno}): {e.strerror}")
            exit(1)
        except: #handle other exceptions such as attribute errors
            print(f"Unexpected error:{sys.exc_info()[0]}")
            exit(1)

    def reset(self):
        super().reset()
        self.center = 0
        self.min = -self.default_max
    
    def __str__(self):
        result = super().__str__()
        result += f"{self.name}_center={self.center}\n"
        result += f"{self.name}_min={self.min}\n"

        return result

class RPCalibrationTrigger(RPCalibrationControl):
    def __init__(self, parameters_dir, name="trigger_left", default_max=DEFAULT_TRIGGER_MAX):
        super().__init__(parameters_dir, name, default_max)
        self.load_parameters()
    
class RPCalibration:
    def __init__(self, parameters_dir=PARAMETERS_DIR_PATH, default_axis_max=DEFAULT_AXIS_MAX, default_trigger_max=DEFAULT_TRIGGER_MAX):
        self.parameters_dir = Path(parameters_dir)
        self.axis_leftx = RPCalibrationAxis(parameters_dir,"axis_leftx",default_axis_max)
        self.axis_lefty = RPCalibrationAxis(parameters_dir,"axis_lefty",default_axis_max)
        self.axis_rightx = RPCalibrationAxis(parameters_dir,"axis_rightx",default_axis_max)
        self.axis_righty = RPCalibrationAxis(parameters_dir,"axis_righty",default_axis_max)
        self.trigger_left = RPCalibrationTrigger(parameters_dir,"trigger_left",default_trigger_max)
        self.trigger_right = RPCalibrationTrigger(parameters_dir,"trigger_right",default_trigger_max)

        self.load_parameters()

    def load_parameters(self):
        try:
            with open(self.parameters_dir / "update_params","r") as fparam:
                self.update_params = int(fparam.readline())

        except IOError as e:
            print(f"I/O error({e.errno}): {e.strerror}")
            exit(1)
        except: #handle other exceptions such as attribute errors
            print(f"Unexpected error:{sys.exc_info()[0]}")
            exit(1)

    def save_configuration(self, savepath):
        with open(savepath,"w") as savefile:
            savefile.write("#!/usr/bin/env bash\n")
            savefile.write("#\n")
            savefile.write("# Retroid Pocket 5/Mini gamepad calibration\n")
            savefile.write("# Made with the Kdog GPcal tool\n")
            savefile.write("# SPDX-License-Identifier: MIT\n")
            savefile.write("#\n")
            self.axis_leftx.save_configuration(savefile)
            self.axis_lefty.save_configuration(savefile)
            self.axis_rightx.save_configuration(savefile)
            self.axis_righty.save_configuration(savefile)
            self.trigger_left.save_configuration(savefile)
            self.trigger_right.save_configuration(savefile)
            savefile.write(f"echo 1 > {self.syspath}/update_params\n")

    def write_parameters(self):
        self.axis_leftx.write_parameters()
        self.axis_lefty.write_parameters()
        self.axis_rightx.write_parameters()
        self.axis_righty.write_parameters()
        self.trigger_left.write_parameters()
        self.trigger_right.write_parameters()
        self.update_params=1
        try:
            with open(self.parameters_dir / "update_params","w") as fparam:
                fparam.write(f"{self.update_params}")
        except IOError as e:
            print(f"I/O error({e.errno}): {e.strerror}")
            exit(1)
        except: #handle other exceptions such as attribute errors
            print(f"Unexpected error:{sys.exc_info()[0]}")
            exit(1)

        self.update_params=0


    def reset_axis_left(self):
        self.axis_leftx.reset()
        self.axis_lefty.reset()
        self.write_parameters()
    
    def reset_axis_right(self):
        self.axis_rightx.reset()
        self.axis_righty.reset()
        self.write_parameters()

    def reset_trigger_left(self):
        self.trigger_left.reset()
        self.write_parameters()

    def reset_trigger_right(self):
        self.trigger_right.reset()
        self.write_parameters()
      
    def reset_all(self):
        self.axis_leftx.reset()
        self.axis_lefty.reset()
        self.axis_rightx.reset()
        self.axis_righty.reset()
        self.trigger_left.reset()
        self.trigger_right.reset()
        self.write_parameters()
    
    def __str__(self):
        return self.axis_leftx \
            + self.axis_lefty \
            + self.axis_rightx \
            + self.axis_righty \
            + self.trigger_left \
            + self.trigger_right \
            +f"self.update_params={self.update_params}\n"
