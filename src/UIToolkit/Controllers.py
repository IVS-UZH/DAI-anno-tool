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



from UIToolkit import Responder

__all__ = ('ViewController', 'WindowController', 'ApplicationController')


class ViewController(Responder):  
  """ Base for view controllers """
  # --- view
  @property
  def view(self):
    try:
      return self.__view
    except AttributeError:
      return None
     
  @view.setter 
  def view(self, view):
    self.__view = view
    if view.controller is not self:
      view.controller = self
  
  # ----- responding
  @property
  def nextResponder(self):
    if self.view is None:
      return None
    else:
      return self.view.superview
      

class WindowController(Responder):  
  """ Base for window controllers """
  # ----- responding
  @property
  def nextResponder(self):
    from UIToolkit import Application
    
    return Application().controller
  
  
class ApplicationController(Responder):
  # ----- responding
  @property
  def nextResponder(self):
    return None
    
  
      
    
# Do we want to go a proper object controller route at this point? Probably not so much... 
# Its too heavy machinery for what I want to achieve
# I think i will rather do it manually and rely on binding and stuff 