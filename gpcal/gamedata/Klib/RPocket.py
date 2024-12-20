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


class RPCalibration:
    def __init__(self, path="/sys/module/retroid/parameters", default_axis_max=DEFAULT_AXIS_MAX, default_trigger_max=DEFAULT_TRIGGER_MAX):
        self.syspath = Path(path)
        self.load_parameters()
        self.default_axis_max = default_axis_max
        self.default_trigger_max = default_trigger_max

    def load_parameters(self):
        try:
            with open(self.syspath / "axis_leftx_antideadzone","r") as fparam:
                self.axis_leftx_antideadzone = int(fparam.readline())
            with open(self.syspath / "axis_leftx_center","r") as fparam:
                self.axis_leftx_center = int(fparam.readline())
            with open(self.syspath / "axis_leftx_deadzone","r") as fparam:
                self.axis_leftx_deadzone = int(fparam.readline())
            with open(self.syspath / "axis_leftx_max","r") as fparam:
                self.axis_leftx_max = int(fparam.readline())
            with open(self.syspath / "axis_leftx_min","r") as fparam:
                self.axis_leftx_min = int(fparam.readline())
            with open(self.syspath / "axis_lefty_antideadzone","r") as fparam:
                self.axis_lefty_antideadzone = int(fparam.readline())
            with open(self.syspath / "axis_lefty_center","r") as fparam:
                self.axis_lefty_center = int(fparam.readline())
            with open(self.syspath / "axis_lefty_deadzone","r") as fparam:
                self.axis_lefty_deadzone = int(fparam.readline())
            with open(self.syspath / "axis_lefty_max","r") as fparam:
                self.axis_lefty_max = int(fparam.readline())
            with open(self.syspath / "axis_lefty_min","r") as fparam:
                self.axis_lefty_min = int(fparam.readline())
            with open(self.syspath / "axis_leftz_antideadzone","r") as fparam:
                self.axis_leftz_antideadzone = int(fparam.readline())
            with open(self.syspath / "axis_leftz_center","r") as fparam:
                self.axis_leftz_center = int(fparam.readline())
            with open(self.syspath / "axis_leftz_deadzone","r") as fparam:
                self.axis_leftz_deadzone = int(fparam.readline())
            with open(self.syspath / "axis_leftz_max","r") as fparam:
                self.axis_leftz_max = int(fparam.readline())
            with open(self.syspath / "axis_leftz_min","r") as fparam:
                self.axis_leftz_min = int(fparam.readline())
            with open(self.syspath / "axis_rightx_antideadzone","r") as fparam:
                self.axis_rightx_antideadzone = int(fparam.readline())
            with open(self.syspath / "axis_rightx_center","r") as fparam:
                self.axis_rightx_center = int(fparam.readline())
            with open(self.syspath / "axis_rightx_deadzone","r") as fparam:
                self.axis_rightx_deadzone = int(fparam.readline())
            with open(self.syspath / "axis_rightx_max","r") as fparam:
                self.axis_rightx_max = int(fparam.readline())
            with open(self.syspath / "axis_rightx_min","r") as fparam:
                self.axis_rightx_min = int(fparam.readline())
            with open(self.syspath / "axis_righty_antideadzone","r") as fparam:
                self.axis_righty_antideadzone = int(fparam.readline())
            with open(self.syspath / "axis_righty_center","r") as fparam:
                self.axis_righty_center = int(fparam.readline())
            with open(self.syspath / "axis_righty_deadzone","r") as fparam:
                self.axis_righty_deadzone = int(fparam.readline())
            with open(self.syspath / "axis_righty_max","r") as fparam:
                self.axis_righty_max = int(fparam.readline())
            with open(self.syspath / "axis_righty_min","r") as fparam:
                self.axis_righty_min = int(fparam.readline())
            with open(self.syspath / "axis_rightz_antideadzone","r") as fparam:
                self.axis_rightz_antideadzone = int(fparam.readline())
            with open(self.syspath / "axis_rightz_center","r") as fparam:
                self.axis_rightz_center = int(fparam.readline())
            with open(self.syspath / "axis_rightz_deadzone","r") as fparam:
                self.axis_rightz_deadzone = int(fparam.readline())
            with open(self.syspath / "axis_rightz_max","r") as fparam:
                self.axis_rightz_max = int(fparam.readline())
            with open(self.syspath / "axis_rightz_min","r") as fparam:
                self.axis_rightz_min = int(fparam.readline())
            with open(self.syspath / "trigger_left_antideadzone","r") as fparam:
                self.trigger_left_antideadzone = int(fparam.readline())
            with open(self.syspath / "trigger_left_deadzone","r") as fparam:
                self.trigger_left_deadzone = int(fparam.readline())
            with open(self.syspath / "trigger_left_max","r") as fparam:
                self.trigger_left_max = int(fparam.readline())
            with open(self.syspath / "trigger_right_antideadzone","r") as fparam:
                self.trigger_right_antideadzone = int(fparam.readline())
            with open(self.syspath / "trigger_right_deadzone","r") as fparam:
                self.trigger_right_deadzone = int(fparam.readline())
            with open(self.syspath / "trigger_right_max","r") as fparam:
                self.trigger_right_max = int(fparam.readline())
            with open(self.syspath / "update_params","r") as fparam:
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
            savefile.write(f"echo {self.axis_leftx_antideadzone} > {self.syspath}/axis_leftx_antideadzone\n")
            savefile.write(f"echo {self.axis_leftx_center} > {self.syspath}/axis_leftx_center\n")
            savefile.write(f"echo {self.axis_leftx_deadzone} > {self.syspath}/axis_leftx_deadzone\n")
            savefile.write(f"echo {self.axis_leftx_max} > {self.syspath}/axis_leftx_max\n")
            savefile.write(f"echo {self.axis_leftx_min} > {self.syspath}/axis_leftx_min\n")
            savefile.write(f"echo {self.axis_lefty_antideadzone} > {self.syspath}/axis_lefty_antideadzone\n")
            savefile.write(f"echo {self.axis_lefty_center} > {self.syspath}/axis_lefty_center\n")
            savefile.write(f"echo {self.axis_lefty_deadzone} > {self.syspath}/axis_lefty_deadzone\n")
            savefile.write(f"echo {self.axis_lefty_max} > {self.syspath}/axis_lefty_max\n")
            savefile.write(f"echo {self.axis_lefty_min} > {self.syspath}/axis_lefty_min\n")
            savefile.write(f"echo {self.axis_leftz_antideadzone} > {self.syspath}/axis_leftz_antideadzone\n")
            savefile.write(f"echo {self.axis_leftz_center} > {self.syspath}/axis_leftz_center\n")
            savefile.write(f"echo {self.axis_leftz_deadzone} > {self.syspath}/axis_leftz_deadzone\n")
            savefile.write(f"echo {self.axis_leftz_max} > {self.syspath}/axis_leftz_max\n")
            savefile.write(f"echo {self.axis_leftz_min} > {self.syspath}/axis_leftz_min\n")
            savefile.write(f"echo {self.axis_rightx_antideadzone} > {self.syspath}/axis_rightx_antideadzone\n")
            savefile.write(f"echo {self.axis_rightx_center} > {self.syspath}/axis_rightx_center\n")
            savefile.write(f"echo {self.axis_rightx_deadzone} > {self.syspath}/axis_rightx_deadzone\n")
            savefile.write(f"echo {self.axis_rightx_max} > {self.syspath}/axis_rightx_max\n")
            savefile.write(f"echo {self.axis_rightx_min} > {self.syspath}/axis_rightx_min\n")
            savefile.write(f"echo {self.axis_righty_antideadzone} > {self.syspath}/axis_righty_antideadzone\n")
            savefile.write(f"echo {self.axis_righty_center} > {self.syspath}/axis_righty_center\n")
            savefile.write(f"echo {self.axis_righty_deadzone} > {self.syspath}/axis_righty_deadzone\n")
            savefile.write(f"echo {self.axis_righty_max} > {self.syspath}/axis_righty_max\n")
            savefile.write(f"echo {self.axis_righty_min} > {self.syspath}/axis_righty_min\n")
            savefile.write(f"echo {self.axis_rightz_antideadzone} > {self.syspath}/axis_rightz_antideadzone\n")
            savefile.write(f"echo {self.axis_rightz_center} > {self.syspath}/axis_rightz_center\n")
            savefile.write(f"echo {self.axis_rightz_deadzone} > {self.syspath}/axis_rightz_deadzone\n")
            savefile.write(f"echo {self.axis_rightz_max} > {self.syspath}/axis_rightz_max\n")
            savefile.write(f"echo {self.axis_rightz_min} > {self.syspath}/axis_rightz_min\n")
            savefile.write(f"echo {self.trigger_left_antideadzone} > {self.syspath}/trigger_left_antideadzone\n")
            savefile.write(f"echo {self.trigger_left_deadzone} > {self.syspath}/trigger_left_deadzone\n")
            savefile.write(f"echo {self.trigger_left_max} > {self.syspath}/trigger_left_max\n")
            savefile.write(f"echo {self.trigger_right_antideadzone} > {self.syspath}/trigger_right_antideadzone\n")
            savefile.write(f"echo {self.trigger_right_deadzone} > {self.syspath}/trigger_right_deadzone\n")
            savefile.write(f"echo {self.trigger_right_max} > {self.syspath}/trigger_right_max\n")
            savefile.write(f"echo 1 > {self.syspath}/update_params\n")

    def apply_parameters(self):
        self.update_params=1
        try:
            with open(self.syspath / "axis_leftx_antideadzone","w") as fparam:
                fparam.write(f"{self.axis_leftx_antideadzone}")
            with open(self.syspath / "axis_leftx_center","w") as fparam:
                fparam.write(f"{self.axis_leftx_center}")
            with open(self.syspath / "axis_leftx_deadzone","w") as fparam:
                fparam.write(f"{self.axis_leftx_deadzone}")
            with open(self.syspath / "axis_leftx_max","w") as fparam:
                fparam.write(f"{self.axis_leftx_max}")
            with open(self.syspath / "axis_leftx_min","w") as fparam:
                fparam.write(f"{self.axis_leftx_min}")
            with open(self.syspath / "axis_lefty_antideadzone","w") as fparam:
                fparam.write(f"{self.axis_lefty_antideadzone}")
            with open(self.syspath / "axis_lefty_center","w") as fparam:
                fparam.write(f"{self.axis_lefty_center}")
            with open(self.syspath / "axis_lefty_deadzone","w") as fparam:
                fparam.write(f"{self.axis_lefty_deadzone}")
            with open(self.syspath / "axis_lefty_max","w") as fparam:
                fparam.write(f"{self.axis_lefty_max}")
            with open(self.syspath / "axis_lefty_min","w") as fparam:
                fparam.write(f"{self.axis_lefty_min}")
            with open(self.syspath / "axis_leftz_antideadzone","w") as fparam:
                fparam.write(f"{self.axis_leftz_antideadzone}")
            with open(self.syspath / "axis_leftz_center","w") as fparam:
                fparam.write(f"{self.axis_leftz_center}")
            with open(self.syspath / "axis_leftz_deadzone","w") as fparam:
                fparam.write(f"{self.axis_leftz_deadzone}")
            with open(self.syspath / "axis_leftz_max","w") as fparam:
                fparam.write(f"{self.axis_leftz_max}")
            with open(self.syspath / "axis_leftz_min","w") as fparam:
                fparam.write(f"{self.axis_leftz_min}")
            with open(self.syspath / "axis_rightx_antideadzone","w") as fparam:
                fparam.write(f"{self.axis_rightx_antideadzone}")
            with open(self.syspath / "axis_rightx_center","w") as fparam:
                fparam.write(f"{self.axis_rightx_center}")
            with open(self.syspath / "axis_rightx_deadzone","w") as fparam:
                fparam.write(f"{self.axis_rightx_deadzone}")
            with open(self.syspath / "axis_rightx_max","w") as fparam:
                fparam.write(f"{self.axis_rightx_max}")
            with open(self.syspath / "axis_rightx_min","w") as fparam:
                fparam.write(f"{self.axis_rightx_min}")
            with open(self.syspath / "axis_righty_antideadzone","w") as fparam:
                fparam.write(f"{self.axis_righty_antideadzone}")
            with open(self.syspath / "axis_righty_center","w") as fparam:
                fparam.write(f"{self.axis_righty_center}")
            with open(self.syspath / "axis_righty_deadzone","w") as fparam:
                fparam.write(f"{self.axis_righty_deadzone}")
            with open(self.syspath / "axis_righty_max","w") as fparam:
                fparam.write(f"{self.axis_righty_max}")
            with open(self.syspath / "axis_righty_min","w") as fparam:
                fparam.write(f"{self.axis_righty_min}")
            with open(self.syspath / "axis_rightz_antideadzone","w") as fparam:
                fparam.write(f"{self.axis_rightz_antideadzone}")
            with open(self.syspath / "axis_rightz_center","w") as fparam:
                fparam.write(f"{self.axis_rightz_center}")
            with open(self.syspath / "axis_rightz_deadzone","w") as fparam:
                fparam.write(f"{self.axis_rightz_deadzone}")
            with open(self.syspath / "axis_rightz_max","w") as fparam:
                fparam.write(f"{self.axis_rightz_max}")
            with open(self.syspath / "axis_rightz_min","w") as fparam:
                fparam.write(f"{self.axis_rightz_min}")
            with open(self.syspath / "trigger_left_antideadzone","w") as fparam:
                fparam.write(f"{self.trigger_left_antideadzone}")
            with open(self.syspath / "trigger_left_deadzone","w") as fparam:
                fparam.write(f"{self.trigger_left_deadzone}")
            with open(self.syspath / "trigger_left_max","w") as fparam:
                fparam.write(f"{self.trigger_left_max}")
            with open(self.syspath / "trigger_right_antideadzone","w") as fparam:
                fparam.write(f"{self.trigger_right_antideadzone}")
            with open(self.syspath / "trigger_right_deadzone","w") as fparam:
                fparam.write(f"{self.trigger_right_deadzone}")
            with open(self.syspath / "trigger_right_max","w") as fparam:
                fparam.write(f"{self.trigger_right_max}")
            with open(self.syspath / "update_params","w") as fparam:
                fparam.write(f"{self.update_params}")
        except IOError as e:
            print(f"I/O error({e.errno}): {e.strerror}")
            exit(1)
        except: #handle other exceptions such as attribute errors
            print(f"Unexpected error:{sys.exc_info()[0]}")
            exit(1)

    def reset_axis_left(self):
        self.axis_leftx_antideadzone=0
        self.axis_leftx_center=0
        self.axis_leftx_deadzone=0
        self.axis_leftx_max=self.default_axis_max
        self.axis_leftx_min=-self.default_axis_max
        self.axis_lefty_antideadzone=0
        self.axis_lefty_center=0
        self.axis_lefty_deadzone=0
        self.axis_lefty_max=self.default_axis_max
        self.axis_lefty_min=-self.default_axis_max
        self.axis_leftz_antideadzone=0
        self.axis_leftz_center=0
        self.axis_leftz_deadzone=0
        self.axis_leftz_max=self.default_axis_max
        self.axis_leftz_min=-self.default_axis_max
        self.apply_parameters()

    def reset_axis_right(self):
        self.axis_rightx_antideadzone=0
        self.axis_rightx_center=0
        self.axis_rightx_deadzone=0
        self.axis_rightx_max=self.default_axis_max
        self.axis_rightx_min=-self.default_axis_max
        self.axis_righty_antideadzone=0
        self.axis_righty_center=0
        self.axis_righty_deadzone=0
        self.axis_righty_max=self.default_axis_max
        self.axis_righty_min=-self.default_axis_max
        self.axis_rightz_antideadzone=0
        self.axis_rightz_center=0
        self.axis_rightz_deadzone=0
        self.axis_rightz_max=self.default_axis_max
        self.axis_rightz_min=-self.default_axis_max
        self.apply_parameters()

    def reset_trigger_left(self):
        self.trigger_left_antideadzone=0
        self.trigger_left_deadzone=0
        self.trigger_left_max=self.default_trigger_max
        self.apply_parameters()

    def reset_trigger_right(self):
        self.trigger_right_antideadzone=0
        self.trigger_right_deadzone=0
        self.trigger_right_max=self.default_trigger_max
        self.apply_parameters()

    def reset_all(self):
        self.reset_axis_left()
        self.reset_axis_right()
        self.reset_trigger_left()
        self.reset_trigger_right()
    
    def __str__(self):
        return f"self.axis_leftx_antideadzone={self.axis_leftx_antideadzone}\n" \
                +f"self.axis_leftx_center={self.axis_leftx_center}\n" \
                +f"self.axis_leftx_deadzone={self.axis_leftx_deadzone}\n" \
                +f"self.axis_leftx_max={self.axis_leftx_max}\n" \
                +f"self.axis_leftx_min={self.axis_leftx_min}\n" \
                +f"self.axis_lefty_antideadzone={self.axis_lefty_antideadzone}\n" \
                +f"self.axis_lefty_center={self.axis_lefty_center}\n" \
                +f"self.axis_lefty_deadzone={self.axis_lefty_deadzone}\n" \
                +f"self.axis_lefty_max={self.axis_lefty_max}\n" \
                +f"self.axis_lefty_min={self.axis_lefty_min}\n" \
                +f"self.axis_leftz_antideadzone={self.axis_leftz_antideadzone}\n" \
                +f"self.axis_leftz_center={self.axis_leftz_center}\n" \
                +f"self.axis_leftz_deadzone={self.axis_leftz_deadzone}\n" \
                +f"self.axis_leftz_max={self.axis_leftz_max}\n" \
                +f"self.axis_leftz_min={self.axis_leftz_min}\n" \
                +f"self.axis_rightx_antideadzone={self.axis_rightx_antideadzone}\n" \
                +f"self.axis_rightx_center={self.axis_rightx_center}\n" \
                +f"self.axis_rightx_deadzone={self.axis_rightx_deadzone}\n" \
                +f"self.axis_rightx_max={self.axis_rightx_max}\n" \
                +f"self.axis_rightx_min={self.axis_rightx_min}\n" \
                +f"self.axis_righty_antideadzone={self.axis_righty_antideadzone}\n" \
                +f"self.axis_righty_center={self.axis_righty_center}\n" \
                +f"self.axis_righty_deadzone={self.axis_righty_deadzone}\n" \
                +f"self.axis_righty_max={self.axis_righty_max}\n" \
                +f"self.axis_righty_min={self.axis_righty_min}\n" \
                +f"self.axis_rightz_antideadzone={self.axis_rightz_antideadzone}\n" \
                +f"self.axis_rightz_center={self.axis_rightz_center}\n" \
                +f"self.axis_rightz_deadzone={self.axis_rightz_deadzone}\n" \
                +f"self.axis_rightz_max={self.axis_rightz_max}\n" \
                +f"self.axis_rightz_min={self.axis_rightz_min}\n" \
                +f"self.trigger_left_antideadzone={self.trigger_left_antideadzone}\n" \
                +f"self.trigger_left_deadzone={self.trigger_left_deadzone}\n" \
                +f"self.trigger_left_max={self.trigger_left_max}\n" \
                +f"self.trigger_right_antideadzone={self.trigger_right_antideadzone}\n" \
                +f"self.trigger_right_deadzone={self.trigger_right_deadzone}\n" \
                +f"self.trigger_right_max={self.trigger_right_max}\n" \
                +f"self.update_params={self.update_params}\n"
