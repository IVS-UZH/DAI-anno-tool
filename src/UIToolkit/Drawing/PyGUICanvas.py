from UIToolkit.Drawing import *
from GUI import rgb as PyGUI_rgb

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
# A graphics context which wraps a PyGIU canvas
# 
# The toolkit will involve recursive clipping of the canvas to draw subitems,  
# so we provide an efficient way to do this on the canvas. In this regard, the
# wrapper is a virtual window into the actual canvas.  We do not botehr with clipping,  
# as we assume that the clipping is doen by someone else
#
# Note that the wrapper WILL make destructive changes to the canvas state, so make sure to
# use gsave/grestore as appropriate. Similarly, you shoudl not change the canvas state when
# the wraper is in use, as it might lead to desynchronization of states
class ContextFromPyGUICanvas(object): 
    __metaclass__ = ContextMetaclass
    
    def __init__(self, canvas):
        self.canvas = canvas
        #self.canvas_offset = Point(canvas_offset_x, canvas_offset_y)
        
        self.color = Color('black')
        self.fillcolor = Color('white')
        
    
    # ++++++++++++++++++ colors +++++++++++++++++    
    @property
    def color(self): return self.__color
    
    @color.setter
    def color(self, color): 
        self.__color = color
        clr = PyGUI_rgb(*color)
        self.canvas.pencolor = clr
        self.canvas.textcolor = clr
    
    @property
    def fillcolor(self): return self.__fillcolor
    
    @fillcolor.setter
    def fillcolor(self, color):
       self.__fillcolor = color
       clr = PyGUI_rgb(*color)
       self.canvas.fillcolor = clr
        
    # ++++++++++++++++++ font state +++++++++++++++++    
    @property
    def font(self):
        return Font._makeWithPyGUIFont(self.canvas.font)

    @font.setter
    def font(self, font):
        self.canvas.font = font._pyguifont
        
    # ++++++++++++++++++ transformation +++++++++++++++++    
    @property
    def transform(self): 
      return self.__transform
    
    @transform.setter
    def transform(self, (x, y)): 
      self.__transform = Point(x, y)
        
    
    
    # ++++++++++++++++++ path drawing +++++++++++++++++    
    def __constructPath(self, path, origin):
        canvas = self.canvas
        Operations = path.Operations
        offset = self.transform + origin
        
        canvas.pensize = path.thickness
        
        canvas.newpath()
        for op in path.operations:
            typ = type(op)
            
            if typ is Operations.MoveTo:
                canvas.moveto(*(op + offset))
            elif typ is Operations.LineTo:
                canvas.lineto(*(op + offset))
            elif typ is Operations.CurveTo:
                canvas.curveto(op[1]+offset, op[2]+offset, op[0]+offset)
            elif typ is Operations.Close:
                canvas.closepath()
                
    
    def strokePath(self, path, origin): 
        self.__constructPath(path, origin)
        self.canvas.stroke()
        
    def fillPath(self, path, origin):
        self.__constructPath(path, origin)
        self.canvas.fill()
        
    
    def fillAndStrokePath(self, path, origin):
        self.__constructPath(path, origin)
        self.canvas.fill()
        self.canvas.stroke()
    
        
    # ++++++++++++++++++ text output +++++++++++++++++    
    def drawTextAtPosition(self, text, point):
        self.canvas.moveto(*(self.transform + point))
        self.canvas.show_text(text)
