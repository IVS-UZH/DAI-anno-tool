##############################################################
# package:SafeCall.py
#
# Allow to call methods which probably don't exist without raising exception 

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



def dummycall(*args,**kwargs): pass


class SafecallError(BaseException): pass       

class safecall(object):
    __slots__ = ['__obj__']
    
    def __new__(cls, obj, raising = False):
        if raising:
            self = object.__new__(safecall_raise)
        else:
            self = object.__new__(safecall)    
        
        object.__setattr__(self, '__obj__', obj)
        
        
        return self
        
    def __getattr__(self, attr):
        return getattr(self.__obj__, attr, dummycall)
        
    # handling of special methods
    def __len__(self):
        return self.__getattr__('__len__')()

    def __getitem__(self, item):
        return self.__getattr__('__getitem__')(item)

    def __setitem__(self, item, value):
        self.__setattr__('__setitem__')(item, value)
        
    def __setattr__(self, attr, value):
        m = getattr(self.__obj__.__class__, attr, dummycall)
        if m is dummycall: return
        
        m = getattr(m, '__set__', dummycall)
        if m is dummycall: return
        
        m(self.__obj__, value)        
        
Error = SafecallError    
            
class safecall_raise(safecall):
    __slots__ = []
    
    def __getattr__(self, attr):
        m = getattr(self.__obj__, attr, dummycall)
        if m is dummycall:
            raise SafecallError()
        else:
            return m
            
    def __setattr__(self, attr, value):
        m = getattr(self.__obj__.__class__, attr, dummycall)
        if m is dummycall: raise SafecallError()
        
        m = getattr(m, '__set__', dummycall)
        if m is dummycall: raise SafecallError()
        
        m(self.__obj__, value)        
        
        
__all__ = ('safecall', 'safecall_raise', 'Error')