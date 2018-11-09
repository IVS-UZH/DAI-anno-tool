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

class StrEditor(UI.Editors.EditorView):
  
  def becameFirstResponder(self):
    self.fstyle = 'rounded'
    super(StrEditor, self).becameFirstResponder()
       
  def yieldedFirstResponder(self):
    self.fstyle = 'none'
    super(StrEditor, self).yieldedFirstResponder()
  
  # --- actions      
  dblClickAction    = Action(Behaviors.Actions.EditableActivated)
  clickAction       = Action()
  # shiftClickAction  = Action('shiftClickToken')
  
  def mouseDown(self, event):
    if event.numClicks >= 2:
      self.dblClickAction()
    else:
      self.clickAction()
  