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
from DependencyView import *
import Behaviors

class ConstituentView(View):
  """ 
    Draws a constituency structure 
  
    Constraints: constituency structure is always over the corresponding
    tokens, but its the job of the parent view to fix this
  """
  # ----- presentation properties
  
  # the tickmark size
  tickmarkHeight = PresentationProperty(int, 15)
  
  # preferred node height (this is the vertical distance from the closest objects)
  preferredNodeDistance = 15
  
  # layout priority: how much the component wants to be close to the tokens 
  # (smaller number means higher priproty)
  layoutPriority = 100
  positionPriority = 0
  
  segments = []
  items    = []
  
  # ----- actions
  clickAction = Action(Behaviors.Actions.ViewSelected)
  
  # -- layout
  performsLayout = True
  
  def computeLayout(self):
    self.size = self.label.size
    
    self.dirty()
    self.needsLayout = False
      
  # ----- presentation properties
  segments     = PresentationProperty(list, [])
  segmentsSelected     = PresentationProperty(bool, False)
  segmentsFocused     = PresentationProperty(bool, False)
  
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

    lwidth = 3 if self.segmentsFocused else 1

    for segmentView in self.segments:
      segmentView.color = segmentColor
      segmentView.lineWidth = lwidth
    
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
    
  def __segmentClicked(self, sender):
    self.clickAction()

  # --- layout logic
  def shouldBeHigherThanNode(self, other):
    """ Returns true if this node should be displayed above the other node """
    # if we are comparing this to a dependency view, check if 
    # we need to be higher than some of its elements
    if isinstance(other, DependencyView):
      return any(self.shouldBeHigherThanNode(n) for n in other.dependentViews) 
        
    if not isinstance(other, ConstituentView): return False
    
    # this constituency node should be above the othe constituency node if
    # if partially contains the other node. However, we want this thing to be assymetrical
    # that means, that it has to be 'larger' then the other node
    this_tokens = frozenset(self.dependentViews)
    other_tokens = frozenset(other.dependentViews)
    
    # we consider X > Y if X contains more elements of Y than 
    # there are elements of Y not contained in X
    #
    # another criterium is if they intersect, we just return the larger one
    # would that be better? Yes, looks better
    # return len(this_tokens  & other_tokens) > len(other_tokens - this_tokens)
    return len(this_tokens  & other_tokens) > 0 and len(this_tokens) > len(other_tokens)
  
  @observable_property
  def dependentViews(self):
    """ Enumerate the views that correspond to the controller and target of the dependency """
    try:
      controller = self.controller.spanController
      return tuple(controller.getViewForSpanObject(token) for token in self.controller.representedObject.tokens)
    except AttributeError:
      return ()
  
  
  # --- segment setup
  @property
  def __consecutiveTokenViewSets(self):
    """
      Returns the list of sorted, consecutive tokenview groups
      That is, if there is a gap in the token list, returns the token views sorted 
      so that the gap is accounted for
    """
    groups = []
    current_group = []
    
    for view in sorted(self.dependentViews, key=lambda v: v.position.x):
      # if there are no tokens in the current group,just append it
      if len(current_group) == 0:
        current_group.append(view)
      else:
        # check if the next token is consecutive to the last one in the current group
        if view.controller.representedObject.index  == current_group[-1].controller.representedObject.index+1:
          current_group.append(view)  
        else:
          # start a new group
          groups.append(current_group)
          current_group = [view]       
    
    groups.append(current_group)
    return groups
 
  def setupSegments(self):
    """
      Creates the segments that provide visual cues for which tokens are part of 
      this constituent. The basic visuals are like this:
    
                           Label
      ----------------------------         ---------
      |                                            |
    token1            token2      nontoken        token3
    
      If a token is NOT part of a constituent, we get a gap at the corresponding place. Its ugly but easy
    """
    # the segment list
    segments = []
    
    # the height on which to put the line
    y = self.rect.y1 - 2
    
    # start building the segments
    viewGroups = self.__consecutiveTokenViewSets
    for i, viewGroup in enumerate(viewGroups):
      # get the extent of the token view set
      x0 = viewGroup[0].rect.x0
      x1 = viewGroup[-1].rect.x1
      
      # adjust the extent if this is the first or the last token view
      # also don't forget to add the vertical tick mark
      if i == 0:
        x0 = x0 + int(viewGroup[0].size.width*0.25)
        segments.append(LineSegmentView(endpoints  = ((x0, y+self.tickmarkHeight), (x0, y)), dblClickAction = Behaviors.Actions.EditableActivated, clickAction = self.__segmentClicked, masterView = self))
                          
      if i == len(viewGroups)-1:
        x1 = x1 - int(viewGroup[-1].size.width*0.25)   
        segments.append(LineSegmentView(endpoints = ((x1, y+self.tickmarkHeight), (x1, y)), dblClickAction = Behaviors.Actions.EditableActivated, clickAction = self.__segmentClicked, masterView = self))
      
      if i > 0:
        segments.append(RectDotView(center = (x0, y), dblClickAction = Behaviors.Actions.EditableActivated, clickAction = self.__segmentClicked, masterView = self))
        
      if i < len(viewGroups)-1:
        segments.append(RectDotView(center = (x1, y), dblClickAction = Behaviors.Actions.EditableActivated, clickAction = self.__segmentClicked, masterView = self))  
      
      
      segments.append(LineSegmentView(endpoints = ((x0, y), (x1, y)), dblClickAction = Behaviors.Actions.EditableActivated, clickAction = self.__segmentClicked, masterView = self))

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
    
    super(ConstituentView, self).__init__(*args, **kwargs)  

    self.addView(self.label)
    self.label.position = (0, 0)
    self.label.value = "hello"
    bindings(self.label).value = ValueBinding(self.controller.representedObject, 'mnemonic', lambda value, *args: unicode(value) if value != "" else "(not set)")


    # observe the model changes
    observers(self.controller.representedObject, 'tokens').before += self.__modelWillChange
    observers(self.controller.representedObject, 'tokens').after += self.__modelDidChange
    

    