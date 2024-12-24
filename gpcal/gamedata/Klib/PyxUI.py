"""
    PyxUI: a very basic Pyxel User Interface library
    Author: Kdog
    Version: 0.1
    SPDX-License-Identifier: MIT
"""
import pyxel
import struct
import os
from pathlib import Path
import math

from Klib.RPocket import RPCalibration

INPUT_SEARCH_PATH="/sys/class/input"
INPUT_DEV_DIR="/dev/input"
GAMEPAD_NAME="Retroid Pocket Gamepad"

class UIObject:
    def __init__(self,x=0,y=0,w=320,h=240):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.umplus12 = pyxel.Font("umplus_j12r.bdf")
        self.visible = True

    def draw_text_with_border(self, x, y, s, col, bcol, font=None):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx != 0 or dy != 0:
                    pyxel.text(
                        x + dx,
                        y + dy,
                        s,
                        bcol,
                        font
                    )
        pyxel.text(x, y, s, col, font)
    
    def toggle_visible(self):
        self.visible = not self.visible

class UIPanel(UIObject):
    def __init__(self,x=0,y=0,w=320,h=240,title="Panel",color=0,lcolor=7,selected=0,btitle=""):
        super().__init__(x,y,w,h)
        self.title = title
        self.btitle = btitle
        self.color = color
        self.lcolor = lcolor
        
        self.ui_objects = []
        self._selected = selected
        self._selection_enabled = True

    def _select_next(self,shift):
        try:
            self._selected = (self._selected + shift) % len(self.ui_objects)
            self.ui_objects[self._selected]._toggle_selected()
        except AttributeError:
            self._select_next(shift)

    def add_uiobject(self, uiobject, selected = False):
        if selected:
            try:
                uiobject._toggle_selected()
                selected = len(self.ui_objects)
            except AttributeError:
                pass
        
        self.ui_objects.append(uiobject)

    def select_first(self):
        self._select_next(1)

    def select_none(self):
        self.ui_objects[self._selected]._selected = False
        self._selected = -1

    def disable_selection(self):
        self._selection_enabled = False
    
    def enable_selection(self):
        self._selection_enabled = True

    def update_selection(self):
        if (self._selected > -1 and self._selection_enabled):
            shift = 0
            if pyxel.btnp(pyxel.KEY_RIGHT) \
                or pyxel.btnp(pyxel.KEY_DOWN) \
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT) \
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
                shift = 1
            elif pyxel.btnp(pyxel.KEY_LEFT) \
                or pyxel.btnp(pyxel.KEY_UP) \
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT) \
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
                shift = -1

            if shift:
                self.ui_objects[self._selected]._toggle_selected()
                self._select_next(shift)

    def update(self):

        self.update_selection()

        for _,ui_object in enumerate(self.ui_objects):
            ui_object.update()

    def draw(self):
        if not self.visible:
            return
        
        pyxel.rect(self.x, self.y, self.w, self.h, self.color)
        pyxel.rectb(self.x + 10, self.y + 10, self.w - 20, self.h - 20, self.lcolor)

        self.draw_text_with_border(self.x + 20, self.y + 4, self.title,0, 7, self.umplus12)
        self.draw_text_with_border(self.x + 200, self.y + self.h - 13, self.btitle,0, 7)
        for _,ui_object in enumerate(self.ui_objects):
            ui_object.draw()

class UISelectable(UIObject):
    def __init__(self,x,y,w,h,selected=False,scolor=8):
        super().__init__(x,y,w,h)
        self._selected = selected
        self.scolor = scolor

    def _toggle_selected(self):
        self._selected = not self._selected

class UIButton(UISelectable):
    def __init__(self,x=0,y=0,w=60,h=16,text="Button",fcolor=13,scolor=7,pcolor=7,tcolor=0,selected=False, callback=None):
        super().__init__(x,y,w,h,selected,scolor)

        self.fcolor = fcolor          # button color
        self.pcolor = pcolor        # pressed color
        self.tcolor = tcolor        # text color

        self.text = text
        self.callback = callback

        self._pressed = False
        self._pressed_frame = 0

    def _toggle_pressed(self):
        self._pressed = not self._pressed
        self._pressed_frame = pyxel.frame_count

    def _run_callback(self):
        if self.callback != None:
            self.callback()

    def _update_pressed(self):
        if self._selected \
              and ( pyxel.btnp(pyxel.KEY_RETURN) \
                    or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)):
            self._toggle_pressed()
            self._run_callback()

    def settext(self,text):
        self.text = text

    def update(self):
        self._update_pressed()

    def draw(self):
        if not self.visible:
            return
        
        color = self.fcolor
        if self._pressed:
            if pyxel.frame_count - self._pressed_frame < 30:
                color = self.pcolor
            else:
                self._toggle_pressed()

        pyxel.rect(self.x, self.y, self.w, self.h, color)

        pyxel.text(self.x + 4,self.y + 2,f"{self.text}",self.tcolor,self.umplus12)

        if self._selected:
            pyxel.rectb(self.x - 1, self.y - 1, self.w + 2, self.h + 2, self.scolor)

class UIGauge(UIButton):
    def __init__(self,calibration,pname="triggerleft",name="Trigger Left",x=0,y=0,w=20,h=80,text="",fcolor=7,lcolor=7,scolor=8,selected=False,callback=None):
        super().__init__(x,y,w,h,text,fcolor,scolor,scolor,0,selected,callback)

        self.name = name
        self.axis=Axis(calibration,f"{pname}",f"{name}","v")
        
        self.lcolor = lcolor # line color

        self.truncate = False

        self.fill = 0

    def update(self):
        self.axis.update()
        self.fill = self.h * (self.axis.value / self.axis.calibration.get_range())
        super().update()

    def reset_measurements(self):
        self.axis.reset_measurements()

    def toggle_truncate(self):
        self.truncate = not self.truncate
    
    def draw(self):
        if not self.visible:
            return
        
        # red line if selected
        if self._selected:
            pyxel.rectb(self.x-1,self.y-1,self.w+2,self.h+2,self.scolor)

        lcolor = self.lcolor
        if self._pressed:
            if pyxel.frame_count - self._pressed_frame < 30:
                lcolor = self.pcolor
            else:
                self._toggle_pressed()
        
        fcolor = self.fcolor
        if self.fill >= self.h-2:
            if self.truncate:
                self.fill = self.h-2
            fcolor = 3
            lcolor = 3

        pyxel.rectb(self.x,self.y,self.w,self.h,lcolor)
        pyxel.rect(self.x + 1,self.y + 1,self.w - 2,self.fill,fcolor)
        hooking_progress=self.axis.get_hooking_progress()
        if hooking_progress >0:
            pyxel.rect(self.x + 1,self.y + 1,int(hooking_progress * (self.w - 2)),self.fill,self.scolor)
    
    def __str__(self):
        return self.axis.__str__()

class Axis:
    def __init__(self,calibration,pname="leftx",name="Left X", orientation="h"):
        self.calibration=calibration
        self.pname=pname
        self.name=name
        self.orientation=orientation
        self.value=0
        self.value_frame=pyxel.frame_count
        self.percent=0
        self.max=None
        self.min=None

        self.hooking_positive=False
        self.hooking_negative=False

        if orientation == "h":
            self.positive_indication="right"
            self.negative_indication="left"
        elif self.orientation == "v":
            self.positive_indication="down"
            self.negative_indication="up"
        else:
            self.positive_indication="positive"
            self.negative_indication="negative"
    
    def update_value(self,value):
        self.value = value
        self.value_frame = pyxel.frame_count
        self.percent = 100 * self.value / self.calibration.max

    def update(self):

        if self.hooking_positive:
            if pyxel.frame_count - self.value_frame > self.hooking_frames:
                if 2 * self.value < self.calibration.max and self.max != None:
                    # minimum should be less than 50% of the max value
                    if self.min == None:
                        self.min = self.value
                    else:
                        self.min = min(self.min,self.value)
                
                elif 2* self.value > self.calibration.max:
                    # maximum should be more than 50% of the max value
                    if self.max == None:
                        self.max = self.value
                    else:            
                        self.max = max(self.max,self.value)
                
        elif self.hooking_negative:
            if pyxel.frame_count - self.value_frame > self.hooking_frames:
                if 2* abs(self.value) < self.calibration.max and self.min != None:
                    # maximum should be less than 50% of the max value
                    if self.max == None:
                        self.max = self.value
                    else:            
                        self.max = min(self.max,self.value)

                elif 2 * self.value < self.calibration.min:
                    # minimum should be lower than 50% of the min value
                    if self.min == None:
                        self.min = self.value
                    else:
                        self.min = min(self.min,self.value)

        else:
            
            if self.min == None:
                self.min = self.value
            else:
                self.min = min(self.min,self.value)
            
            if self.max == None:
                self.max = self.value
            else:            
                self.max = max(self.max,self.value)


    def reset_measurements(self):
        self.max = None
        self.min = None

    def enable_hooking_positive(self,frames=30):
        self.last_hooking_frame=0
        self.hooking_frames=frames
        self.hooking_positive = True
        self.reset_measurements()
    
    def enable_hooking_negative(self,frames=30):
        self.last_hooking_frame=0
        self.hooking_frames=frames
        self.hooking_negative = True
        self.reset_measurements()

    def get_hooking_progress(self):
        if self.hooking_negative or self.hooking_positive:
            return min((pyxel.frame_count - self.value_frame) / self.hooking_frames, 1 )
        else:
            return -1
    
    def disable_hooking(self):
        self.hooking_negative = False
        self.hooking_positive = False
        self.last_hooking_frame=0

    def __str__(self):
        if self.min == None:
            minimum = f"{'-':^5}"
        else:
            minimum = f"{self.min:#5}"

        if self.max == None:
            maximum = f"{'-':^5}"
        else:
            maximum = f"{self.max:#5}"

        try:
            cal_center=f"{self.calibration.center:^5}"
        except AttributeError:
            cal_center=f"{'n/a':^5}"
        
        try:
            cal_minimum=f"{self.calibration.min:^5}"
        except AttributeError:
            cal_minimum=f"{'n/a':^5}"

        return f"{self.pname:<15}|{self.value:#5}|{minimum}|{maximum}|" \
                + f"{cal_center}|{self.calibration.deadzone:^5}|" \
                + f"{self.calibration.antideadzone:^5}|{cal_minimum}|" \
                + f"{self.calibration.max:^5}|\n"

class UIStick(UIButton):
    def __init__(self,calibration_x,calibration_y,pname="left",name="Left",x=0,y=0,r=40,text="",fcolor=7,lcolor=7,scolor=8,selected=False,callback=None):
        super().__init__(x,y,r,r,text,fcolor,scolor,scolor,0,selected,callback)

        self.name = name

        self.axis_x=Axis(calibration_x,f"{pname}x",f"{self.name} X","h")
        self.axis_y=Axis(calibration_y,f"{pname}y",f"{self.name} Y","v")

        self.delta_x = 0
        self.delta_y = 0
        self.r = r
        
        self.lcolor = lcolor # line color

        self.truncate = False
    
    def update(self):
        self.axis_x.update()
        self.axis_y.update()
        self.delta_x = 0.5 * self.r * self.axis_x.value / self.axis_x.calibration.get_range()
        self.delta_y = 0.5 * self.r * self.axis_y.value / self.axis_y.calibration.get_range()
        super().update()

    def reset_measurements(self):
        self.axis_x.reset_measurements()
        self.axis_y.reset_measurements()

    def toggle_truncate(self):
        self.truncate = not self.truncate

    def draw(self):

        if not self.visible:
            return
        
        if self._selected:
            # Red circle r+1 size
            pyxel.circ(self.x,self.y,self.r+1,self.scolor)

        fcolor = self.fcolor
        if self._pressed:
            if pyxel.frame_count - self._pressed_frame < 30:
                fcolor = self.pcolor
            else:
                self._toggle_pressed()
        
        # Detect if touching edged
        lcolor = self.lcolor
        pythagore_sum = self.delta_x * self.delta_x + self.delta_y * self.delta_y
        pythagore_hypo = math.ceil((self.r * self.r)/4)

        if pyxel.frame_count % 60 == 0:
            print(self.delta_x,self.delta_y,pythagore_sum,pythagore_hypo)
        
        if pythagore_hypo - pythagore_sum < 2:
            lcolor = 3
            fcolor = 3

        # if SDL view
        if self.truncate:
            if pythagore_sum > 0:
                ratio2 = pythagore_hypo / pythagore_sum
                if ratio2 < 1:
                    ratio = pow(ratio2,0.5)
                    self.delta_x = self.delta_x * ratio
                    self.delta_y = self.delta_y * ratio

        pyxel.circ(self.x,self.y,self.r,0)
        pyxel.circb(self.x,self.y,self.r,lcolor)
        pyxel.circ(self.x + self.delta_x,self.y + self.delta_y,self.r/2,fcolor)

        hooking_progress=max(self.axis_x.get_hooking_progress() ,self.axis_y.get_hooking_progress() )
        if hooking_progress >0:
            pyxel.circ(self.x + self.delta_x,self.y + self.delta_y,int(hooking_progress * self.r/2),self.scolor)

    def __str__(self):
        return self.axis_x.__str__() + self.axis_y.__str__()

class UIGamepad(UIPanel):
 
    def __init__(self,x=0,y=0):
        super().__init__(x,y,280,80,title="",lcolor=0,selected=-1)

        self.calibration = RPCalibration(default_trigger_max=0x755)

        self.gauge_triggerleft = UIGauge(self.calibration.trigger_left,"triggerleft","Trigger Left",self.x,self.y,fcolor=6,)          # left
        self.add_uiobject(self.gauge_triggerleft)

        self.stickleft = UIStick(self.calibration.axis_leftx,self.calibration.axis_lefty,"left","Left Stick",self.x + 80,self.y + 40, 40,fcolor=6)    # left
        self.add_uiobject(self.stickleft)

        self.stickright = UIStick(self.calibration.axis_rightx,self.calibration.axis_righty,"right","Right Stick",self.x + 200,self.y + 40, 40,fcolor=6)  # right
        self.add_uiobject(self.stickright)

        self.gauge_triggerright = UIGauge(self.calibration.trigger_right,"triggerright","Trigger Right",self.x+260,self.y,fcolor=6)     # right
        self.add_uiobject(self.gauge_triggerright)

        self.textbox_info = UITextbox(self.x + 120,self.y+60, 40, 20, 1,1,7," SDL")
        self.textbox_info.toggle_visible()

        self.add_uiobject(self.textbox_info)

        self.event_path = None
        self.find_event_path()

        self.event_format = 'llHHi'
        self.event_size = struct.calcsize(self.event_format)

        self.eventpipe = os.open(self.event_path, os.O_RDONLY | os.O_NONBLOCK)
    
    def find_event_path(self, gp_name=GAMEPAD_NAME):
        search_path = Path(INPUT_SEARCH_PATH)
        for sys_event_dir in search_path.glob("event*"):
            with open(sys_event_dir / "device" / "name", "r") as event_name_file:
                if event_name_file.readline().strip() == gp_name:
                    sys_event_dir.stem
                    self.event_path=Path(INPUT_DEV_DIR) / sys_event_dir.stem
                    break
    
    def reset_measurements_all(self):
        self.stickleft.reset_measurements()
        self.stickright.reset_measurements()
        self.gauge_triggerleft.reset_measurements()
        self.gauge_triggerright.reset_measurements()

    def backup_calibration(self):
        self.backup_calibration_data = RPCalibration()

    def restore_calibration(self):
        self.backup_calibration_data.write_parameters()
        self.calibration.load_parameters()

    def update(self):

        while True:
            try:
                event = os.read(self.eventpipe, self.event_size)
                #event = b'\x00' * 24

                (tv_sec, tv_usec, type, code, value) = struct.unpack(self.event_format, event)

                if type == 3 and  code == 0:  
                    self.stickleft.axis_x.update_value(value)

                elif type == 3 and  code == 1:
                    self.stickleft.axis_y.update_value(value)

                elif type == 3 and code == 3:
                    self.stickright.axis_x.update_value(value)

                elif type == 3 and code == 4:
                    self.stickright.axis_y.update_value(value)

                elif type == 3 and  code == 20:
                    self.gauge_triggerleft.axis.update_value(value)

                elif type == 3 and code == 21:
                    self.gauge_triggerright.axis.update_value(value)

            except OSError as e:
                break

        super().update()

    def toggle_sdl_view(self):
        self.stickleft.toggle_truncate()
        self.stickright.toggle_truncate()
        self.gauge_triggerleft.toggle_truncate()
        self.gauge_triggerright.toggle_truncate()
        self.textbox_info.toggle_visible()

    def draw(self):
        if not self.visible:
            return
        
        super().draw()

    def __str__(self):
        return f"{'':^15}|{'raw measurements':^17}|" \
                + f"{'calibration':^29}|\n" \
          + f"{'axis':^15}|{'value':^5}|{'min':^5}|{'max':^5}|" \
                + f"{'centr':^5}|{'dzone':^5}|{'adzon':^5}|{'min':^5}|{'max':^5}|\n" \
          + self.stickleft.__str__() \
          + self.stickright.__str__() \
          + self.gauge_triggerleft.__str__() \
          + self.gauge_triggerright.__str__()

class UITextbox(UIObject):
    def __init__(self, x=0, y=0, w=200, h=50, fcolor=0,lcolor=7,tcolor=7,text="Display test here\nAnotherline",minshowframe=0):
        super().__init__(x, y, w, h)
        self.fcolor = fcolor
        self.lcolor = lcolor
        self.tcolor = tcolor
        self.text = [text]
        self.minshowframe = minshowframe    # minimum number of frame to show the text
        self.lastupdateframe = pyxel.frame_count

    def settext(self, text):
        self.text.append(text)

    def update(self):
        if len(self.text) > 1 and (pyxel.frame_count - self.lastupdateframe) > self.minshowframe:
            self.lastupdateframe = pyxel.frame_count
            self.text.pop(0)

    def draw(self):
        if not self.visible:
            return
        
        pyxel.rect(self.x,self.y,self.w,self.h,self.fcolor)
        pyxel.rectb(self.x+5,self.y+5,self.w-10,self.h-10,self.lcolor)
        pyxel.text(self.x+10,self.y+10,self.text[0], self.tcolor)
