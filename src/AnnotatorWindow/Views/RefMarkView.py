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
labelFont = Drawing.Font(Drawing.Font.defaultFont.familyname, int(Drawing.Font.defaultFont.size*0.8), ['italic'])
selectedLabelFont = Drawing.Font(Drawing.Font.defaultFont.familyname, int(Drawing.Font.defaultFont.size*1), ['bold'])

class RefMarkView(UI.OverlayView, UI.Label):
  clickAction = Action(None)
  dblClickAction = Action(Behaviors.Actions.EditableActivated)
  
  font         = PresentationProperty(Drawing.Font.makeFont, labelFont)
  margins      = UI.Label.margins.override((5, 5, 5, 5))
  highlighted  = PresentationProperty(bool, False)
  selected  = PresentationProperty(bool, False)
  
  
  
  @View.presentationState.changed
  def presentationState(self, context):  
    if self.selected:
      self.color = 'green'
      self.font = selectedLabelFont  
    elif self.highlighted:
      self.color = 'dodgerblue'
      self.font = RefMarkView.font.default
    else:
      self.color = RefMarkView.color.default
      self.font = RefMarkView.font.default
    
    UI.Label.presentationState.__changed__(self, context)
    UI.OverlayView.presentationState.__changed__(self, context)
    
    
  @property 
  def highlightable(self):
    try:
      return self.window.firstResponder.dispatchCall('viewCanBeHighlighted', self)
    except:
      return True
      
      
  # ------ event handling
  def mouseDown(self, event):
    if event.numClicks >= 2:
      self.dblClickAction()
    else:
      self.clickAction()
