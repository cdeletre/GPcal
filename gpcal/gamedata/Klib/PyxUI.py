"""
    PyxUI: a very basic Pyxel User Interface library
    Author: Kdog
    Version: 0.1
    SPDX-License-Identifier: MIT
"""
import pyxel
import struct
import os
import math

from Klib.RPocket import RPCalibration


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
    def __init__(self,x=0,y=0,w=20,h=80,fcolor=7,lcolor=7,scolor=8,selected=False,callback=None):
        super().__init__(x,y,w,h,"",fcolor,scolor,scolor,0,selected,callback)

        self.lcolor = lcolor # line color
        self.truncate = False

        self.fill = 0
    
    def update(self):
        super().update()

    def update_value(self,value,range):
        self.fill = self.h * (value / range)

    def toggle_truncate(self):
        self.truncate = not self.truncate
    
    def draw(self):
        if not self.visible:
            return
        
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

class UIStick(UIButton):
    def __init__(self,x=0,y=0,r=40,fcolor=7,lcolor=7,scolor=8,selected=False,callback=None):
        super().__init__(x,y,r,r,"",fcolor,scolor,scolor,0,selected,callback)

        self.r = r
        self.lcolor = lcolor # line color
        
        self.xdelta = 0
        self.ydelta = 0
        self.truncate = False
    
    def update(self):
        super().update()

    def update_value(self,xvalue,xrange,yvalue,yrange):        
        self.xdelta = math.ceil((self.r * xvalue) / (xrange * 2))
        self.ydelta = math.ceil((self.r * yvalue) / (yrange * 2))

        

    def toggle_truncate(self):
        self.truncate = not self.truncate

    def draw(self):

        if not self.visible:
            return
        
        if self._selected:
            pyxel.circb(self.x,self.y,self.r+1,self.scolor)

        fcolor = self.fcolor
        if self._pressed:
            if pyxel.frame_count - self._pressed_frame < 30:
                color = self.pcolor
            else:
                self._toggle_pressed()
        
        lcolor = self.lcolor
        pythagore_sum = self.xdelta * self.xdelta + self.ydelta * self.ydelta
        pythagore_hypo = math.ceil((self.r * self.r) / 4)

        if pythagore_hypo - pythagore_sum < 2:
            lcolor = 3
            fcolor = 3

        if self.truncate:
            if pythagore_sum > 0:
                ratio2 = pythagore_hypo / pythagore_sum
                if ratio2 < 1:
                    ratio = pow(ratio2,0.5)
                    self.xdelta = self.xdelta * ratio
                    self.ydelta = self.ydelta * ratio

        pyxel.circb(self.x,self.y,self.r,lcolor)
        pyxel.circ(self.x + self.xdelta,self.y + self.ydelta,self.r/2,fcolor)

class UIGamepad(UIPanel):
 
    def __init__(self,x=0,y=0):
        super().__init__(x,y,280,80,title="",lcolor=0,selected=-1)

        self.gauge_triggerleft = UIGauge(self.x,self.y,fcolor=6)          # left
        self.add_uiobject(self.gauge_triggerleft)
        self.stickleft = UIStick(self.x + 80,self.y + 40, 40,fcolor=6)    # left
        self.add_uiobject(self.stickleft)
        self.stickright = UIStick(self.x + 200,self.y + 40, 40,fcolor=6)  # right
        self.add_uiobject(self.stickright)
        self.gauge_triggerright = UIGauge(self.x+260,self.y,fcolor=6)     # right
        self.add_uiobject(self.gauge_triggerright)
        self.textbox_info = UITextbox(self.x + 120,self.y+60, 40, 20, 1,1,7," SDL")
        self.textbox_info.toggle_visible()
        self.add_uiobject(self.textbox_info)

        self.event_format = 'llHHi'
        self.event_size = struct.calcsize(self.event_format)

        self.eventpipe = os.open("/dev/input/event4", os.O_RDONLY | os.O_NONBLOCK)

        self.calibration = RPCalibration(default_trigger_max=0x755)

        self.leftx = 0
        self.leftx_min = 0
        self.leftx_max = 0

        self.lefty = 0
        self.lefty_min = 0
        self.lefty_max = 0

        self.rightx = 0
        self.rightx_min = 0
        self.rightx_max = 0

        self.righty = 0
        self.righty_min = 0
        self.righty_max = 0

        self.triggerright = 0
        self.triggerright_min = 1000
        self.triggerright_max = 0
        self.triggerright_touched = 0

        self.triggerleft = 0
        self.triggerleft_min = 1000
        self.triggerleft_max = 0
        self.triggerleft_touched = 0

    def reset_measurements_all(self):
        self.reset_measurements_stickleft()
        self.reset_measurements_stickright()
        self.reset_measurements_triggerleft()
        self.reset_measurements_triggerright()

    def reset_measurements_stickleft(self):
        self.leftx_max = 0
        self.leftx_min = 0
        self.lefty_max = 0
        self.lefty_min = 0

    def reset_measurements_stickright(self):
        self.rightx_max = 0
        self.rightx_min = 0
        self.righty_max = 0
        self.righty_min = 0

    def reset_measurements_triggerleft(self):
        self.triggerleft_max = 0
        self.triggerleft_min = 1000
        self.triggerleft_touched = False

    def reset_measurements_triggerright(self):
        self.triggerright_max = 0
        self.triggerright_min = 1000
        self.triggerright_touched = False

    def backup_calibration(self):
        self.backup_calibration_data = RPCalibration()

    def restore_calibration(self):
        self.backup_calibration_data.apply_parameters()
        self.calibration=self.backup_calibration_data

    def update(self):

        while True:
            try:
                event = os.read(self.eventpipe, self.event_size)
                #event = b'\x00' * 24

                (tv_sec, tv_usec, type, code, value) = struct.unpack(self.event_format, event)

                if type == 3 and  code == 0:  
                    self.leftx = value
                    self.leftx_min = min(self.leftx_min, value)
                    self.leftx_max = max(self.leftx_max, value)


                elif type == 3 and  code == 1:
                    self.lefty = value
                    self.lefty_min = min(self.lefty_min, value)
                    self.lefty_max = max(self.lefty_max, value)

                elif type == 3 and code == 3:
                    self.rightx = value
                    self.rightx_min = min(self.rightx_min, value)
                    self.rightx_max = max(self.rightx_max, value)

                elif type == 3 and code == 4:
                    self.righty = value
                    self.righty_min = min(self.righty_min, value)
                    self.righty_max = max(self.righty_max, value)

                elif type == 3 and  code == 20:
                    if value != self.triggerleft:
                        self.triggerleft_touched = True
                    self.triggerleft = value

                    if self.triggerleft_touched:
                        self.triggerleft_min = min(self.triggerleft_min, value)
                        self.triggerleft_max = max(self.triggerleft_max, value)

                elif type == 3 and code == 21:
                    if value != self.triggerright:
                        self.triggerright_touched = True
                    self.triggerright = value

                    if self.triggerright_touched:
                        self.triggerright_min = min(self.triggerright_min, value)
                        self.triggerright_max = max(self.triggerright_max, value)

            except OSError as e:
                break

        self.stickleft.update_value(self.leftx,self.calibration.axis_leftx_max-self.calibration.axis_leftx_antideadzone,self.lefty,self.calibration.axis_lefty_max-self.calibration.axis_lefty_antideadzone)
        self.stickright.update_value(self.rightx,self.calibration.axis_rightx_max-self.calibration.axis_rightx_antideadzone,self.righty,self.calibration.axis_righty_max-self.calibration.axis_righty_antideadzone)
        self.gauge_triggerleft.update_value(self.triggerleft,self.calibration.trigger_left_max-self.calibration.trigger_left_antideadzone)
        self.gauge_triggerright.update_value(self.triggerright,self.calibration.trigger_right_max-self.calibration.trigger_right_antideadzone)

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
