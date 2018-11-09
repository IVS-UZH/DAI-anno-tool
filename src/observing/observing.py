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



from weakcall import WeakKey, weakcallable
from operator import itemgetter
from collections import namedtuple
import weakref

# ====================================================================================================================
#
# Support for reference anchoring (this creates a GC dependency so that weak references survive longer)
#
# ====================================================================================================================
__anchors = {}
def __remove_anchor(where):
  if __anchors is not None:
    del __anchors[where]  

def anchor(what, where):
  """
    Used to anchor an object to an instance (the object is guarantied not be garbage collected while the anchor is alive). 
    Intended usage is to keep week references alive even though the object is not explicitely retained (e.g. on-the-fly generated
    utility objects, validator functions and the like)
    
    
    ## Example 
    def generate_weak_callback(self):
      def callback():
        self.notify()
      
      anchor(callback, self)

      # callback will not be immediately collected when function returns!        
      return weakref.ref(callback) 
  """    
  l = __anchors.get(where)
  if l is None:
    l = __anchors[WeakKey(where, __remove_anchor)] = []
  #print 'anchoring', what, 'to', where  
  l.append(what)

def abstract(method):
  def m(*args, **kwargs):
    raise NotImplemented('Method %s is abstract and should be implemented in the descendant' % method.__name__)
  
  m.__name__ = method.__name__
  
  return m  
  
# ====================================================================================================================
#
# Observer lists
#
# ====================================================================================================================
class Observers(object):
  """
    A collection of observers
  """    
  
  
  __slots__ = ('__wrefs',)
  
  
  def __init__(self, *observers):
    self.__wrefs = [weakcallable(observer, self.__wref_collected) for observer in observers]
    
  def __wref_collected(self, wref):
    self.__wrefs.remove(wref)  
    
  def append(self, observer): 
    self.__wrefs.append(weakcallable(observer, self.__wref_collected))

    return self
    
  __iadd__ = append
      
  def remove(self, observer): 
    wrefs = self.__wrefs
    for i in xrange(len(wrefs)):
      if wrefs[i]() is observer:
        del wrefs[i]
        break
        
    return self 
    
  __isub__ = remove
  
  
  def __iter__(self):
    # we want to iterate over a copy, because weak references could get dropped during observer execution
    for wref in list(self.__wrefs):
      observer = wref()
      if observer is not None:
        yield observer        
  
  def __nonzero__(self): return len(self.__wrefs) != 0
  
  def clear(self):
    del self.__wrefs[:]
    
  def __repr__(self): return 'observers %s' % (tuple(r for r in self),)  
  
  
class BeforeAfterObservers(object):
  """
    A collection of observers. Consists of two lists - before and after.
  """    
  __slots__ = ('__before', '__after')
  
  def __init__(self):
    self.__before = Observers()
    self.__after = Observers()
        
  @property
  def before(self):
    """ Access to the beforeChange observer collection """
    return self.__before
  
  @before.setter
  def before(self, value):
    if value is not self.__before: raise ValueError('Cannot assign to the internal observer list')
  
  @property
  def after(self): 
    """ Access to the afterChange observer collection """
    return self.__after
  
  @after.setter
  def after(self, value):
    if value is not self.__after: raise ValueError('Cannot assign to the internal observer list')
    
  def remove(self, observer): 
    """ Removes the observer from the collection """
    self.__before -= observer
    self.__after -= observer

  def clear(self): 
    """ Removes all observers from the collection """
    self.__before.clear()
    self.__after.clear()
    
  def __repr__(self):
    return 'observers(before change: %s, after change: %s)' % (self.__before, self.__after)
      
  def __nonzero__(self): return (bool(self.__before) or bool(self.__after))   
  
# ====================================================================================================================
#
# Value binding
#
# ====================================================================================================================

class ValueBinding(tuple):
  def __new__(cls, obj, key, transformer):  
    return tuple.__new__(cls, (obj, key, transformer))
      
  obj = property(itemgetter(0))
  key = property(itemgetter(1))
  transformer = property(itemgetter(2))
  
  def get_transformed_value(self, target, targetKey):
    # retrieve the value from the object
    value = getattr(self[0], self[1])
    
    # apply the transformer, if nessesary
    transformer = self[2]
    if transformer is not None:
      value = transformer(value)
    
    return value  
 
    
# ====================================================================================================================
#
# Observer and binding storage
#
# We use global dictionaries to store the obeserver lists. Key is the observable object. This allows
# us to enumerate the bindings and observers if nessesary
#
# ====================================================================================================================
__observers = {}
__bindings  = {}


def __remove_obj_wref(wref):
  if __observers is not None:
    __observers.pop(wref, None)
  if __bindings is not None:
    __bindings.pop(wref, None)
    
__empty__observer_list = namedtuple("EmptyObserverList", "before,after")((), ()) 

def __get_observers_for_obj_and_observable(obj, observable, create = False):
  # get the observer table for the instance
  observers_for_obj = __observers.get(obj, None)
  # create the observer table if nessesary
  if observers_for_obj is None:
    # guard agains unnessesary creation
    if not create:
      return __empty__observer_list
    # create the table
    observers_for_obj = __observers[WeakKey(obj, __remove_obj_wref)] = {}
  # get the observer list for the observable
  observer_list = observers_for_obj.get(observable, None)
  # create the observer list if nessesary
  if observer_list is None:
    # guard agains unnessesary creation
    if not create:
      return __empty__observer_list
    # create the table
    observer_list = observers_for_obj[observable] = BeforeAfterObservers()
  
  return observer_list    
  
  
def __get_bindings_for_obj(obj, create = False):
  # get the binding table for the instance
  bindings_for_obj = __bindings.get(obj, None)
  if bindings_for_obj is None:
    # guard agains unnessesary creation
    if not create:
      return {}
    # create the table
    bindings_for_obj = __bindings[WeakKey(obj, __remove_obj_wref)] = {}
  
  return bindings_for_obj
  
  
def _install_binding_observer(target, target_key, binding):  
  # ensure that target it weakly referenced
  target = weakref.ref(target)
  
  def binding_observer(source, context = None):
    _target = target()
    # check if the target and the binding still exist
    if _target is None or __bindings.get(target(), {}).get(target_key, None) is not binding:
        # does not exist, uninstall the binding
        #print "Removing the observer for %s because the target dissapeared or the binding has been removed" % (binding,)
        observers(binding.obj, binding.key).after -= binding_observer
        return
    
    # the binding still exists, get the new value
    value = binding.get_transformed_value(_target, target_key)
    
    # if the value has changed, propagate the changes to the 
    if value != getattr(_target, target_key):
      setattr(_target, target_key, value)

  # anchor the binding observer at the source
  anchor(binding_observer, binding.obj)
  
  # install the observer
  observers(binding.obj, binding.key).after += binding_observer
  

# ====================================================================================================================
#
# Observing interface
#
#
#  === Custom data model ============================================================================================= 
#
# Objects can define custom hooks to implement key observing. Doing so overrides obserable properties: DO NOT MIX AND
# MATCH UNLESS YOU KNOW WHAT YOU ARE DOING
#  
#  The following methods must always be defined together (its an error to only define some of them )
#  __key_is_observable__(key)    - return True if the key is observable
#  __get_observers_for_key__(key)  - return an observer list for the key
#
#  The following properties are optional:
#  __observers__          - an observer interface (that can be used to enumerate keys etc.)
#  __observable_keys__      - a tuple of observable keys for the object
# ==================================================================================================================== 
class NoObservableException(Exception):
  def __init__(self, obj, key):
    if key is None:
      super(Exception, self).__init__("Object %s is not observable" % (obj, ))
    else:
      super(Exception, self).__init__("Object %s does not have an observable key %s" % (obj, key))
    
    self.obj = obj
    self.key = key
    
def observers(obj, key = None):
  """
    Returns a mutable observer list for the given object and key
    
    TODO: observable objects are not yet supported
    
    Rules: 
    
    A. If no key is given:
      1. If the object defines __get_observers__(), use it (this is a global observer interface)
      2. TODO: create my own observer interface that enumerates observable attributes
      3. Raise an error
    B. If a key is given:
      1. If the key is an observable attibute, use it
      2. If the object has an observable attribute 'key', use it
      3. If the object defines __get_observers_for_key__(), use it
      3. Raise an error
  """
  # A. No key is given:
  if key is None:      
    # case 1. Object defines __get_observers__ interface
    if hasattr(obj, '__observers__'):
      return obj.__observers__   

    # return an observer proxy
    return ObjectObserversList(obj)     
  # B. A key is given
  else:
    # case 1. key is an observable attribute
    if(isinstance(key, ObservableAttribute)):
      return __get_observers_for_obj_and_observable(obj, key, create = True)

    # case 2: object has an observable attribute key
    attr = getattr(obj.__class__, key, None)
    #print "Asked for observers(%s).%s, got %s" % (obj, key, attr)
    
    if attr is not None and isinstance(attr, ObservableAttribute):
      return __get_observers_for_obj_and_observable(obj, attr, create = True)
    
    # case 3 object defines __get_observers_for_key__ interface
    if hasattr(obj, '__key_is_observable__') and obj.__key_is_observable__(key):
      return obj.__get_observers_for_key__(key)
  
  
  # if we are here, no observer could be found, so we raise an error
  raise NoObservableException(obj, key)
  
      
class ObjectObserversList(object):
  """
    A proxy object used to access observable properties of an object
  """        
  def __init__(self, obj):
    self.__obj = obj
      
  def __iter__(self):
    """
      Iterate through the observable keys
    """
    obj = self.__obj
    
    # if the object defines a custom observable interface, use that
    if hasattr(obj, '__observable_keys__'):
      return iter(obj.__observable_keys__)
        
    # else, iterate through all the observable attributes
    def iterateobservables():
      for key, attr in obj.__class__.__dict__.iteritems():
        if isinstance(attr, ObservableAttribute):
          yield key
    return iterateobservables()
  
  def __getitem__(self, key):
    return observers(self.__obj, key)
  
  __getattr__ = __getitem__

def willChange(obj, key, context):
  """
    Starts a change on an observable item specified by object and key

    Rules:

    1. Invoke __changing__ on the observable attribute of the object
    2. Invoke __key_changing__ hook on the object
    2. Raise an error
  """
  # if the object defines a no observer notification interface, stop
  if hasattr(obj, '__no_observer_notifications'): return
  
  # case 1. Object has an observable attribute with the key
  attr = getattr(obj.__class__, key, None)
  #print "Asked for observers(%s).%s, got %s" % (obj, key, attr)
  if attr is not None and isinstance(attr, ObservableAttribute):
    return attr.__changing__(obj, context)

  # case 2. Object defines the __key_changing__ interface
  if hasattr(obj, '__key_changing__'):
   return obj.__key_changing__(key, context)

  # if we are here, no observer could be found, so we raise an error
  raise NoObservableException(obj, key)
#
#
def didChange(obj, key, context):
  """
    Ends a change on an observable item specified by object and key

    Rules:

    1. Invoke __changed__ on the observable attribute of the object
    2. Invoke __key_changed__ hook on the object
    2. Raise an error
  """
  if hasattr(obj, '__no_observer_notifications'): return
  
  # case 1. Object has an observable attribute with the key
  attr = getattr(obj.__class__, key, None)
  if attr is not None and isinstance(attr, ObservableAttribute):
    return attr.__changed__(obj, context)

  # case 2. Object defines the __key_changing__ interface
  if hasattr(obj, '__key_changing__'):
   return obj.__key_changed__(key, context)

  # if we are here, no observer could be found, so we raise an error
  raise NoObservableException(obj, key)
  
class ChangeContextManager(object):  
  slots = ['obj', 'key']
        
  def __init__(self, obj, key, context = ()):
    self.obj = obj
    self.key = key
    self.context = ObservingContext(context)
    
  def __enter__(self): 
    willChange(self.obj, self.key, self.context)
        
  def __exit__(self, exc_type, exc_val, exc_tb):
    if exc_type is not None: return 
    didChange(self.obj, self.key, self.context)  

                
def changing(obj, key, context= ()):
  return  ChangeContextManager(obj, key, context)      
  
  
def disableObserving(obj):
  obj.__no_observer_notifications = True

def enableObserving(obj):
  try: del obj.__no_observer_notifications 
  except: pass

  
  
# ====================================================================================================================
#
# Bindings interface. Bindings create strong references to the target object.
#
#
#  === Custom data model ============================================================================================= 
#
#  
#
# ==================================================================================================================== 
def bindings(obj):
  return BindingList(obj, __get_bindings_for_obj(obj, True))
  
  
class BindingList(object):
  __slots__ = ('__obj', '__binding_table')
  
  def __init__(self, obj, binding_table):
    super(BindingList, self).__setattr__('_BindingList__obj', obj)
    super(BindingList, self).__setattr__('_BindingList__binding_table', binding_table)

    
    # super(MyTest, self).__setattr__('__obj', value)
    # self.__obj = obj
    # self.__binding_table = binding_table
    
  def __can_bind_key(self, key):
    return True
    # obj = self.__obj
    #
    # # case 1: key is an observable attribute
    # attr = getattr(obj.__class__, key, None)
    # if attr is not None and isinstance(attr, ObservableAttribute):
    #   return True
    #
    # # case 3 object defines __get_observers_for_key__ interface
    # if hasattr(obj, '__key_is_observable__'):
    #    return obj.__key_is_observable__(key):
    #
    # return False
    
  def __setitem__(self, key, binding):
    if not isinstance(binding, ValueBinding):
      raise ValueError('Binding specification must be a ValueBinding')
      
    if not self.__can_bind_key(key):
      raise ValueError("Key '%s' is not bindable" % key)
      
    # install the binding
    self.__binding_table[key] = binding
    _install_binding_observer(self.__obj, key, binding)
    
    # make sure that the values are identical
    value = binding.get_transformed_value(self.__obj, key)
    if value != getattr(self.__obj, key):
      setattr(self.__obj, key, value)
    
    
  __setattr__ = __setitem__
    
  def __getitem__(self, key):
    return self.__binding_table.get(key, None)

  __getattr__ = __getitem__

  def __delitem__(self, key):
    self.__binding_table.pop(key, None)
    
  def clear(self):
    self.__binding_table.clear()
    
  
  
# ====================================================================================================================
#
# Observable attributes
#
# ====================================================================================================================
class ObservableAttribute(object):
  """
    An observable attribute interface
  """
  def __changing__(self, obj, context): 
    for o in observers(obj, self).before:
      o(obj, context)      

  def __changed__(self, obj, context): 
    for o in observers(obj, self).after:
      o(obj, context)      

class ObservableProperty(ObservableAttribute):  
  __slots__ = ('fget', 'fset', 'fchanging', 'fchanged', 'ftransform') 
        
  def __init__(self, fget, fset = None, fchanging = None, fchanged = None, ftransform = None):
    # set basic functions
    self.fget = fget
    self.fset = fset
    self.fchanged = fchanged
    self.fchanging = fchanging
    self.ftransform = ftransform
    
  # --------- property building properties
  def getter(self, method):
    return self.__class__(fget = method, fset = self.fset, fchanging = self.fchanging, fchanged = self.fchanged, ftransform=self.ftransform)

  def setter(self, method):
    return self.__class__(fget = self.fget, fset = method, fchanging = self.fchanging, fchanged = self.fchanged, ftransform=self.ftransform)

  def changing(self, method):
    return self.__class__(fget = self.fget, fset = self.fset, fchanging = method, fchanged = self.fchanged, ftransform=self.ftransform)
  
  def changed(self, method):
    return self.__class__(fget = self.fget, fset = self.fset, fchanging = self.fchanging, fchanged = method, ftransform=self.ftransform)

  def transform(self, method):
    return self.__class__(fget = self.fget, fset = self.fset, fchanging = self.fchanging, fchanged = self.fchanged, ftransform=method)
    
    
  # --------- managing changes and notifications    
  def __changing__(self, obj, context): 
    if hasattr(obj, '__no_observer_notifications'): return
    # if self.fset is not None:
    #   raise ValueError('Use the setter to change this property!')
            
    # notify the observers that a change will be happening
    for o in observers(obj, self).before:
      o(obj, context)      

    # invoke the start change function (if any)      
    if self.fchanging is not None:
      self.fchanging(obj, context)     

  def __changed__(self, obj, context): 
    if hasattr(obj, '__no_observer_notifications'): return
    # invoke the end change function (if any)    
    if self.fchanged is not None:
      self.fchanged(obj, context)        
    
    # notify the observers that a change has happened
    for o in observers(obj, self).after:
      o(obj, context)      
  
  def __get__(self, obj, owner = None):
    if obj is None:
      return self
    else:
      return self.fget(obj)
      
      
  def __set__(self, obj, value):
    old_value = self.fget(obj)
    
    # transform the value, if needed
    if self.ftransform is not None:
      value = self.ftransform(obj, value)
    
    # silently ignore same assigment as it is semantically empty
    # helps with reflectory binding
    if old_value is value:
      return 
      
    if self.fset is None:
      raise AttributeError('Cannot assign a read-only attribute!')
      
    # create the change context
    context = ObservingContext(old = old_value, new = value)

    self.__changing__(obj, context)
    self.fset(obj, value)
    self.__changed__(obj, context)
    
    # # get the observers
    # prop_observers = observers(obj, self)
    #
    # # notify the observers that a change will be happening
    # for o in prop_observers.before:
    #   o(obj, context)
    #
    # # invoke the start change function (if any)
    # if self.fchanging is not None:
    #   self.fchanging(obj, context)
    #
    # self.fset(obj, value)
    #
    # # invoke the end change function (if any)
    # if self.fchanged is not None:
    #   self.fchanged(obj, context)
    #
    # # notify the observers that a change has happened
    # for o in prop_observers.after:
    #   o(obj, context)

observable_property = ObservableProperty
    
class ObservableState(ObservableAttribute):
  __slots__ = ('fchanging', 'fchanged') 
        
  def __init__(self, fchanged = None,  fchanging = None):
    # set basic functions
    self.fchanged = fchanged
    self.fchanging = fchanging
    
  # --------- property building properties
  def changing(self, method):
    return ObservableState(fchanging = method, fchanged = self.fchanged)
  
  def changed(self, method):
    return ObservableState(fchanging = self.fchanging, fchanged = method)
  
  
  # --------- Descriptor interface      
  def __get__(self, obj, owner = None):
    if obj is None:
      return self
    else:
      raise TypeError("Cannot set or get state attributes, please use the observing API instead")
      
      
  def __set__(self, obj, value):
    raise TypeError("Cannot set or get state attributes, please use the observing API instead")
    
  
  # --------- managing changes and notifications    
  def __changing__(self, obj, context): 
    # notify the observers that a change will be happening
    for o in observers(obj, self).before:
      o(obj, context)      

    # invoke the start change function (if any)      
    if self.fchanging is not None:
      self.fchanging(obj, context)     

  def __changed__(self, obj, context): 
    # invoke the end change function (if any)    
    if self.fchanged is not None:
      self.fchanged(obj, context)        
    
    # notify the observers that a change has happened
    for o in observers(obj, self).after:
      o(obj, context)      
      
state = ObservableState
    
    
def observable(attribute):
  if isinstance(attribute, property):
    v = ObservableProperty(attribute.fget, attribute.fset)
  else:
    raise ValueError('I don\'t know how to make %s observable' % attribute)
  
  return v
  

def changes(key):
  """
    Signal data dependencies. Usage:

    @changing(key)           -- declare method as such that changes a string key on its instance
    @changing(attribute)       -- declare method as such that changes an observable attribute on its instance
  """
  if isinstance(key, basestring):
    return __changes_wrapper_key(key) # TODO
  elif isinstance(key, ObservableAttribute):
    return __changes_wrapper_attribute(key)
  else:
    raise ValueError()    
    
class __changes_wrapper_key(object):  
  slots = ['key']
  
  def __init__(self, attribute):
    self.key = key
      
  def __call__(self, method_or_property):
    attribute = self.attribute
    
    if isinstance(method_or_property, property):
      # decorate a property
      old_fset = method_or_property.fset
      
      def fset(obj, value):
        willChange(obj, self.key, ObservingContext())
        old_fset(obj, value)
        didChange(obj, self.key, ObservingContext())
      
      return property(fget = method_or_property.fget, fset = fset, fdel = method_or_property.fdel)
    else:    
      # decorate a method
      def _(obj, *args, **kwargs):
        willChange(obj, self.key, ObservingContext())
        v = method_or_property(obj, *args, **kwargs)
        didChange(obj, self.key, ObservingContext())   
        return v
      
      _.__name__ = method_or_property.__name__
      return _                    
                  
class __changes_wrapper_attribute(object):  
  slots = ['attribute']
  
  def __init__(self, attribute):
    self.attribute = attribute
      
  def __call__(self, method_or_property):
    attribute = self.attribute
    
    if isinstance(method_or_property, property):
      # decorate a property
      old_fset = method_or_property.fset
      
      def fset(obj, value):
        attribute.__changing__(obj, ObservingContext())
        old_fset(obj, value)
        attribute.__changed__(obj, ObservingContext())   
      
      return property(fget = method_or_property.fget, fset = fset, fdel = method_or_property.fdel)
    else:    
      # decorate a method
      def _(obj, *args, **kwargs):
        attribute.__changing__(obj, ObservingContext())
        v = method_or_property(obj, *args, **kwargs)
        attribute.__changed__(obj, ObservingContext())   
        return v
      
      _.__name__ = method_or_property.__name__
      return _ 
    
    
# ====================================================================================================================
#
# Observing context: a helper dictionary wrapper that simplifies development
#
# ====================================================================================================================
class ObservingContext(dict):    
  def __setattr__(self, name, value):
    self[name] = value
  
  def __getattr__(self, name):
    return self.get(name, None)
  
  def __getitem__(self, key):
    return self.get(key, None)      
  

# ====================================================================================================================
#
# Testing
#
# ====================================================================================================================
if __name__ == '__main__':
  class T1(object):
    @observable
    @property
    def x(self):
      try:
        return self.__x
      except:
        return 0
    
    @x.setter
    def x(self, value):
      self.__x = value
      
    @x.changed
    def x(self, context = None): 
      print context  
  
  def observer(obj, context = None):
    print obj, 'has changed from', context['old'], 'to', context['new']

  def validator(obj, context = None):
    if context['new'] > context['old']:
      raise ValueError()      

      
  t = T1()
  t2 = T1()
  
  #observers(t, 'x').after += observer
  #observers(t, 'x').before += validator
  
  #print observers(t, 'x')
  
  # for k in __observers[t]:
  #   print dir(k)
  #
  # print t.x
  # t.x = 8
  # print t.x
  
  t1 = T1()
  
  t.x=5
  
  #print('-----------')
  bindings(t1).x = ValueBinding(t, 'x', None)
  
  print t1.x
    
  t.x  = 44
  print t1.x

  #bindings(t1).clear()
    
  t.x = 33
  
  print t1.x
  
  bindings(t1).x = ValueBinding(t2, 'x', None)
  
  print t1.x
  
  t.x = 33
  
  print t1.x
  
  
  
    
