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
        self.antideadzone = {}
        self.deadzone = {}
        self.max = {}

    def load_parameters(self,axis="default"):
        if axis == "default":
            suffix = ""
        else:
            suffix = axis

        try:
            print(axis)
            with open(self.parameters_dir / f"{self.name}{suffix}_antideadzone","r") as fparam:
                self.antideadzone[axis] = int(fparam.readline())
            print(axis)
            with open(self.parameters_dir / f"{self.name}{suffix}_deadzone","r") as fparam:
                self.deadzone[axis] = int(fparam.readline())
            print(axis) 
            with open(self.parameters_dir / f"{self.name}{suffix}_max","r") as fparam:
                self.max[axis] = int(fparam.readline())

        except IOError as e:
            print(f"I/O error({e.errno}): {e.strerror}")
            exit(1)
        except: #handle other exceptions such as attribute errors
            print(f"Unexpected error:{sys.exc_info()[0]}")
            exit(1)

    def save_parameters(self, savefile, axis="default"):
        if axis == "default":
            suffix = ""
        else:
            suffix = axis
        
        savefile.write(f"echo {self.antideadzone[axis]} > {self.parameters_dir}/{self.name}{suffix}_antideadzone\n")
        savefile.write(f"echo {self.deadzone[axis]} > {self.parameters_dir}/{self.name}{suffix}_deadzone\n")
        savefile.write(f"echo {self.max[axis]} > {self.parameters_dir}/{self.name}{suffix}_max\n")
    
    def apply_parameters(self,axis="default"):
        if axis == "default":
            suffix = ""
        else:
            suffix = axis
        
        try:
            with open(self.parameters_dir / f"{self.name}{suffix}_antideadzone","w") as fparam:
                fparam.write(f"{self.antideadzone[axis]}")

            with open(self.parameters_dir / f"{self.name}{suffix}_deadzone","w") as fparam:
                fparam.write(f"{self.deadzone[axis]}")
                    
            with open(self.parameters_dir / f"{self.name}{suffix}_max","w") as fparam:
                fparam.write(f"{self.max[axis]}")

        except IOError as e:
            print(f"I/O error({e.errno}): {e.strerror}")
            exit(1)
        except: #handle other exceptions such as attribute errors
            print(f"Unexpected error:{sys.exc_info()[0]}")
            exit(1)
    
    def reset(self,axis="default"):
        self.antideadzone[axis] = 0
        self.deadzone[axis] = 0
        self.max[axis] = self.default_max

    def __str__(self,axis="default"):
        if axis == "default":
            suffix = ""
        else:
            suffix = axis
        
        result = f"{self.name}{suffix}_antideadzone={self.antideadzone[axis]}\n"
        result += f"{self.name}{suffix}_deadzone={self.deadzone[axis]}\n"
        result += f"{self.name}{suffix}_max={self.max[axis]}\n"

        return result

class RPCalibrationStick(RPCalibrationControl):
    def __init__(self, parameters_dir, name="axis_left", default_max=DEFAULT_AXIS_MAX, axis_list=["x","y","z"],):
        super().__init__(parameters_dir, name, default_max)
        self.axis_list=axis_list
        self.min = {}
        self.center = {}
        self.load_parameters()

    def load_parameters(self):
        
        for axis in self.axis_list:
            super().load_parameters(axis)
            try:
                with open(self.parameters_dir / f"{self.name}{axis}_center","r") as fparam:
                    self.center[axis] = int(fparam.readline())
                with open(self.parameters_dir / f"{self.name}{axis}_min","r") as fparam:
                    self.min[axis] = int(fparam.readline())

            except IOError as e:
                print(f"I/O error({e.errno}): {e.strerror}")
                exit(1)
            except: #handle other exceptions such as attribute errors
                print(f"Unexpected error:{sys.exc_info()[0]}")
                exit(1)
    
    def save_parameters(self, savefile):
        for axis in self.axis_list:
            super().save_parameters(savefile,axis)
            savefile.write(f"echo {self.center[axis]} > {self.parameters_dir}/{self.name}{axis}_center\n")
            savefile.write(f"echo {self.min[axis]} > {self.parameters_dir}/{self.name}{axis}_min\n")
    
    def apply_parameters(self):
        for axis in self.axis_list:
            super().apply_parameters(axis)
            try:
                with open(self.parameters_dir / f"{self.name}{axis}_center","w") as fparam:
                    fparam.write(f"{self.center[axis]}")
                with open(self.parameters_dir / f"{self.name}{axis}_min","w") as fparam:
                    fparam.write(f"{self.min[axis]}")

            except IOError as e:
                print(f"I/O error({e.errno}): {e.strerror}")
                exit(1)
            except: #handle other exceptions such as attribute errors
                print(f"Unexpected error:{sys.exc_info()[0]}")
                exit(1)

    def reset(self):
        for axis in self.axis_list:
            super().reset(axis)
            self.center[axis] = 0
            self.min[axis] = 0

    def get_range(self,axis):
        return self.max[axis] - self.antideadzone[axis]
    
    def __str__(self):
        result = ""
        for axis in self.axis_list:
            result += super().__str__()
            result += f"{self.name}{axis}_center={self.center[axis]}\n"
            result += f"{self.name}{axis}_min={self.min[axis]}\n"

        return result

class RPCalibrationTrigger(RPCalibrationControl):
    def __init__(self, parameters_dir, name="trigger_left", default_max=DEFAULT_TRIGGER_MAX):
        super().__init__(parameters_dir, name, default_max)
        self.load_parameters()

    def load_parameters(self):
        super().load_parameters()

    def save_parameters(self, savefile):
        super().save_parameters(savefile)

    def apply_parameters(self):
        super().apply_parameters()

    def reset(self):
        super().reset()
    
    def get_range(self):
        return self.max["default"] - self.antideadzone["default"]

    def __str__(self):
        return super().__str__()
    
class RPCalibration:
    def __init__(self, parameters_dir=PARAMETERS_DIR_PATH, default_axis_max=DEFAULT_AXIS_MAX, default_trigger_max=DEFAULT_TRIGGER_MAX):
        self.parameters_dir = Path(parameters_dir)
        self.axis_left = RPCalibrationStick(parameters_dir,"axis_left",default_axis_max)
        self.axis_right = RPCalibrationStick(parameters_dir,"axis_right",default_axis_max)
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

    def save_parameters(self, savepath):
        with open(savepath,"w") as savefile:
            savefile.write("#!/usr/bin/env bash\n")
            savefile.write("#\n")
            savefile.write("# Retroid Pocket 5/Mini gamepad calibration\n")
            savefile.write("# Made with the Kdog GPcal tool\n")
            savefile.write("# SPDX-License-Identifier: MIT\n")
            savefile.write("#\n")
            self.axis_left.save_parameters(savefile)
            self.axis_right.save_parameters(savefile)
            self.trigger_left.save_parameters(savefile)
            self.trigger_right.save_parameters(savefile)
            savefile.write(f"echo 1 > {self.syspath}/update_params\n")

    def apply_parameters(self):
        self.axis_left.apply_parameters()
        self.axis_right.apply_parameters()
        self.trigger_left.apply_parameters()
        self.trigger_right.apply_parameters()
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

    def reset_axis_left(self):
        self.axis_left.reset()
        self.apply_parameters()
    
    def reset_axis_right(self):
        self.axis_right.reset()
        self.apply_parameters()

    def reset_trigger_left(self):
        self.trigger_left.reset()
        self.apply_parameters()

    def reset_trigger_right(self):
        self.trigger_right.reset()
        self.apply_parameters()
      
    def reset_all(self):
        self.axis_left.reset()
        self.axis_right.reset()
        self.trigger_left.reset()
        self.trigger_right.reset()
        self.apply_parameters()
    
    def __str__(self):
        return self.axis_left \
            + self.axis_right \
            + self.trigger_left \
            + self.trigger_right \
            +f"self.update_params={self.update_params}\n"
