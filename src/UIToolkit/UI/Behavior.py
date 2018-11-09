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



from UIToolkit import Action, View
# This module defines a numer of standard behaviors for views

__all__ = ('ClickableView', 'HoverableView')

class ClickableView(View):
  click = Action('viewClicked')
  
  def mouseDown(self, event):
    self.click()
    
class HoverableView(View):
  enter = Action('viewEntered')
  leave = Action('viewLeft')
  
  def mouseEnteredArea(self, event):
    if event.view is self:
      self.enter()
    else:
      super(HoverableView, self).mouseEnteredArea(event)

  def mouseLeftArea(self, event):
    if event.view is self:
      self.left()
    else:
      super(HoverableView, self).mouseLeftArea(event)
