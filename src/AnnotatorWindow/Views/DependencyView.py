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
import Behaviors
from AnnotatorWindow import PresentationSettings

class DependencyView(View):
  """ 
    Draws a dependency structure   
  """
  
  # ----- layout properties
    
  # the distance from the subnode and the line
  lineDistance = 5
  
  # preferred node height (this is the vertical distance from the closest objects)
  preferredNodeDistance = 50
  
  # layout priority: how much the component wants to be close to the tokens 
  # (smaller number means higher priproty)
  layoutPriority = 0
  positionPriority = 1

  
  # ----- actions
  clickAction = Action(Behaviors.Actions.ViewSelected)  
  
  # -- layout
  performsLayout = True
  
  def computeLayout(self):
    self.size = self.label.size
    
    self.dirty()
    self.needsLayout = False
    
  @observable_property
  def dependentViews(self):
    """ Enumerate the views that correspond to the controller and target of the dependency """
    try:
      controller = self.controller.spanController
      view1 = controller.getViewForSpanObject(self.controller.representedObject.controller)
      view2 = controller.getViewForSpanObject(self.controller.representedObject.target)
      return (view1, view2)
      # if view1.position.x < view2.position.x:
      #   return (view1, view2)
      # else:
      #   return (view2, view1)
    except AttributeError:
      return ()
      
  # ----- presentation properties
  segments             = PresentationProperty(list, [])
  segmentsSelected     = PresentationProperty(bool, False)
  segmentsFocused      = PresentationProperty(bool, False)
  
  highlighted     = PresentationProperty(bool, False)
  selected        = PresentationProperty(bool, False)
  

  @View.presentationState.changed
  def presentationState(self, context):
    """ Adjust the apperiance to the state """
    if self.selected:
      self.label.color = PresentationSettings.selectedColor
      segmentColor = PresentationSettings.selectedColor
    elif self.highlighted:
      self.label.color = PresentationSettings.highlightedColor
      segmentColor = PresentationSettings.highlightedColor
    else:
      self.label.color = Drawing.Color('black')
      segmentColor = Drawing.Color('black')
      
    if self.segmentsSelected:
      segmentColor = PresentationSettings.selectedColor
      
    for segmentView in self.segments:
      segmentView.color = segmentColor
      if self.controller.editor is not None and self.controller.editor.member == getattr(segmentView, 'tag', None):
        segmentView.lineWidth = 3 
      else:
        segmentView.lineWidth = 1
    
    self.dirty()
    
    
  @property 
  def highlightable(self):
    try:
      return self.window.firstResponder.dispatchCall('viewCanBeHighlighted', self)
    except:
      return True
      
  @property 
  def selectable(self):
    try:
      return self.window.firstResponder.dispatchCall('viewCanBeSelected', self)
    except:
      return True
  
  
  # ------ event handling
  def mouseDown(self, event):
    self.clickAction()
  
  
  # --- layout logic
  def shouldBeHigherThanNode(self, other):
    """ Returns true if this node should be displayed above the other node """
    #if not isinstance(other, ConstituencyView): return False
    
    # a dependency node should be over a node if it is part of its targets
    # or some of its items needs to be higher than this node
    return other in self.dependentViews
    
  
  # --- segment setup
  def setupSegments(self):
    """
      Creates the segments that provide visual cues for which nodes are part of 
      this dependency relation. The basic visuals are like this:
    
                           
      -----------------  Label --------------- 
      |                                       |
    controller                             target
    
      If a token is NOT part of a constituent, we get a gap at the corresponding place. Its ugly but easy
    """
    # the segment list
    segments = []
    
    
    # Case 1: target = controller
    if self.dependentViews[0] == self.dependentViews[1]:
      # we want to draw a single line straight down to the item
      view = self.dependentViews[0]
      x0 = view.rect.center.x
      y0 = view.position.y - self.lineDistance
      x1 = self.rect.center.x
      y1 = self.rect.y1

      segments.append(LineSegmentView(endpoints  = ((x0, y0), (x0, y1)), dblClickAction = Behaviors.Actions.EditableActivated, tag='target', masterView = self))
    # we want to draw the node label above the segment  
    elif abs(self.dependentViews[0].rect.center.x - self.dependentViews[1].rect.center.x) <= self.size.width+15:      
      x0 = self.dependentViews[0].rect.center.x
      y0 = self.dependentViews[0].position.y - self.lineDistance
      x1 = self.dependentViews[1].rect.center.x
      y1 = self.dependentViews[1].position.y - self.lineDistance
      y  = self.rect.y1
      
      
      segments.append(LineSegmentView(endpoints  = ((x0, y0), (x0, y)), dblClickAction = Behaviors.Actions.EditableActivated, tag='controller', masterView = self))  
      segments.append(LineSegmentView(endpoints  = ((x0, y), (x1, y)), masterView=self))
      segments.append(LineSegmentView(endpoints  = ((x1, y), (x1, y1)), drawsArrow=True, dblClickAction = Behaviors.Actions.EditableActivated, tag='target', masterView = self))          
    # we want to draw the label inline  
    else:
      x0 = self.dependentViews[0].rect.center.x
      y0 = self.dependentViews[0].position.y - self.lineDistance
      x1 = self.dependentViews[1].rect.center.x
      y1 = self.dependentViews[1].position.y - self.lineDistance
      y  = self.rect.center.y
      x_start = self.rect.x0
      x_end = self.rect.x1
      
      segments.append(LineSegmentView(endpoints  = ((x0, y0), (x0, y)), dblClickAction = Behaviors.Actions.EditableActivated, tag='controller', masterView = self))  
      if x0 < x1:
        segments.append(LineSegmentView(endpoints  = ((x0, y), (x_start, y)), masterView=self))
        segments.append(LineSegmentView(endpoints  = ((x_end, y), (x1, y)), masterView=self))
      else:
        segments.append(LineSegmentView(endpoints  = ((x1, y), (x_start, y)), masterView=self))
        segments.append(LineSegmentView(endpoints  = ((x_end, y), (x0, y)), masterView=self))
        
      segments.append(LineSegmentView(endpoints  = ((x1, y), (x1, y1)), drawsArrow=True, dblClickAction = Behaviors.Actions.EditableActivated, tag='target', masterView = self))          
                      
    self.segments = segments
    
  # ------- model
  def __modelWillChange(self, obj, context):
      willChange(self, 'dependentViews', {})

  
  def __modelDidChange(self, obj, context):
      didChange(self, 'dependentViews', {})
    
  # ----- initializer
  def __init__(self, *args, **kwargs):
    # call the super constructor
    self.label = UI.Label(color='black')
    
    super(DependencyView, self).__init__(*args, **kwargs)  
    
    # setup the label
    bindings(self.label).value = ValueBinding(self.controller.representedObject, 'mnemonic', lambda value, *args: unicode(value) if value != "" else "(not set)")
    self.label.position = (0, 0)
    self.addView(self.label)
    
    # observe the model changes
    observers(self.controller.representedObject, 'controller').before += self.__modelWillChange
    observers(self.controller.representedObject, 'controller').after += self.__modelDidChange
    observers(self.controller.representedObject, 'target').before += self.__modelWillChange
    observers(self.controller.representedObject, 'target').after += self.__modelDidChange
    

    
    
    
    

    