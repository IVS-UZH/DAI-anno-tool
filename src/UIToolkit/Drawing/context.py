import UIToolkit

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



##############################################################
# context.py
#
# Defines the graphics context API

##############################################################
# The high-level context metaclass
#
# platform-specific context implementations must use this to ensure their integration in the framework 
class ContextMetaclass(type):
    __active = None
    
    @property
    def activeContext(cls): return ContextMetaclass.__active
    
    @property
    def activeContextNotNone(cls):
        instance = ContextMetaclass.__active
        if instance is None:
            raise ValueError('This operation requires an active graphics context!')          
        return instance
    

    def __new__(metaclass, name, bases, dct):
        # ensure that context can become active
        def __enter__(context):
            if ContextMetaclass.__active  is not None:
                raise ValueError('A graphics context is already active')
            
            ContextMetaclass.__active = context
                    
        def __exit__(context, exc_type, exc_val, exc_tb):
            if ContextMetaclass.__active is not context:
                raise ValueError('This context is not active')
        
            ContextMetaclass.__active = None
            
        
        dct['__enter__'] = __enter__
        dct['__exit__'] = __exit__
        
        cls = type.__new__(metaclass, name, bases, dct)
        
        return cls
     
    # the implementations must define these attributes!
        
    # ++++++++++++++++++ colors +++++++++++++++++    
    @property
    def color(cls): return cls.activeContextNotNone.color
    
    @color.setter
    def color(cls, color): cls.activeContextNotNone.color = color
    
    @property
    def fillcolor(cls): return cls.activeContextNotNone.fillcolor
    
    @fillcolor.setter
    def fillcolor(cls, color): cls.activeContextNotNone.fillcolor = color
    
    # ++++++++++++++++++ font state +++++++++++++++++    
    @property
    def font(cls): return cls.activeContextNotNone.font

    @font.setter
    def font(cls, val): cls.activeContextNotNone.font = val
    
    # ++++++++++++++++++ transformation +++++++++++++++++    
    @property
    def transform(cls): return cls.activeContextNotNone.transform
    
    @transform.setter
    def transform(cls, point): cls.activeContextNotNone.transform = point
    
    
    # ++++++++++++++++++ path drawing +++++++++++++++++    
    def strokePath(cls, path, origin): cls.activeContextNotNone.strokePath(path, origin)
    def fillPath(cls, path, origin): cls.activeContextNotNone.fillPath(path, origin)
    def fillAndStrokePath(cls, path, origin): cls.activeContextNotNone.fillAndStrokePath(path, origin)
    

    # ++++++++++++++++++ text output +++++++++++++++++    
    def drawTextAtPosition(cls, text, point): cls.activeContextNotNone.drawTextAtPosition(text, point)
    
    

    
##############################################################
# A dummy class, its only purpose is to access the current context class
# 
# The actual context implementations will be delievered by someone else 
class Context(object):
    __metaclass__ = ContextMetaclass
    
    @staticmethod
    def fromPyGUICanvas(canvas):
      import UIToolkit.Drawing.PyGUICanvas as PyGUICanvas
      return PyGUICanvas.ContextFromPyGUICanvas(canvas)

    def __new__(cls):
        raise TypeError('Cannot instantiate the abstract class Context! Instantiate the implementation-specific classes instead')

