# encoding: utf-8

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


from UIToolkit import *
from observing import *
from SafeCall import safecall
import Behaviors

class SegmentView(View):
  @observable_property
  def masterView(self):
    try:
      return self.__masterView
    except:
      return None
  
  @masterView.setter
  def masterView(self, value):
    self.__masterView = value
    
  @property
  def controller(self):
    try:
      return self.masterView.controller
    except:
      return None
    
  
      


class RectDotView(SegmentView):
  """
    Draws a rectangular notch
  """
  color         = PresentationProperty(Drawing.Color, 'black')
  side          = PresentationProperty(int, 6)
  
  # --------  line geometry  
  @observable_property
  def center(self):
    return self.rect.center
  
  @center.setter
  def center (self, (x, y)):
    self.rect = Rect(int(x-self.side/2), int(y-self.side/2), int(x+self.side/2), int(y+self.side/2)) 
  
  
  # --------  drawing
  def draw(self, rect): 
    path = Drawing.Path.initWithRect(0, 0, *self.rect.size)
    self.color.makeDrawcolor()
    self.color.makeFillcolor()
    path.fillAndStroke()
    
  # --------- event handling
  def mouseEnteredArea(self, event):
    Behaviors.Actions.ViewHoweved(getattr(self.controller, 'view', None))

  def mouseLeftArea(self, event):
    Behaviors.Actions.ViewHoweved(None)


class LineSegmentView(SegmentView):
  """
    A segmentview draws a single line, possibly with an arrow. Lines are either horizontal or
    vertical.
  """
  color         = PresentationProperty(Drawing.Color, 'black')
  lineWidth     = PresentationProperty(int, 1)
  drawsArrow    = PresentationProperty(bool, False)
  
  boundingBoxOffset = 5
  
  # --------  actions
  clickAction = Action(None)
  dblClickAction = Action(None)
  
  # --------  line geometry  
  @observable_property
  def orientation(self):
    return getattr(self, '_orientation', 'horizontal')

  @observable_property
  def direction(self):
     lineGoesToMaxCoord = getattr(self, '_lineGoesToMaxCoord', True)
     
     if self.orientation == 'horizontal' and lineGoesToMaxCoord:
       return 'right'
     elif self.orientation == 'horizontal' and not lineGoesToMaxCoord:
       return 'left'
     elif self.orientation == 'vertical' and not lineGoesToMaxCoord:
       return 'up'
     elif self.orientation == 'vertical' and lineGoesToMaxCoord:
       return 'down'
       
     raise RuntimeError("Invalid segment state")
      
  
  @observable_property
  def endpoints(self):
    x0, y0, x1, y1 = self.rect
        
    if self.direction == 'up':
      return ((x0+self.boundingBoxOffset, y0), (x0+self.boundingBoxOffset, y1))
    elif self.direction == 'down':
      return ((x0+self.boundingBoxOffset, y1), (x0+self.boundingBoxOffset, y0))
    elif self.direction == 'right':
      return ((x0, y0 + self.boundingBoxOffset), (x1, y0 +self.boundingBoxOffset))
    elif self.direction == 'left':
      return ((x1, y0 + self.boundingBoxOffset), (x0, y0 + self.boundingBoxOffset))
      
    raise RuntimeError("Invalid segment state")
      
  @endpoints.setter
  def endpoints(self, ((x0, y0), (x1, y1))):
    """ Sets new endpoints, derives the line state and rets the rect """
    if x0 == x1:
      # set the state
      self._orientation = 'vertical'
      self._lineGoesToMaxCoord = (y1 > y0)
      
      # compute the new rect
      # we have a vertical line that has x0 at its center
      self.rect = Rect(x0-self.boundingBoxOffset, min(y0, y1), x0+self.boundingBoxOffset, max(y0, y1))
    elif y0 == y1:
      # set the state
      self._orientation = 'horizontal'
      self._lineGoesToMaxCoord = (x1 > x0)
      
      # compute the new rect
      # we have a horizontal line that has x0 at its center
      self.rect = Rect(min(x0, x1), y0-self.boundingBoxOffset, max(x0, x1), y0+self.boundingBoxOffset)
    else:
      raise ValueError("Segment must be horizontal or vertical!")
      
      
  # --------  drawing
  def draw(self, rect): 
    path = Drawing.Path()
    
    if self.orientation == 'horizontal':
      path.moveTo(0, self.boundingBoxOffset)
      path.lineTo(self.size.width, self.boundingBoxOffset)
    elif self.orientation == 'vertical':
      path.moveTo(self.boundingBoxOffset, 0)
      path.lineTo(self.boundingBoxOffset, self.size.height)
    else:
      raise ValueError("Segment must be horizontal or vertical!")
      
    # draw the path
    path.thickness = self.lineWidth
    self.color.makeDrawcolor()   

    path.stroke()    
        
    # draw the arrow if required
    if not self.drawsArrow: return
    
    path = Drawing.Path()
    path.thickness = self.lineWidth
    
    if self.direction == 'left':
      path.moveTo(self.boundingBoxOffset, 0)
      path.lineTo(0, self.boundingBoxOffset)
      path.lineTo(self.boundingBoxOffset, self.size.height)
    elif self.direction == 'right':
      path.moveTo(self.size.width - self.boundingBoxOffset, 0)
      path.lineTo(self.size.width, self.boundingBoxOffset)
      path.lineTo(self.size.width - self.boundingBoxOffset, self.size.height)
    elif self.direction == 'up':
      path.moveTo(0, self.boundingBoxOffset)
      path.lineTo(self.boundingBoxOffset, 0)
      path.lineTo(self.size.width, self.boundingBoxOffset)
    elif self.direction == 'down':
      path.moveTo(0, self.size.height - self.boundingBoxOffset)
      path.lineTo(self.boundingBoxOffset, self.size.height)
      path.lineTo(self.size.width, self.size.height - self.boundingBoxOffset)
    else:
      raise ValueError("Segment must be horizontal or vertical!")
    
    self.color.makeDrawcolor()   
    self.color.makeFillcolor()   
    path.fillAndStroke()
    
    
  # ------ event handling
  def mouseDown(self, event):
    if event.numClicks >= 2:
      self.dblClickAction()
    else:
      self.clickAction()
  
  

      
  
  


    
    