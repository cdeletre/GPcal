#!/usr/bin/env python3

"""
    GPcal: a gamepad calibration tool for RP 5/Mini
    Author: Kdog
    Version: 0.1
    SPDX-License-Identifier: MIT
"""

import pyxel
import datetime
from pathlib import Path
from Klib.PyxUI import *

CALIBRATE_DETECTION_PERCENT=10  
AXIS_MAX_PERCENT=95             # correction after calc (error margin)
AXIS_DEADZONE_PERCENT=150       # correction after calc (error margin), stick rest zone is wide...
AXIS_DEADZONE_PERCENT_MINI=5
AXIS_ANTIDEADZONE_PERCENT=80    # 0 to 100 (> 50 to avoid big first step)
TRIGGER_MAX_PERCENT=100         # correction after calc (error margin)
TRIGGER_DEADZONE_PERCENT=105    # correction after calc (error margin)
TRIGGER_ANTIDEADZONE_PERCENT=80 # 0 to 100 (> 50 to avoid big first step)
FPS=60
CALIBRATION_DETECTION_FPS = FPS//2    # 0.5s : minimum time to maintain a stick / trigger in a position

TITLE="Kdog GPcal for RP 5/Mini"

class GPCalibrate:
    def __init__(self):
        pyxel.init(320, 240, title=TITLE,fps=FPS, quit_key=pyxel.KEY_ESCAPE, display_scale=1)

        self.ui = []
        self.sdlview = False
        self.exit_frame = 0

        # calibration process stuff
        self.calibrate = False
        self.calibrate_triggerleft = False
        self.calibrate_stickleft = False
        self.calibrate_stickright = False
        self.calibrate_triggerright = False
        self.calibrate_step = 0
        self.calibrate_last_value = None
        self.calibrate_last_value_frame = 0
        self.calibrate_data = [0,0,0,0]  # -max , -min, +min, +max

        # Create UI main panel
        ui_panel = UIPanel(title=TITLE,selected=1,btitle="made with <3 with Pyxel")

        # Create the gamepad object
        self.ui_gamepad = UIGamepad(20,140)
        self.ui_gamepad.select_none()
        self.ui_gamepad.gauge_triggerleft.callback=self.start_calibrate_triggerleft
        self.ui_gamepad.stickleft.callback=self.start_calibrate_stickleft
        self.ui_gamepad.stickright.callback=self.start_calibrate_stickright
        self.ui_gamepad.gauge_triggerright.callback=self.start_calibrate_triggerright

        ui_panel.add_uiobject(self.ui_gamepad)

        # Create the buttons
        self.button_calibrate = UIButton(20,20,60,16,"Calibrate",callback=self.start_calibration)
        ui_panel.add_uiobject(self.button_calibrate, True)

        self.button_sdlview = UIButton(90,20,60,16,"SDL view", callback=self.toggle_sdl_view)
        ui_panel.add_uiobject(self.button_sdlview)

        self.button_reset = UIButton(160,20,40,16,"Reset", callback=self.reset_calibration)
        ui_panel.add_uiobject(self.button_reset)

        self.button_save = UIButton(210,20,40,16,"Save",callback=self.save_calibration)
        ui_panel.add_uiobject(self.button_save)

        self.button_quit = UIButton(260,20,40,16,"Quit",callback=self.exit)
        ui_panel.add_uiobject(self.button_quit)

        # Create the textbox
        self.ui_textbox_info = UITextbox(20,40,280,30,1,text="Ahoy ! Welcome to Kdog Retroid Pocket Gamepad calibation tool",minshowframe=FPS)
        ui_panel.add_uiobject(self.ui_textbox_info)

        self.ui_textbox_data = UITextbox(20,65,280,70,1,text="")
        ui_panel.add_uiobject(self.ui_textbox_data)

        self.ui.append(ui_panel)

        pyxel.playm(0, loop=True)
        pyxel.run(self.update, self.draw)

    def exit(self):
        self.ui_textbox_info.minshowframe=0
        self.ui_textbox_info.settext("Sail safe !")
        self.exit_frame = pyxel.frame_count

    def update(self):

        if pyxel.frame_count - self.exit_frame > 30 and self.exit_frame > 0:
            exit()

        if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
            if self.calibrate_triggerleft:
                self.ui_textbox_info.settext("Calibration canceled")
                self.stop_calibrate_triggerleft()
                self.ui_gamepad.restore_calibration()
            elif self.calibrate_stickleft:
                self.ui_textbox_info.settext("Calibration canceled")
                self.stop_calibrate_stickleft()
                self.ui_gamepad.restore_calibration()
            elif self.calibrate_stickright:
                self.ui_textbox_info.settext("Calibration canceled")
                self.stop_calibrate_stickright()
                self.ui_gamepad.restore_calibration()
            elif self.calibrate_triggerright:
                self.ui_textbox_info.settext("Calibration canceled")
                self.stop_calibrate_triggerright()
                self.ui_gamepad.restore_calibration()
            elif self.calibrate:
                self.stop_calibration()
                self.ui_textbox_info.settext("Where to sail now captain ?")

        if self.calibrate_triggerleft:
            self.run_calibrate_triggerleft()
        elif self.calibrate_triggerright:
            self.run_calibrate_triggerright()
        elif self.calibrate_stickleft:
            self.run_calibrate_stickleft()
        elif self.calibrate_stickright:
            self.run_calibrate_stickright()

        for _,ui_object in enumerate(self.ui):
            ui_object.update()

        self.ui_textbox_data.settext(self.ui_gamepad.__str__())

    def draw(self):
        pyxel.cls(0)

        for _,ui_object in enumerate(self.ui):
            ui_object.draw()        

    def save_calibration(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d-%Hh%M")
        savepath = Path.home() / f"GPcal-{now}.sh"
        self.ui_gamepad.calibration.save_parameters(savepath)
        self.ui_textbox_info.settext(f"Calibration data saved to")
        self.ui_textbox_info.settext(f"{savepath}")

    def reset_calibration(self):
        self.ui_gamepad.calibration.reset_all()
        self.ui_textbox_info.settext("Calibration data reset to default")

    def toggle_sdl_view(self):
        self.ui_gamepad.toggle_sdl_view()
        self.sdlview = not self.sdlview
        if self.sdlview:
            self.button_sdlview.settext("RAW view")
        else:
            self.button_sdlview.settext("SDL view")

    def start_calibration(self):
        self.calibrate = True
        for _,ui_object in enumerate(self.ui):
            ui_object.select_none()
        self.ui_gamepad.select_first()
        self.ui_textbox_info.settext("Which control do you want to calibrate ?")
    
    def stop_calibration(self):
        self.calibrate = False
        self.ui_gamepad.select_none()
        for _,ui_object in enumerate(self.ui):
            ui_object.select_first()
            break
        self.ui_textbox_info.settext("Where to sail now captain ?")
    
    def start_calibrate_init(self):
        self.ui_gamepad.backup_calibration()
        self.calibrate_last_value = None
        self.calibrate_last_value_frame = 0
        self.calibrate_data = [0,0,0,0]
        self.ui_gamepad.disable_selection()
        self.calibrate_step = 0

    def stop_calibrate_clean(self):
        self.calibrate_last_value = None
        self.calibrate_last_value_frame = 0
        self.calibrate_data = [0,0,0,0]
        self.ui_gamepad.enable_selection()
        self.calibrate_step = 0
        self.ui_textbox_info.settext("Where to sail now captain ?")

    def start_calibrate_triggerleft(self):
        self.start_calibrate_init()
        self.ui_gamepad.reset_measurements_triggerleft()
        self.calibrate_triggerleft = True
        self.ui_gamepad.calibration.reset_trigger_left()

    def start_calibrate_stickleft(self):
        self.start_calibrate_init()
        self.ui_gamepad.reset_measurements_stickleft()
        self.calibrate_stickleft = True
        self.ui_gamepad.calibration.reset_axis_left()
        self.calibrate_axis = "x"

    def start_calibrate_stickright(self):
        self.start_calibrate_init()
        self.ui_gamepad.reset_measurements_stickright()
        self.calibrate_stickright = True
        self.ui_gamepad.calibration.reset_axis_right()
        self.calibrate_axis = "x"

    def start_calibrate_triggerright(self):
        self.start_calibrate_init()
        self.ui_gamepad.reset_measurements_triggerright()
        self.calibrate_triggerright = True
        self.ui_gamepad.calibration.reset_trigger_right()

    def stop_calibrate_triggerleft(self):
        self.stop_calibrate_clean()
        self.calibrate_triggerleft = False

    def stop_calibrate_stickleft(self):
        self.stop_calibrate_clean()
        self.calibrate_stickleft = False

    def stop_calibrate_stickright(self):
        self.calibrate_stickright = False
        self.stop_calibrate_clean()

    def stop_calibrate_triggerright(self):
        self.calibrate_triggerright = False
        self.stop_calibrate_clean()

    def run_calibrate_stickleft(self):
        if self.calibrate_axis == "x":
            if self.calibrate_last_value != self.ui_gamepad.leftx:
                self.calibrate_last_value = self.ui_gamepad.leftx
                self.calibrate_last_value_frame = pyxel.frame_count
        elif self.calibrate_axis == "y":
            if self.calibrate_last_value != self.ui_gamepad.lefty:
                self.calibrate_last_value = self.ui_gamepad.lefty
                self.calibrate_last_value_frame = pyxel.frame_count

        if self.calibrate_axis == "x":
            if self.calibrate_step == 0:
                self.ui_textbox_info.settext("Step 1/12: Push stick full right few seconds and release")
                self.calibrate_step = 1
                print(self.calibrate_data)

            elif self.calibrate_step == 1:

                if self.calibrate_last_value > self.ui_gamepad.calibration.axis_leftx_max/2 and (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.ui_gamepad.leftx_max) / self.ui_gamepad.leftx_max) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[3] = self.calibrate_last_value
                        self.calibrate_step = 2
                
            elif self.calibrate_step == 2:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value) / self.ui_gamepad.leftx_max) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[2] = self.calibrate_last_value
                        self.calibrate_step = 3

            elif self.calibrate_step == 3:
                self.ui_textbox_info.settext("Step 2/12: Push stick full right few seconds and release")
                self.calibrate_step = 4
                print(self.calibrate_data)
            
            elif self.calibrate_step == 4:

                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.calibrate_data[3]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[3] += self.calibrate_last_value
                        self.calibrate_step = 5

            elif self.calibrate_step == 5:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.calibrate_data[2]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[2] += self.calibrate_last_value
                        self.calibrate_step = 6

            elif self.calibrate_step == 6:
                self.ui_textbox_info.settext("Step 3/12: Push stick full right few seconds and release")
                self.calibrate_step = 7
                print(self.calibrate_data)
            
            elif self.calibrate_step == 7:

                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[3]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[3] += self.calibrate_last_value
                        self.calibrate_step = 8

            elif self.calibrate_step == 8:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[2]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[2] += self.calibrate_last_value
                        self.calibrate_step = 9
            
            elif self.calibrate_step == 9:
                self.ui_textbox_info.settext("Step 4/12: Push stick full left few seconds and release")
                self.calibrate_step = 10
                print(self.calibrate_data)

            elif self.calibrate_step == 10:

                if self.calibrate_last_value < self.ui_gamepad.calibration.axis_leftx_min/2 and (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.ui_gamepad.leftx_min) / self.ui_gamepad.leftx_min) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[1] = self.calibrate_last_value
                        self.calibrate_step = 11
                
            elif self.calibrate_step == 11:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value) / self.ui_gamepad.leftx_min) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[0] = self.calibrate_last_value
                        self.calibrate_step = 12

            elif self.calibrate_step == 12:
                self.ui_textbox_info.settext("Step 5/12: Push stick full left few seconds and release")
                self.calibrate_step = 13
                print(self.calibrate_data)
            
            elif self.calibrate_step == 13:

                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.calibrate_data[1]) / self.calibrate_data[1]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[1] += self.calibrate_last_value
                        self.calibrate_step = 14

            elif self.calibrate_step == 14:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.calibrate_data[0]) / self.calibrate_data[1]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[0] += self.calibrate_last_value
                        self.calibrate_step = 15

            elif self.calibrate_step == 15:
                self.ui_textbox_info.settext("Step 6/12: Push stick full left few seconds and release")
                self.calibrate_step = 16
                print(self.calibrate_data)
            
            elif self.calibrate_step == 16:

                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[1]) / self.calibrate_data[1]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[1] += self.calibrate_last_value
                        self.calibrate_step = 17

            elif self.calibrate_step == 17:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[0]) / self.calibrate_data[1]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[0] += self.calibrate_last_value
                        self.calibrate_step = 18

            elif self.calibrate_step == 18:
                print(self.calibrate_data) 

                if self.calibrate_data[3] == 3 * self.ui_gamepad.calibration.axis_leftx_max \
                    and self.calibrate_data[2] == 0 \
                    and self.calibrate_data[1] == 3 * self.ui_gamepad.calibration.axis_leftx_min \
                    and self.calibrate_data[0] == 0:
                    # nothing to do it's perfect !
                    pass
                else:
                    self.calibrate_data[3] = self.calibrate_data[3] / 3  # average
                    self.calibrate_data[2] = self.calibrate_data[2] / 3  # average
                    self.calibrate_data[1] = self.calibrate_data[1] / 3  # average
                    self.calibrate_data[0] = self.calibrate_data[0] / 3  # average

                    axis_center = (self.calibrate_data[2] + self.calibrate_data[0]) / 2

                    self.calibrate_data[3] = self.calibrate_data[3] - axis_center   # recenter
                    self.calibrate_data[2] = self.calibrate_data[2] - axis_center   # recenter
                    self.calibrate_data[1] = self.calibrate_data[1] - axis_center   # recenter
                    self.calibrate_data[0] = self.calibrate_data[0] - axis_center   # recenter

                    axis_max = AXIS_MAX_PERCENT * min(abs(self.calibrate_data[1]), self.calibrate_data[3]) / 100
                    deadzone = AXIS_DEADZONE_PERCENT * (abs(self.calibrate_data[0]) + abs(self.calibrate_data[2])) / 200
                    if (100 * deadzone / axis_max) < AXIS_DEADZONE_PERCENT_MINI:
                        deadzone = AXIS_DEADZONE_PERCENT_MINI * axis_max / 100

                    self.ui_gamepad.calibration.axis_leftx_max = int(axis_max)
                    self.ui_gamepad.calibration.axis_leftx_min = -int(axis_max)
                    self.ui_gamepad.calibration.axis_leftx_center = - int(axis_center)
                    self.ui_gamepad.calibration.axis_leftx_deadzone  = int(deadzone)

                    self.ui_gamepad.calibration.axis_leftx_antideadzone = int(AXIS_ANTIDEADZONE_PERCENT * self.ui_gamepad.calibration.axis_leftx_deadzone / 100)  # -20 %

                self.calibrate_axis="y"
                self.calibrate_step=0
                self.calibrate_data = [0,0,0,0]
                self.calibrate_last_value = None
                self.calibrate_last_value_frame = 0


        elif self.calibrate_axis == "y":
            if self.calibrate_step == 0:
                self.ui_textbox_info.settext("Step 7/12: Push stick full down few seconds and release")
                self.calibrate_step = 1
                print(self.calibrate_data)

            elif self.calibrate_step == 1:

                if self.calibrate_last_value > self.ui_gamepad.calibration.axis_lefty_max/2 and (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.ui_gamepad.leftx_max) / self.ui_gamepad.leftx_max) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[3] = self.calibrate_last_value
                        self.calibrate_step = 2
                
            elif self.calibrate_step == 2:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value) / self.ui_gamepad.leftx_max) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[2] = self.calibrate_last_value
                        self.calibrate_step = 3

            elif self.calibrate_step == 3:
                self.ui_textbox_info.settext("Step 8/12: Push stick full down few seconds and release")
                self.calibrate_step = 4
                print(self.calibrate_data)
            
            elif self.calibrate_step == 4:

                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.calibrate_data[3]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[3] += self.calibrate_last_value
                        self.calibrate_step = 5

            elif self.calibrate_step == 5:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.calibrate_data[2]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[2] += self.calibrate_last_value
                        self.calibrate_step = 6

            elif self.calibrate_step == 6:
                self.ui_textbox_info.settext("Step 9/12: Push stick full down few seconds and release")
                self.calibrate_step = 7
                print(self.calibrate_data)
            
            elif self.calibrate_step == 7:

                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[3]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[3] += self.calibrate_last_value
                        self.calibrate_step = 8

            elif self.calibrate_step == 8:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[2]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[2] += self.calibrate_last_value
                        self.calibrate_step = 9
            
            elif self.calibrate_step == 9:
                self.ui_textbox_info.settext("Step 10/12: Push stick full up few seconds and release")
                self.calibrate_step = 10
                print(self.calibrate_data)

            elif self.calibrate_step == 10:

                if self.calibrate_last_value < self.ui_gamepad.calibration.axis_lefty_min/2 and (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.ui_gamepad.leftx_min) / self.ui_gamepad.leftx_min) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[1] = self.calibrate_last_value
                        self.calibrate_step = 11
                
            elif self.calibrate_step == 11:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value) / self.ui_gamepad.leftx_min) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[0] = self.calibrate_last_value
                        self.calibrate_step = 12

            elif self.calibrate_step == 12:
                self.ui_textbox_info.settext("Step 11/12: Push stick full up few seconds and release")
                self.calibrate_step = 13
                print(self.calibrate_data)
            
            elif self.calibrate_step == 13:

                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.calibrate_data[1]) / self.calibrate_data[1]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[1] += self.calibrate_last_value
                        self.calibrate_step = 14

            elif self.calibrate_step == 14:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.calibrate_data[0]) / self.calibrate_data[1]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[0] += self.calibrate_last_value
                        self.calibrate_step = 15

            elif self.calibrate_step == 15:
                self.ui_textbox_info.settext("Step 12/12: Push stick full up few seconds and release")
                self.calibrate_step = 16
                print(self.calibrate_data)
            
            elif self.calibrate_step == 16:

                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[1]) / self.calibrate_data[1]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[1] += self.calibrate_last_value
                        self.calibrate_step = 17

            elif self.calibrate_step == 17:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[0]) / self.calibrate_data[1]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[0] += self.calibrate_last_value
                        self.calibrate_step = 18


            elif self.calibrate_step == 18:
                print(self.calibrate_data) 

                if self.calibrate_data[3] == 3 * self.ui_gamepad.calibration.axis_lefty_max \
                    and self.calibrate_data[2] == 0 \
                    and self.calibrate_data[1] == 3 * self.ui_gamepad.calibration.axis_lefty_min \
                    and self.calibrate_data[0] == 0:
                    # nothing to do it's perfect !
                    pass
                else:
                    self.calibrate_data[3] = self.calibrate_data[3] / 3  # average
                    self.calibrate_data[2] = self.calibrate_data[2] / 3  # average
                    self.calibrate_data[1] = self.calibrate_data[1] / 3  # average
                    self.calibrate_data[0] = self.calibrate_data[0] / 3  # average

                    axis_center = (self.calibrate_data[2] + self.calibrate_data[0]) / 2

                    self.calibrate_data[3] = self.calibrate_data[3] - axis_center   # recenter
                    self.calibrate_data[2] = self.calibrate_data[2] - axis_center   # recenter
                    self.calibrate_data[1] = self.calibrate_data[1] - axis_center   # recenter
                    self.calibrate_data[0] = self.calibrate_data[0] - axis_center   # recenter

                    axis_max = AXIS_MAX_PERCENT * min(abs(self.calibrate_data[1]), self.calibrate_data[3]) / 100
                    deadzone = AXIS_DEADZONE_PERCENT * (abs(self.calibrate_data[0]) + abs(self.calibrate_data[2])) / 200

                    if (100 * deadzone / axis_max) < AXIS_DEADZONE_PERCENT_MINI:
                        deadzone = AXIS_DEADZONE_PERCENT_MINI * axis_max / 100

                    self.ui_gamepad.calibration.axis_lefty_max = int(axis_max)
                    self.ui_gamepad.calibration.axis_lefty_min = -int(axis_max)
                    self.ui_gamepad.calibration.axis_lefty_center = -int(axis_center)
                    self.ui_gamepad.calibration.axis_lefty_deadzone  = int(deadzone)

                    self.ui_gamepad.calibration.axis_lefty_antideadzone = int(80 * self.ui_gamepad.calibration.axis_lefty_deadzone / 100)  # -20 %

                print(self.ui_gamepad.calibration)
                self.ui_gamepad.calibration.apply_parameters()
                self.ui_textbox_info.settext("Calibration done")
                self.stop_calibrate_stickleft()


    def run_calibrate_stickright(self):
        if self.calibrate_axis == "x":
            if self.calibrate_last_value != self.ui_gamepad.rightx:
                self.calibrate_last_value = self.ui_gamepad.rightx
                self.calibrate_last_value_frame = pyxel.frame_count
        elif self.calibrate_axis == "y":
            if self.calibrate_last_value != self.ui_gamepad.righty:
                self.calibrate_last_value = self.ui_gamepad.righty
                self.calibrate_last_value_frame = pyxel.frame_count

        if self.calibrate_axis == "x":
            if self.calibrate_step == 0:
                self.ui_textbox_info.settext("Step 1/12: Push stick full right few seconds and release")
                self.calibrate_step = 1
                print(self.calibrate_data)

            elif self.calibrate_step == 1:

                if self.calibrate_last_value > self.ui_gamepad.calibration.axis_rightx_max/2 and (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.ui_gamepad.rightx_max) / self.ui_gamepad.rightx_max) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[3] = self.calibrate_last_value
                        self.calibrate_step = 2
                
            elif self.calibrate_step == 2:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value) / self.ui_gamepad.rightx_max) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[2] = self.calibrate_last_value
                        self.calibrate_step = 3

            elif self.calibrate_step == 3:
                self.ui_textbox_info.settext("Step 2/12: Push stick full right few seconds and release")
                self.calibrate_step = 4
                print(self.calibrate_data)
            
            elif self.calibrate_step == 4:

                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.calibrate_data[3]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[3] += self.calibrate_last_value
                        self.calibrate_step = 5

            elif self.calibrate_step == 5:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.calibrate_data[2]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[2] += self.calibrate_last_value
                        self.calibrate_step = 6

            elif self.calibrate_step == 6:
                self.ui_textbox_info.settext("Step 3/12: Push stick full right few seconds and release")
                self.calibrate_step = 7
                print(self.calibrate_data)
            
            elif self.calibrate_step == 7:

                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[3]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[3] += self.calibrate_last_value
                        self.calibrate_step = 8

            elif self.calibrate_step == 8:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[2]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[2] += self.calibrate_last_value
                        self.calibrate_step = 9
            
            elif self.calibrate_step == 9:
                self.ui_textbox_info.settext("Step 4/12: Push stick full left few seconds and release")
                self.calibrate_step = 10
                print(self.calibrate_data)

            elif self.calibrate_step == 10:

                if self.calibrate_last_value < self.ui_gamepad.calibration.axis_rightx_min/2 and (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.ui_gamepad.rightx_min) / self.ui_gamepad.rightx_min) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[1] = self.calibrate_last_value
                        self.calibrate_step = 11
                
            elif self.calibrate_step == 11:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value) / self.ui_gamepad.rightx_min) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[0] = self.calibrate_last_value
                        self.calibrate_step = 12

            elif self.calibrate_step == 12:
                self.ui_textbox_info.settext("Step 5/12: Push stick full left few seconds and release")
                self.calibrate_step = 13
                print(self.calibrate_data)
            
            elif self.calibrate_step == 13:

                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.calibrate_data[1]) / self.calibrate_data[1]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[1] += self.calibrate_last_value
                        self.calibrate_step = 14

            elif self.calibrate_step == 14:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.calibrate_data[0]) / self.calibrate_data[1]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[0] += self.calibrate_last_value
                        self.calibrate_step = 15

            elif self.calibrate_step == 15:
                self.ui_textbox_info.settext("Step 6/12: Push stick full left few seconds and release")
                self.calibrate_step = 16
                print(self.calibrate_data)
            
            elif self.calibrate_step == 16:

                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[1]) / self.calibrate_data[1]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[1] += self.calibrate_last_value
                        self.calibrate_step = 17

            elif self.calibrate_step == 17:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[0]) / self.calibrate_data[1]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[0] += self.calibrate_last_value
                        self.calibrate_step = 18


            elif self.calibrate_step == 18:
                print(self.calibrate_data) 

                if self.calibrate_data[3] == 3 * self.ui_gamepad.calibration.axis_rightx_max \
                    and self.calibrate_data[2] == 0 \
                    and self.calibrate_data[1] == 3 * self.ui_gamepad.calibration.axis_rightx_min \
                    and self.calibrate_data[0] == 0:
                    # nothing to do it's perfect !
                    pass
                else:
                    self.calibrate_data[3] = self.calibrate_data[3] / 3  # average
                    self.calibrate_data[2] = self.calibrate_data[2] / 3  # average
                    self.calibrate_data[1] = self.calibrate_data[1] / 3  # average
                    self.calibrate_data[0] = self.calibrate_data[0] / 3  # average

                    axis_center = (self.calibrate_data[2] + self.calibrate_data[0]) / 2

                    self.calibrate_data[3] = self.calibrate_data[3] - axis_center   # recenter
                    self.calibrate_data[2] = self.calibrate_data[2] - axis_center   # recenter
                    self.calibrate_data[1] = self.calibrate_data[1] - axis_center   # recenter
                    self.calibrate_data[0] = self.calibrate_data[0] - axis_center   # recenter

                    axis_max = AXIS_MAX_PERCENT * min(abs(self.calibrate_data[1]), self.calibrate_data[3]) / 100
                    deadzone = AXIS_DEADZONE_PERCENT * (abs(self.calibrate_data[0]) + abs(self.calibrate_data[2])) / 200

                    if (100 * deadzone / axis_max) < AXIS_DEADZONE_PERCENT_MINI:
                        deadzone = AXIS_DEADZONE_PERCENT_MINI * axis_max / 100

                    self.ui_gamepad.calibration.axis_rightx_max = int(axis_max)
                    self.ui_gamepad.calibration.axis_rightx_min = -int(axis_max)
                    self.ui_gamepad.calibration.axis_rightx_center = -int(axis_center)
                    self.ui_gamepad.calibration.axis_rightx_deadzone  = int(deadzone)

                    self.ui_gamepad.calibration.axis_rightx_antideadzone = int(80 * self.ui_gamepad.calibration.axis_rightx_deadzone / 100)  # -20 %

                self.calibrate_axis="y"
                self.calibrate_step=0
                self.calibrate_data = [0,0,0,0]
                self.calibrate_last_value = None
                self.calibrate_last_value_frame = 0


        elif self.calibrate_axis == "y":
            if self.calibrate_step == 0:
                self.ui_textbox_info.settext("Step 7/12: Push stick full down few seconds and release")
                self.calibrate_step = 1
                print(self.calibrate_data)

            elif self.calibrate_step == 1:

                if self.calibrate_last_value > self.ui_gamepad.calibration.axis_righty_max/2 and (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.ui_gamepad.rightx_max) / self.ui_gamepad.rightx_max) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[3] = self.calibrate_last_value
                        self.calibrate_step = 2
                
            elif self.calibrate_step == 2:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value) / self.ui_gamepad.rightx_max) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[2] = self.calibrate_last_value
                        self.calibrate_step = 3

            elif self.calibrate_step == 3:
                self.ui_textbox_info.settext("Step 8/12: Push stick full down few seconds and release")
                self.calibrate_step = 4
                print(self.calibrate_data)
            
            elif self.calibrate_step == 4:

                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.calibrate_data[3]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[3] += self.calibrate_last_value
                        self.calibrate_step = 5

            elif self.calibrate_step == 5:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.calibrate_data[2]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[2] += self.calibrate_last_value
                        self.calibrate_step = 6

            elif self.calibrate_step == 6:
                self.ui_textbox_info.settext("Step 9/12: Push stick full down few seconds and release")
                self.calibrate_step = 7
                print(self.calibrate_data)
            
            elif self.calibrate_step == 7:

                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[3]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[3] += self.calibrate_last_value
                        self.calibrate_step = 8

            elif self.calibrate_step == 8:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[2]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[2] += self.calibrate_last_value
                        self.calibrate_step = 9
            
            elif self.calibrate_step == 9:
                self.ui_textbox_info.settext("Step 10/12: Push stick full up few seconds and release")
                self.calibrate_step = 10
                print(self.calibrate_data)

            elif self.calibrate_step == 10:

                if self.calibrate_last_value < self.ui_gamepad.calibration.axis_righty_min/2 and (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.ui_gamepad.rightx_min) / self.ui_gamepad.rightx_min) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[1] = self.calibrate_last_value
                        self.calibrate_step = 11
                
            elif self.calibrate_step == 11:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value) / self.ui_gamepad.rightx_min) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[0] = self.calibrate_last_value
                        self.calibrate_step = 12

            elif self.calibrate_step == 12:
                self.ui_textbox_info.settext("Step 11/12: Push stick full up few seconds and release")
                self.calibrate_step = 13
                print(self.calibrate_data)
            
            elif self.calibrate_step == 13:

                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.calibrate_data[1]) / self.calibrate_data[1]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[1] += self.calibrate_last_value
                        self.calibrate_step = 14

            elif self.calibrate_step == 14:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (self.calibrate_last_value - self.calibrate_data[0]) / self.calibrate_data[1]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[0] += self.calibrate_last_value
                        self.calibrate_step = 15

            elif self.calibrate_step == 15:
                self.ui_textbox_info.settext("Step 12/12: Push stick full up few seconds and release")
                self.calibrate_step = 16
                print(self.calibrate_data)
            
            elif self.calibrate_step == 16:

                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[1]) / self.calibrate_data[1]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[1] += self.calibrate_last_value
                        self.calibrate_step = 17

            elif self.calibrate_step == 17:
                if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                    if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[0]) / self.calibrate_data[1]) < CALIBRATE_DETECTION_PERCENT:
                        self.calibrate_data[0] += self.calibrate_last_value
                        self.calibrate_step = 18


            elif self.calibrate_step == 18:
                print(self.calibrate_data) 

                if self.calibrate_data[3] == 3 * self.ui_gamepad.calibration.axis_righty_max \
                    and self.calibrate_data[2] == 0 \
                    and self.calibrate_data[1] == 3 * self.ui_gamepad.calibration.axis_righty_min \
                    and self.calibrate_data[0] == 0:
                    # nothing to do it's perfect !
                    pass
                else:
                    self.calibrate_data[3] = self.calibrate_data[3] / 3  # average
                    self.calibrate_data[2] = self.calibrate_data[2] / 3  # average
                    self.calibrate_data[1] = self.calibrate_data[1] / 3  # average
                    self.calibrate_data[0] = self.calibrate_data[0] / 3  # average

                    axis_center = (self.calibrate_data[2] + self.calibrate_data[0]) / 2

                    self.calibrate_data[3] = self.calibrate_data[3] - axis_center   # recenter
                    self.calibrate_data[2] = self.calibrate_data[2] - axis_center   # recenter
                    self.calibrate_data[1] = self.calibrate_data[1] - axis_center   # recenter
                    self.calibrate_data[0] = self.calibrate_data[0] - axis_center   # recenter

                    axis_max = AXIS_MAX_PERCENT * min(abs(self.calibrate_data[1]), self.calibrate_data[3]) / 100
                    deadzone = AXIS_DEADZONE_PERCENT * (abs(self.calibrate_data[0]) + abs(self.calibrate_data[2])) / 200

                    if (100 * deadzone / axis_max) < AXIS_DEADZONE_PERCENT_MINI:
                        deadzone = AXIS_DEADZONE_PERCENT_MINI * axis_max / 100

                    self.ui_gamepad.calibration.axis_righty_max = int(axis_max)
                    self.ui_gamepad.calibration.axis_righty_min = -int(axis_max)
                    self.ui_gamepad.calibration.axis_righty_center = -int(axis_center)
                    self.ui_gamepad.calibration.axis_righty_deadzone  = int(deadzone)

                    self.ui_gamepad.calibration.axis_righty_antideadzone = int(AXIS_ANTIDEADZONE_PERCENT * self.ui_gamepad.calibration.axis_righty_deadzone / 100)  # -20 %

                print(self.ui_gamepad.calibration)
                self.ui_gamepad.calibration.apply_parameters()
                self.ui_textbox_info.settext("Calibration done")
                self.stop_calibrate_stickright()

    def run_calibrate_triggerleft(self):
        
        if self.calibrate_last_value != self.ui_gamepad.triggerleft:
            self.calibrate_last_value = self.ui_gamepad.triggerleft
            self.calibrate_last_value_frame = pyxel.frame_count

        if self.calibrate_step == 0:
            self.ui_textbox_info.settext("Step 1/3: Push trigger to max few seconds and release")
            self.calibrate_step = 1
            print(self.calibrate_data)

        elif self.calibrate_step == 1:

            if self.calibrate_last_value > self.ui_gamepad.calibration.trigger_left_max/2 and (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                if abs(100 * (self.calibrate_last_value - self.ui_gamepad.triggerleft_max) / self.ui_gamepad.triggerleft_max) < CALIBRATE_DETECTION_PERCENT:
                    self.calibrate_data[3] = self.calibrate_last_value
                    self.calibrate_step = 2

        elif self.calibrate_step == 2:
            if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                if abs(100 * (self.calibrate_last_value - self.ui_gamepad.triggerleft_min) / self.ui_gamepad.triggerleft_max) < CALIBRATE_DETECTION_PERCENT:
                    self.calibrate_data[2] = self.calibrate_last_value
                    self.calibrate_step = 3

        elif self.calibrate_step == 3:
            self.ui_textbox_info.settext("Step 2/3: Push trigger to max few seconds and release")
            self.calibrate_step = 4
            print(self.calibrate_data)


        elif self.calibrate_step == 4:

            if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                if abs(100 * (self.calibrate_last_value - self.calibrate_data[3]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                    self.calibrate_data[3] += self.calibrate_last_value
                    self.calibrate_step = 5

        elif self.calibrate_step == 5:
            if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                if abs(100 * (self.calibrate_last_value - self.calibrate_data[2]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                    self.calibrate_data[2] += self.calibrate_last_value
                    self.calibrate_step = 6
        
        elif self.calibrate_step == 6:
            self.ui_textbox_info.settext("Step 3/3: Push trigger to max few seconds and release")
            self.calibrate_step = 7
            print(self.calibrate_data)

        elif self.calibrate_step == 7:

            if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[3]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                    self.calibrate_data[3] += self.calibrate_last_value
                    self.calibrate_step = 8

        elif self.calibrate_step == 8:
            if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[2]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                    self.calibrate_data[2] += self.calibrate_last_value
                    self.calibrate_step = 9
        
        elif self.calibrate_step == 9:
            print(self.calibrate_data) 

            if self.calibrate_data[3] == 3 * self.ui_gamepad.calibration.trigger_right_max\
                and self.calibrate_data[2] == 0:
                # nothing to do it's perfect !
                pass
            else:

                # if we change max value, the minimum value is lowered
                # see kernel driver code for trigger:
                #
                # 	value = (int16_t)(trigger_left_max - (data->data[2] | (data->data[3] << 8)));
                #	input_report_abs(indev, ABS_HAT2X,
                #       ( value < trigger_left_deadzone )? 0 : value - trigger_left_antideadzone);
                #

                self.calibrate_data[3] = self.calibrate_data[3] / 3
                self.calibrate_data[2] = self.calibrate_data[2] / 3

                maxvalue = self.calibrate_data[3] - self.calibrate_data[2]
                maxvalue = TRIGGER_MAX_PERCENT * maxvalue / 100
                deadzone = (TRIGGER_DEADZONE_PERCENT - 100) * self.calibrate_data[2] / 100
                #                                      ^ we remove 100 because calibrate_data[2]
                #                                        is substracted in maxvalue
                
                self.ui_gamepad.calibration.trigger_left_max  = int(maxvalue)
                self.ui_gamepad.calibration.trigger_left_deadzone  = int(deadzone)
                self.ui_gamepad.calibration.trigger_left_antideadzone = int(TRIGGER_ANTIDEADZONE_PERCENT * deadzone / 100)

            self.ui_gamepad.calibration.apply_parameters()
            self.ui_textbox_info.settext("Calibration done")
            self.stop_calibrate_triggerleft()

    def run_calibrate_triggerright(self):
        self.ui_gamepad.calibration.reset_trigger_right()

        
        if self.calibrate_last_value != self.ui_gamepad.triggerright:
            self.calibrate_last_value = self.ui_gamepad.triggerright
            self.calibrate_last_value_frame = pyxel.frame_count

        if self.calibrate_step == 0:
            self.ui_textbox_info.settext("Step 1/3: Push trigger to max few seconds and release")
            self.calibrate_step = 1
            print(self.calibrate_data)

        elif self.calibrate_step == 1:

            if self.calibrate_last_value > self.ui_gamepad.calibration.trigger_right_max/2 and (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                if abs(100 * (self.calibrate_last_value - self.ui_gamepad.triggerright_max) / self.ui_gamepad.triggerright_max) < CALIBRATE_DETECTION_PERCENT:
                    self.calibrate_data[3] = self.calibrate_last_value
                    self.calibrate_step = 2

        elif self.calibrate_step == 2:
            if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                if abs(100 * (self.calibrate_last_value - self.ui_gamepad.triggerright_min) / self.ui_gamepad.triggerright_max) < CALIBRATE_DETECTION_PERCENT:
                    self.calibrate_data[2] = self.calibrate_last_value
                    self.calibrate_step = 3

        elif self.calibrate_step == 3:
            self.ui_textbox_info.settext("Step 2/3: Push trigger to max few seconds and release")
            self.calibrate_step = 4
            print(self.calibrate_data)


        elif self.calibrate_step == 4:

            if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                if abs(100 * (self.calibrate_last_value - self.calibrate_data[3]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                    self.calibrate_data[3] += self.calibrate_last_value
                    self.calibrate_step = 5

        elif self.calibrate_step == 5:
            if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                if abs(100 * (self.calibrate_last_value - self.calibrate_data[2]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                    self.calibrate_data[2] += self.calibrate_last_value
                    self.calibrate_step = 6
        
        elif self.calibrate_step == 6:
            self.ui_textbox_info.settext("Step 3/3: Push trigger to max few seconds and release")
            self.calibrate_step = 7
            print(self.calibrate_data)

        elif self.calibrate_step == 7:

            if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[3]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                    self.calibrate_data[3] += self.calibrate_last_value
                    self.calibrate_step = 8

        elif self.calibrate_step == 8:
            if (pyxel.frame_count - self.calibrate_last_value_frame) > CALIBRATION_DETECTION_FPS:
                if abs(100 * (2 * self.calibrate_last_value - self.calibrate_data[2]) / self.calibrate_data[3]) < CALIBRATE_DETECTION_PERCENT:
                    self.calibrate_data[2] += self.calibrate_last_value
                    self.calibrate_step = 9
        
        elif self.calibrate_step == 9:
            print(self.calibrate_data)
            if self.calibrate_data[3] == 3 * self.ui_gamepad.calibration.trigger_right_max\
                and self.calibrate_data[2] == 0:
                # nothing to do it's perfect !
                pass
            else:
                # if we change max value, the minimum value is lowered
                # see kernel driver code for trigger:
                #
                # 	value = (int16_t)(trigger_right_max - (data->data[2] | (data->data[3] << 8)));
                #	input_report_abs(indev, ABS_HAT2X,
                #       ( value < trigger_right_deadzone )? 0 : value - trigger_right_antideadzone);
                #

                self.calibrate_data[3] = self.calibrate_data[3] / 3
                self.calibrate_data[2] = self.calibrate_data[2] / 3

                maxvalue = self.calibrate_data[3] -  self.calibrate_data[2]
                maxvalue = TRIGGER_MAX_PERCENT * maxvalue / 100
                deadzone = (TRIGGER_DEADZONE_PERCENT - 100) * self.calibrate_data[2] / 100
                #                                      ^ we remove 100 because calibrate_data[2]
                #                                        is substracted in maxvalue
                
                self.ui_gamepad.calibration.trigger_right_max  = int(maxvalue)
                self.ui_gamepad.calibration.trigger_right_deadzone  = int(deadzone)
                self.ui_gamepad.calibration.trigger_right_antideadzone = int(TRIGGER_ANTIDEADZONE_PERCENT * deadzone / 100)

            self.ui_gamepad.calibration.apply_parameters()
            self.ui_textbox_info.settext("Calibration done")
            self.stop_calibrate_triggerright()

GPCalibrate()
