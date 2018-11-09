# Copyright 2018 Taras Zakharko (taras.zakharko)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.



from UIToolkit import View, PresentationProperty, PresentationStateDelegate, Action
from UIToolkit.Drawing import *
from UIToolkit.Animation import Animator
from collections import namedtuple


__all__ = ('Button', )


class ButtonPresentationState(PresentationStateDelegate):
  color  = PresentationProperty(Color, 'black')
  bcolor = PresentationProperty(Color, Color(0.8, 0.8, 0.8))
  fcolor = PresentationProperty(Color, 'black')
  
  def __init__(self, *args, **kwargs):
    super(ButtonPresentationState, self).__init__(*args, **kwargs)
    self.animator = Animator(self, duration=0.15, repeat=2, swap_on_repeat = True, reset_value= True)
  
  def animateClick(self):
    # ignore if an animation is ongoing
    if self.animator.running:
      return
        
    self.animator.reset()
    self.animator.color = 'white'
    self.animator.bcolor = 'blue'
    
    
  
class Button(View):
  # --- initialisation
  def __init__(self, **kwargs):    
    if 'size' not in kwargs:
      font = Font.defaultFont
      kwargs['size'] = (font.getWidthForString(self.value) + 20, font.ascent + font.descent + 10)
      
    self.__presentationDelegate = ButtonPresentationState(self)
    
    super(Button, self).__init__(**kwargs)
    
  
  # --- presentation
  value    = PresentationProperty(unicode, 'Button')
    
  # ++++++++++++++++++ drawing +++++++++++++++++   
  def draw(self, rect): 
    super(Button, self).draw(rect)
    w, h = self.size
    font = Font.defaultFont
    value = self.value
    
    color = self.__presentationDelegate.color
    bcolor = self.__presentationDelegate.bcolor
    fcolor = self.__presentationDelegate.fcolor

    # compute the text position
    x = (w - font.getWidthForString(value))/2
    y = (h - font.descent + font.ascent)/2
    
    fcolor.makeDrawcolor()
    bcolor.makeFillcolor()
    path = Path.initWithRoundedRect(0, 0, *self.size, roundness=0.3)
    path.thickness = 1
    path.fillAndStroke()
    
    font.makeCurrent()
    color.makeDrawcolor()   
    Context.drawTextAtPosition(value, Point(x, y))    
    
  # ++++++++++++++++++ clicks +++++++++++++++++   
  action = Action()
  
  def mouseDown(self, event):
    self.__presentationDelegate.animateClick()
    self.action()
