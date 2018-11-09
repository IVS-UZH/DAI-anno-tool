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
from Segments import *
from SafeCall import safecall
import itertools
from DependencyView import *
import Behaviors

italicFont = Drawing.Font(Drawing.Font.defaultFont.familyname, Drawing.Font.defaultFont.size, ['italic'])
boldFont = Drawing.Font(Drawing.Font.defaultFont.familyname, Drawing.Font.defaultFont.size, ['bold'])


class KeyLabel(UI.Label):
  color    = PresentationProperty(Drawing.Color, 'white')

class ValueLabel( UI.Label):
  color    = PresentationProperty(Drawing.Color, 'white')
  clickAction = Action(None)
  
  highlighted     = PresentationProperty(bool, False)
  selected        = PresentationProperty(bool, False)
  highlightable   = PresentationProperty(bool, True)
  
  @View.presentationState.changed
  def presentationState(self, context):
    color = ValueLabel.color.default
    
    # print "%s.highlighted = %s" % (self, self.highlighted)
    
    if self.selected:
      color = 'green'
    elif self.highlighted:
      color = 'dodgerblue'
      
    self.color = color
    
    UI.Label.presentationState.__changed__(self, context)
      
  # ------ event handling
  def mouseDown(self, event):
    self.clickAction()
  
  
class VariableView(UI.OverlayView):
  """ A view that displays key value lists """
  fcolor  = PresentationProperty(Drawing.Color, 'slategray')
  bcolor  = PresentationProperty(Drawing.Color, Drawing.Color('gray', alpha=0.9))
  
  # ----- layout
  performsLayout = True
  
  def computeLayout(self):
    """ Arrange the views """
    
    # we arrange the key views and the value views separately, so that they are properly aligned
    # both keys and values are aligned to the right
    padding = 0
    margin = 0
    
    
    try:
      keyAreaWidth = max(v.size.width for v in self.__keyViews) + margin
      valueAreaWidth = max(v.size.width for v in self.__valueViews) + margin
    except ValueError:
      keyAreaWidth = 0
      valueAreaWidth = 0
      
    width = keyAreaWidth + valueAreaWidth + padding
    
    # lay out the keys and values 
    y = 0
    for keyView, valueView in itertools.izip(self.__keyViews, self.__valueViews):
      h = max(keyView.size.height, valueView.size.height)
      keyView.position = (keyAreaWidth - keyView.size.width, y + (h - keyView.size.height)/2)
      valueView.position = (keyAreaWidth + padding, y + (h - valueView.size.height)/2)
      y = y + h
    
    # set the container size
    self.size = (width, y)

    
    # layout is done, trigger redraw
    self.needsLayout = False
    self.dirty()
    
  @observable_property
  def views(self):
    return itertools.chain(self.__keyViews, self.__valueViews)
  
  def addView(self, view, after = None, before = None):
    safecall(self.controller).addedSubview(view)
    
  def removeView(self, view):
    safecall(self.controller).removedSubview(view)
    
  def getValueViewForKey(self, key):
    if key is None: return None

    for view in self.__valueViews:
      if view.key == key:
        return view

    return None
    
  
  
  # ----- model update logic
  def __model_changed(self, obj, context):
    """ 
      Update the view in accordance with the changes in the model.
      Currently, I just recreate the entire thing
    """
    self.__keyViews   = []
    self.__valueViews = []
    
    for key, value in self.representedObject.variables:
      keyView = KeyLabel(value=u"%s:" % (key, ), superview = self, controller=self.controller)
      
      if value is None:
        valueView = ValueLabel(value=u"(not set)", superview = self, controller=self.controller)
      else:
        valueView = ValueLabel(value=u"%s" % (value, ), superview = self, controller=self.controller)

        
      keyView.key = key
      valueView.key = key
      
      self.__keyViews.append(keyView)
      self.__valueViews.append(valueView)
    
    self.needsLayout = True
    self.dirty()            
  
  # ----- initializer
  def __init__(self, *args, **kwargs):
    # init the state
    self.__keyViews   = []
    self.__valueViews = []
    
    # call the super constructor
    super(VariableView, self).__init__(*args, **kwargs)  
    
    # link the model
    observers(self.representedObject, 'variables').after += self.__model_changed
    
    # make sure that the data is correctly reflected
    self.__model_changed(None, None)
  
  @property
  def representedObject(self):
    return self.controller.representedObject
    
  def draw(self, rect):
    frame = Drawing.Path.initWithRoundedRect(0, 0, *self.size, roundness=0.2)
    
    if self.bcolor is not None:
      self.bcolor.makeFillcolor()
      frame.fill()
    
    if self.fcolor is not None:
      self.fcolor.makeDrawcolor()
      frame.stroke()
    
    