# -*- coding: utf-8 -*-

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


"""
  file: weakcall.py

  This module implements weak callable support (such as weak references to bound methods)
"""
from weakref import ref


# ====================================================================================================================
#
# Support for weak keys in dictionaries (this is faster and more flexible then the WeakKeyDictionary)
#
# ====================================================================================================================
class WeakKey(ref):
    """
        Weak key support for dictionaries
    """
    # def __init__(self, obj, callback = None):
    #     super(WeakKey, self).__init__(obj, callback)
        
    def __eq__(self, other):
        return (self is other) or (self() is other and other is not None)
        
        
        
# ====================================================================================================================
#
# Weak bound method
#
# ====================================================================================================================
class weakboundmethod(ref):
    def __new__(cls, obj, func, callback = None):
        self = ref.__new__(cls, obj, callback)
        self.__func__ = func
        
        return self
        
    def __init__(self, obj, func, callback = None):
        pass
        
    @property
    def __self__(self):
        return ref.__call__(self)

    def __call__(self):
        obj = ref.__call__(self)
        return self.__func__.__get__(obj) if obj is not None else None
            
    def __nonzero__(self): return  (ref.__call__(self) is not None)
    
    def __eq__(self, other):
        try:
            if self is other:
                return True
                
            obj1 = ref.__call__(self)
            obj2 = ref.__call__(other)
            
            return (obj1 is not None) and (obj1 is obj2) and (self.__func__ is other.__func__)
        except:
            return False    
            
    def __repr__(self): 
        obj = ref.__call__(self)
        if obj is None:
            return '<weak bound method at 0x%x; dead>' % id(self)
        else:
            return '<weak bound method at 0x%x; of \'%s\'.%s>' % (id(self), object.__repr__(obj), self.__func__.__name__)    
            
# ====================================================================================================================
#
# Weak callable support
#
# ====================================================================================================================

def weakcallable(f, callback = None):
    try:
        instance = f.__self__
        # this is a bound method, so we anchor it at the instance
        # python should automatically do it, if we must be honest
        return weakboundmethod(instance, f.__func__, callback)
    except AttributeError:
        return ref(f, callback)    
          


    
