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



from operator import itemgetter
from UIToolkit import Application
from weakref import WeakKeyDictionary
from observing import weakcallable
from SafeCall import safecall

class action(tuple):
  """
    Specifies the method to be called the the action is executed.
    This is either a (weak) callable or a string specifying a
    method to look up in the responser chain. The method signature is
    always method(sender)
  """
  __slots__ = ()

  def __new__(cls, target):
    if target is None:
      return None
    elif isinstance(target, action):
      return action(target[0])
    elif callable(target):
      target = weakcallable(target)
    elif not isinstance(target, basestring):
      raise TypeError('Action must be a string or a callable')

    return tuple.__new__(cls, (target,))  
    
  def canBeInvoked(self):
    return self.__as_call__() is not None
      
  def getCurrentTarget(self):
    call = self.__as_call__()
    obj  = getattr(call, '__self__', None)
    
    return obj
      
  def __repr__(self):
    return "action(%s)" % self[0]
    
  def __as_call__(self):
    if isinstance(self[0], basestring):
      responder = Application().firstResponder.findResponderForAction(self[0])      
      call = getattr(responder, self[0], None)
    else:
      # resolve the weak reference
      call = self[0]()

    return call
    
  def __call__(self, sender, *args, **kwargs):
    call = self.__as_call__()
    
    if call:
      call(sender, *args, **kwargs)  
      
class noaction(action):
  def __new__(cls):
    return tuple.__new__(cls, (None,))
  
  def __as_call__(self):
    return None
    
  @property
  def action(self):
    return _noaction  
  
  @property
  def hasResponder(self):
    return False   
    
  def __repr__(self):
    return "action(none)"
  
  
_noaction = noaction()  
  
class boundaction(tuple):
  """
    An action that is called to a specific sender
  """
  def __new__(cls, action, sender):
    return tuple.__new__(cls, (action, sender))  
     
  action = property(itemgetter(0))
  sender = property(itemgetter(1))
  
  def __call__(self, *args, **kwargs):
    self.action(self.sender, *args, **kwargs)
    
  def canBeInvoked(self):
    return self.action.canBeInvoked()

  def getCurrentTarget(self):
    return self.action.getCurrentTarget()

    
class Action(object):
  """
    An attribute that stores an action. Can specify a default action
  """
  def __init__(self, default = None):
    self.__default = action(default)
    self.__action_storage = WeakKeyDictionary()

  def __get__(self, instance, cls = None):
    a = self.__action_storage.get(instance, self.__default)
    if a is None:
      return boundaction(_noaction, instance)
    else:
      return boundaction(a, instance)

  def __set__(self, instance, value):
    # setting action to None is the same as deleting it
    if value is None:
      self.__del__(instance)
      return 
    
    if not isinstance(value, action):
      value = action(value)
    self.__action_storage[instance] = value

  def __del__(self, instance):
    return self.__action_storage.pop(instance, _noaction)