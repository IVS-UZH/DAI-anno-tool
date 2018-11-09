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
from VariableView import *
from collections import namedtuple
from StrEditor import *


__all__ = ['TokenView']



class TokenTranscriptionView(UI.Editors.EditorView):
  """ An editor view that represents a single token in the corpus. If double-clicked, becomes editable """      
  @property
  def canBecomeFirstResponder(self):
    return True
    
  @property
  def showingPlaceholder(self):
    return False
  
  def becameFirstResponder(self):
    self.fstyle = 'rounded'
    super(TokenTranscriptionView, self).becameFirstResponder()
       
  def yieldedFirstResponder(self):
    self.fstyle = 'none'
    super(TokenTranscriptionView, self).yieldedFirstResponder()
    
    
  # --- actions      
  dblClickAction    = Action(Behaviors.Actions.EditableActivated)
  # shiftClickAction  = Action('shiftClickToken')
  
  def mouseDown(self, event):
    if event.numClicks >= 2:
      self.dblClickAction()
    else:
      View.mouseDown(self, event)

  
   

  


class TokenView(View):
  """ 
    Represents a token. 
  
    A token consists of a token transcription and an 
    optional set of other items, such as reference label
    annotation etc.
  """
  # ----- actions
  clickAction = Action(Behaviors.Actions.ViewSelected)
  
  # ----- presentation properties  
  highlighted     = PresentationProperty(bool, False)
  selected        = PresentationProperty(bool, False)
    
  @View.presentationState.changed
  def presentationState(self, context):
    """ Adjust the apperiance to the state """
    # check if a parent node is currently highlighted
    if self.selected:
      color = PresentationSettings.selectedColor
    elif self.highlighted:
      color = PresentationSettings.highlightedColor 
    else:
      color = Drawing.Color('black')
      
    self.transcriptionLabel.color = color
    self.secondaryLabel.color = color
          
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
  
  # ----- subviews and layout
  performsLayout = True
  
  def computeLayout(self):
    """ Arrange the views """
    # the total width
    width = max(v.size.width for v in self.views)
    
    # arrange the views
    self.transcriptionLabel.position = (0, 0) #((width - self.transcriptionLabel.size.width)/2, 0)
    self.secondaryLabel.position = (0, self.transcriptionLabel.rect.y1)  #((width - self.mnemonicsLabel.size.width)/2, self.transcriptionLabel.rect.y1)
      
    # set the size of the box
    self.size = (max(v.rect.x1 for v in self.views), max(v.rect.y1 for v in self.views))
    
    # layout is done, trigger redraw
    self.dirty()
    self.needsLayout = False
    
  @observable_property
  def views(self):
    yield self.transcriptionLabel
    yield self.secondaryLabel
    

  @observable_property
  def showsGloss(self):
    return self.__showsGloss
    
  @showsGloss.setter
  def showsGloss(self, value):
    self.secondaryLabel.superview = None
    self.secondaryLabel = None
  
        
    self.__showsGloss = value  

    if value:
      self.secondaryLabel = StrEditor(margins=(15, 0, 0, 0), minWidth=100, fstyle='none', targetVariable='gloss', placeholderValue='(no lemma)')
      self.secondaryLabel.superview = self
      self.secondaryLabel.controller = self.controller
      bindings(self.secondaryLabel).value = ValueBinding(self.controller.representedObject, 'gloss', lambda value, *args: unicode(value))
    else:
      self.secondaryLabel  = UI.Label(margins=(15, 0, 0, 0), font = italicFont)
      self.secondaryLabel.superview = self
      bindings(self.secondaryLabel).value = ValueBinding(self.controller.representedObject, 'mnemonic', lambda value, *args: unicode(value))
      
    
    self.needsLayout = True
    self.dirty()
    
  # ----- initializer
  def __init__(self, *args, **kwargs):
    # create the subviews
    self.transcriptionLabel = TokenTranscriptionView(margins=(15, 0, 0, 0), fstyle='none', minWidth=20)
    self.secondaryLabel     = UI.Label(margins=(15, 0, 0, 0), font = italicFont)

    # call the super constructor
    super(TokenView, self).__init__(*args, **kwargs)  

    self.__showsGloss = False

    self.transcriptionLabel.superview = self
    self.transcriptionLabel.controller = self.controller
    self.secondaryLabel.superview = self

    # link the labels to the token data
    assert(self.controller is not None)
    bindings(self.transcriptionLabel).value = ValueBinding(self.controller.representedObject, 'transcription', lambda value, *args: unicode(value))
    bindings(self.secondaryLabel).value = ValueBinding(self.controller.representedObject, 'mnemonic', lambda value, *args: unicode(value))
    
    self.needsLayout = True

 
    