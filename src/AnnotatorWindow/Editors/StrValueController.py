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
from AnnotatorWindow.Views import *
import logging
from UIToolkit.UI.Editors import EditorOperationError, StrEditController

class StrValueEditController(StrEditController):
  def __init__(self, editor, target, prop):
    super(StrValueEditController, self).__init__(editor)
    self.target = target
    self.prop = prop
    
  def keyEvent(self, event):
    if event.key in ('enter', 'return'):
      transaction = self.target.__db__.transaction()
      with transaction:
        setattr(self.target, self.prop, self.value)
      transaction.commit()
      self.editor.window.firstResponder = None
      return True
    elif event.key in ('esc', ):
      self.editor.window.firstResponder = None
      return True  
  