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
from SafeCall import safecall
from observing import *

import Actions

# class Hoverable(object):
#   def mouseEnteredArea(self, event):
#     Actions.ViewHoweved(self)
#
#   def mouseLeftArea(self, event):
#     Actions.ViewHoweved(None)
#
#
# class Selectable(View):
#   @observable_property
#   def selected(self):
#     return getattr(self, '__selected', False)
#
#   @selected.setter
#   def selected(self, value):
#     assert((self.selectable and value) or not value)
#
#     print "%s.selected=%s" % (self, value)
#
#     willChange(self, 'presentationState', {})
#     setattr(self, '__selected', value)
#     didChange(self, 'presentationState', {})
#
#
#
#     #selectionHandlingController = self.findControllerForMethod("viewWillBeSelected")
#       #
#     # if value and selectionHandlingController is not None:
#     #   selectionHandlingController.viewWillBeSelected(self)
#     #
#     # willChange(self, 'presentationState', {})
#     # setattr(self, '__selected', value)
#     # didChange(self, 'presentationState', {})
#     #
#     # if value and selectionHandlingController is not None:
#     #   selectionHandlingController.viewWasSelected(self)
#
#
#   @selected.transform
#   def selected(self, value):
#     return value and self.selectable
#
#   @observable_property
#   def selectable(self):
#     result = safecall(self.findControllerForMethod("viewCanBeSelected")).viewCanBeSelected(self)
#
#     if result is None:
#       return True
#     else:
#       return result
#
#
# class Highlightable(View):
#   @observable_property
#   def highlighted(self):
#     return getattr(self, '__highlighted', False)
#
#   @highlighted.setter
#   def highlighted(self, value):
#     assert((self.highlightable and value) or not value)
#
#     willChange(self, 'presentationState', {})
#     setattr(self, '__highlighted', value)
#     didChange(self, 'presentationState', {})
#
#   @highlighted.transform
#   def highlighted(self, value):
#     return value and self.highlightable
#
#   @observable_property
#   def highlightable(self):
#     result = safecall(self.findControllerForMethod("viewCanBeHighlighted")).viewCanBeHighlighted(self)
#
#     if result is None:
#       return True
#     else:
#       return result