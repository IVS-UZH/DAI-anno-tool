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


from observing import *
from UIToolkit.Drawing import *
from UIToolkit import View, PresentationProperty, Action, PresentationStateDelegate, Tasklet
from collections import namedtuple
from UIToolkit.Animation import Animator
from SafeCall import safecall
#from itertools import chain

__all__ = ('SimpleLayoutContainer','LineLayoutContainer')

def NamedTupleWithInterpolation(name, fields):
  tupleClass = namedtuple(name, fields)
  
  def __interpolate__(A, B, t):
     return tupleClass._make(a*(1-t) + b*t for a, b in zip(A, B))
     
  tupleClass.__interpolate__ = __interpolate__
  
  return  tupleClass  
  
class SimpleLayoutContainer(View):
  """ An auto-resizing container that arranges the items within """
  
  # ----  presentation attributes  
  margins = PresentationProperty(NamedTupleWithInterpolation('Margins', ('left', 'right', 'top', 'bottom'))._make, (5, 5, 5, 5), triggersLayout = True)
  fcolor  = PresentationProperty(Color, None)
  bcolor  = PresentationProperty(Color, 'white')
  # one of rect, rounded, none
  fstyle  = PresentationProperty(str, 'rect') 
  layout  = PresentationProperty(str, 'vertical', triggersLayout = True)
  spacing = PresentationProperty(int, 0, triggersLayout = True)
  
  
  # ----  layout computation
  performsLayout = True
  
  def computeLayout(self):
    """ Arrange the subviews """
    vertical_layout = self.layout == 'vertical'
    
    # the x and y to put items on
    x = self.margins.left
    y = self.margins.top
    w = 0
    h = 0
    spacing = self.spacing
    
    for view in self.views:
      view.position = (x, y)
      
      if vertical_layout:
        h = y = view.rect.y1 + spacing
        w = max(w, view.rect.x1)
      else:
        w = x = view.rect.x1 + spacing
        h = max(h, view.rect.y1)
        
    self.size = (w+self.margins.right, y+self.margins.bottom)
    
    self.dirty()
    self.needsLayout = False
    
  def draw(self, rect): 
    super(SimpleLayoutContainer, self).draw(rect)

    # make the frame
    if self.fstyle == 'rounded':
      frame = Path.initWithRoundedRect(0, 0, *self.size, roundness=0.2)
    else:
      frame = Path.initWithRect(0, 0, *self.size)
    
    # empty the background
    if self.bcolor is not None:
      self.bcolor.makeFillcolor()
      frame.fill()
    
    if self.fcolor is not None:
      self.fcolor.makeDrawcolor()
      frame.stroke()    
  
    
class LineLayoutContainer(View):
  """ An auto-resizing container that arranges the items within """
  
  # ----  presentation attributes  
  margins = PresentationProperty(NamedTupleWithInterpolation('Margins', ('left', 'right', 'top', 'bottom'))._make, (5, 30, 5, 5), triggersLayout = True)
  fcolor  = PresentationProperty(Color, 'black')
  bcolor  = PresentationProperty(Color, 'white')
  # one of rect, rounded, none
  fstyle  = PresentationProperty(str, 'rect') 
  wspacing = PresentationProperty(int, 0, triggersLayout = True)
  hspacing = PresentationProperty(int, 0, triggersLayout = True)
  textWidth = PresentationProperty(int, 640, triggersLayout = True)
  
  
  # ----  layout computation
  performsLayout = True
  
  def computeLayout(self):
    """ Arrange the subviews """
    # list of lists, stores the object order
    viewLines = [[]]
    
    # the x and y to put items on
    x = self.margins.left
    y = self.margins.top
    # the width the line should break at
    targetWidth = self.textWidth
    # the total width and height of the container
    w = 0
    h = 0
    # spacing to separate items from each other
    wspacing = self.wspacing
    hspacing = self.hspacing
    
    for view in self.views:
      # position the view and add it to te current line
      view.position = (x, y)
      viewLines[-1].append(view)
      
      # adjust the x layout parameters
      x = view.rect.x1 + wspacing
      w = max(w, view.rect.x1)
      h = max(h, view.rect.y1)
      
      
      # change the line if needed
      if x >= targetWidth:
        x = self.margins.left
        # set the y coordinate to the lowest point of the previous line
        y = h + hspacing
        # add a new view line
        viewLines.append([])
      
    self.size = (w+self.margins.right, h+self.margins.bottom)
    self.viewLines = viewLines
    
    self.dirty()
    self.needsLayout = False
    
  def draw(self, rect): 
    super(LineLayoutContainer, self).draw(rect)

    # make the frame
    if self.fstyle == 'rounded':
      frame = Path.initWithRoundedRect(0, 0, *self.size, roundness=0.2)
    else:
      frame = Path.initWithRect(0, 0, *self.size)
    
    # empty the background
    if self.bcolor is not None:
      self.bcolor.makeFillcolor()
      frame.fill()
    
    if self.fcolor is not None:
      self.fcolor.makeDrawcolor()
      frame.stroke()      
  