##############################################################
# path.py
#
# Defines the path drawing API

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



import collections

import UIToolkit
from UIToolkit.Drawing import *

##############################################################
# Path class for representing a sequence of 
# drawing operations
# 
# 
# Internally, a path is simply a list which contains primitive 
# operations
#
class Path(object):
    # ++++++++++++++++++ definition of drawign operations +++++++++++++++++   
    class Operations(object):
        class MoveTo(Point): __slots__ = []
        class LineTo(Point): __slots__ = []
        CurveTo = collections.namedtuple('CurveTo', 'endPoint,controlPoint1,controlPoint2')
        class Close(tuple): __slots__ = []
    
    # ++++++++++++++++++ initialization +++++++++++++++++    
    def __init__(self):
        self.__operations = []
        self.__thickness = 1
        
    @classmethod 
    def initWithPath(cls, path, thickness = None):
        self = cls()
        
        self.__operations = list(path.__operations)
        self.__thickness = thickness if thickness is not None else path.__thickness
        
        return self

    @classmethod 
    def initWithRect(cls, x0, y0, x1, y1):
        return cls().moveTo(x0, y0).lineTo(x1, y0).lineTo(x1, y1).lineTo(x0, y1).close()

    @classmethod 
    def initWithRoundedRect(cls, x0, y0, x1, y1, roundness = 0.1):
        radius_x = (x1-x0)*roundness
        radius_y = (y1-y0)*roundness
        
        x0 += 1
        x1 -= 1 
        y0 += 1 
        y1 -= 1
        
        
        self = cls()
        self.moveTo(x0+radius_x, y0)
        self.lineTo(x1-radius_x, y0)
        self.curveTo((x1, y0+radius_y), (x1, y0), (x1, y0))
        #self.curveTo((x1, y0+radius), (x1, y0+radius), (x1-radius, y0))
        self.lineTo(x1, y1-radius_y)
        self.curveTo((x1-radius_x, y1), (x1, y1), (x1, y1))
        #self.curveTo((x1-radius, y1), (x1, y1-radius), (x1-radius, y1))
        self.lineTo(x0+radius_x, y1)
        self.curveTo((x0, y1-radius_y), (x0, y1), (x0, y1))
        #self.curveTo((x0, y1-radius), (x0, y1-radius), (x0+radius, y1))
        self.lineTo(x0, y0+radius_y)
        self.curveTo((x0+radius_x, y0), (x0, y0), (x0, y0))
        #self.curveTo((x0+radius, y0), (x0+radius, y0), (x0, y0+radius))
        self.close()
        
        return self
        
        
                    
    # ++++++++++++++++++ lien draw width +++++++++++++++++               
    @property
    def thickness(self): return self.__thickness
    
    @thickness.setter
    def thickness(self, v): self.__thickness = v
    
    
    # ++++++++++++++++++ drawing operations +++++++++++++++++                   
    def moveTo(self, x, y):
        self.__operations.append(Path.Operations.MoveTo(x, y))  
        return self  

    def lineTo(self, x, y):
        self.__operations.append(Path.Operations.LineTo(x, y))    
        return self  

    def curveTo(self, (x, y), (cp1_x, cp1_y), (cp2_x, cp2_y)):
        self.__operations.append(Path.Operations.CurveTo(Point(x, y), Point(cp1_x, cp1_y), Point(cp2_x, cp2_y)))
        return self  
    
    def close(self):
        self.__operations.append(Path.Operations.Close())
        return self  
        
    # ++++++++++++++++++ visualization +++++++++++++++++                   
    @property
    def operations(self): return self.__operations
    
    def __repr__(self):
        return 'Path with operations %s' % (self.__operations, )
            
    # ++++++++++++++++++ abstract! +++++++++++++++++        
    def stroke(self): Context.strokePath(self, Point(0, 0))

    def fill(self): Context.fillPath(self, Point(0, 0))
    
    def fillAndStroke(self): Context.fillAndStrokePath(self, Point(0, 0))

    def strokeAtOrigin(self, x, y): Context.strokePath(self, Point(x, y))

    def fillAtOrigin(self, x, y): Context.fillPath(self, Point(x, y))
    
    def fillAndStrokeAtOrigin(self, x, y): Context.fillAndStrokePath(self, Point(x, y))
    
        
        
        

