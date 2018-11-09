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
from collections import namedtuple
from itertools import chain as ichain


# ------ event properties (mapping tuple positions to names and managing optional values)
propDecl          = namedtuple('propDecl', ('name'))
optionalPropDecl  = namedtuple('optionalPropDecl', ('name', 'defaultValue'))


class eventproperty(property):
  def __init__(self, decl, tuple_index):
    property.__init__(self, itemgetter(tuple_index))
    self.__name__ = decl.name
    if isinstance(decl, optionalPropDecl):
      self.defaultValue = decl.defaultValue

  def extract(self, dictionary):
    try:
      if hasattr(self, 'defaultValue'):
        return dictionary.get(self.__name__, self.defaultValue)
      else:
        return dictionary[self.__name__]
    except KeyError:
      raise KeyError('Missing obligatory event property %s' % self.__name__)

# ------ event typology root
class Event(tuple):
  def __new__(cls):
    raise ValueError('Cannot instantiate abstract class %s' % cls.__name__)
  
  __properties__ = ()
  # __properties__ = ('globalMousePos',)
  #
  # globalMousePos = eventproperty(optionalPropDecl('globalMousePos', (-1, -1)), 0)
  
  def __repr__(self):
    # get the path of the event in the typology
    bases = self.__class__.mro()
    bases = bases[0:(bases.index(Event)+1)]
    bases.reverse()
    path = '.'.join(base.__name__ for base in bases)
        
    values = ', '.join("%s = %s" % (k,repr(self[i])) for i, k in enumerate(self.__properties__))
    return "%s(%s)" % (path, values)
    
  def dict(self):
    return {k:self[i] for i, k in enumerate(self.__properties__)}
  
  def eventReplacing(self, **kwargs):
    values = self.dict()
    values.update(kwargs)
    return self.__class__(**values)

# ------ factory functions for declaring events      
def construct_event_class(eventClassName, eventSuper, isAbstract, *propertyDecls):
  # eventSuper should inherit from Event
  assert issubclass(eventSuper, Event)
  
  # process the property declarations
  properties = [eventproperty(decl, i) for i, decl in enumerate(propertyDecls)]
  
  # class template
  class eventClass(eventSuper):
    # build the constructor
    if isAbstract:
      __new__ = Event.__new__
    else:
      def __new__(cls, **kwargs):
        # construct the tuple containing property values
        values =  tuple(getattr(cls, prop_name).extract(kwargs) for prop_name in cls.__properties__)
        return tuple.__new__(cls, values)
        
    # property names
    __properties__ = tuple(ichain(eventSuper.__properties__, (p.__name__ for p in properties)))
  # --- end class template
    
  # add the property declarations
  for p in properties:
    setattr(eventClass, p.__name__, p)
  
  # install the class in the event typology
  eventClass.__name__ = eventClassName
  setattr(eventSuper, eventClassName, eventClass)
  
  return eventClass
  


#----- key events
construct_event_class('Key', Event, True, 
  propDecl('key'), 
  optionalPropDecl('unicodePoint', None), 
  optionalPropDecl('modifierKeys', frozenset())
)

construct_event_class('Down', Event.Key, False)
construct_event_class('Up', Event.Key, False) 

#----- mouse events
construct_event_class('Mouse', Event, True, 
  propDecl('position'), 
  optionalPropDecl('numClicks', None), 
  optionalPropDecl('modifierKeys', frozenset())
)
construct_event_class('Down', Event.Mouse, False)
construct_event_class('Up', Event.Mouse, False) 
construct_event_class('RightDown', Event.Mouse, False)
construct_event_class('RightUp', Event.Mouse, False) 

#----- Area trigger events
construct_event_class('Area', Event, True,
   propDecl('rect'), 
   optionalPropDecl('view', None), 
)

construct_event_class('Entered', Event.Area, False)
construct_event_class('Left', Event.Area, False)



