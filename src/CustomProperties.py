##############################################################
# package:CustomProperties.py
#
# Various useful attribute descriptors:
#   - cached properties: a convenience property which manages the storage behind the scenes 

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



class cachedproperty(object):
    slots = ('fset', 'ftransform', 'key', 'default_key')
    
    def __new__(cls, fset, ftransform = None):
        self = object.__new__(cls)#, fget = None, fset = fset)

        self.fset = fset
        self.ftransform = ftransform
        self.key = '_' + fset.__name__ 
        self.default_key = 'default_' + fset.__name__ 
        
        return self
        
    def __get__(self, obj, cls = None):
        if obj is None:
            return self
        else:
            # get the value from the object's dictionary, or the default one
            try:
                return getattr(obj, self.key)
            except AttributeError:
                return getattr(obj, self.default_key, None)
                                    
    def __set__(self, obj, value):
        old_value = self.__get__(obj)
        # transform the value if needed
        if self.ftransform is not None:
            value = self.ftransform(obj, old_value, value)
        # is the new value different from the old one?
        if value != old_value:
            # then change it and notify that the change has happened
            object.__setattr__(obj, self.key, value)   
            self.fset(obj, old_value, value)    
        
    def transformer(self, ftransform):
        return cachedproperty(fset = self.fset, ftransform = ftransform)


  

__all__ = ('cachedproperty')