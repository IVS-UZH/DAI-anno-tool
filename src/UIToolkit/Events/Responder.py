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



from SafeCall import safecall


class Responder(object):
  """
    A base for objects that respond to actions
  """
  # -----  default functionality
  def respondsToAction(self, action):
    return callable(getattr(self, action, None))
    
  def findResponderForAction(self, action):
    for responder in self.responderChain:
      if responder.respondsToAction(action):
        return responder
        
    return None
    
    
  def findMethodImplementation(self, method):
    responder = self.findResponderForAction(method)
    return getattr(responder, method, None)
    
    
  def dispatchCall(self, method, *args, **kwargs):
    call = self.findMethodImplementation(method)
    if call is None:
      raise AttributeError()
    else:
      return call(*args, **kwargs)  
                  
  @property
  def responderChain(self):
    responder = self
    
    while responder is not None:
      yield responder
      responder = getattr(responder, 'nextResponder', None)
      
    # yield self
  #
  #   # yield from the next responder's chain if it exists
  #   next_responder = self.nextResponder
  #   if next_responder is None:
  #     return
  #
  #   for responder in next_responder.responderChain:
  #     yield responder
  
  #---------- first responder protocol -------------
  @property
  def canBecomeFirstResponder(self):
    return False
  
  def becameFirstResponder(self):
    pass
    
  def yieldedFirstResponder(self):
    pass
  
  # ----- key event handling
  def keyDown(self, event):
    safecall(self.nextResponder).keyDown(event)

  def keyUp(self, event):
    safecall(self.nextResponder).keyUp(event)

  
  
                    
  # -----  needs to be overriden
  @property
  def nextResponder(self):
    return None
    
  # ------ menu validation interface - can be overriden to customize behavior
  def getStateForMenuItem(self, menu_item):
    """
      Given a menu action that this responder responds to,
      returns one of
        - True (menu enabled)
        - False (menu disabled)
        - 1 (menu item checked)
      Used to customize menu appearance
    """
    return True  
  
    