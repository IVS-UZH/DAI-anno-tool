##############################################################
# geometry.py
#
# Defines common geometry primitives used in the toolkit

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



import collections, operator

##############################################################
# Represents a two-dimentional position
class Point(collections.namedtuple('Point', 'x,y')):
    __slots__ = []
    
    def __add__(self, point):
        return Point(self[0] + point[0], self[1] + point[1])
    __radd__ = __add__
    
    def __sub__(self, point):
        return Point(self[0] - point[0], self[1] - point[1])
    __rsub__ = __sub__
        
    def __mul__(self, number):
        return Point(self[0]*number, self[1]*number)
    __rmul__ = __mul__    
            
    def __div__(self, number):
        return Point(self[0]/number, self[1]/number)
    __rdiv__ = __div__    
        
    def __neg__(self):
        return Point(-self[0], -self[1])    
        
    def __interpolate__(self, target, t):
        invt = 1-t
        return Point(self[0]*invt + target[0]*t, self[1]*invt + target[1]*t)
        
##############################################################
# Represents a two-dimentional size
class Size(collections.namedtuple('Size', 'width,height')):
    __slots__ = []
    
    def __add__(self, size):
        return Size(self[0] + size[0], self[1] + size[1])
    __radd__ = __add__
        
        
    def __mul__(self, number):
        return Size(self[0]*number, self[1]*number)
    __rmul__ = __mul__    
        
            
    def __div__(self, number):
        return Size(self[0]/number, self[1]/number)
    __rdiv__ = __div__    
        
        
    def __interpolate__(self, target, t):
        invt = 1-t
        return Size(self[0]*invt + target[0]*t, self[1]*invt + target[1]*t)
        
    
        

##############################################################
# Represents a two-dimentional rectangle
class Rect(collections.namedtuple('Rect', 'x0, y0, x1, y1')):
    __slots__ = []
    
    @classmethod
    def fromOriginPointWithSize(cls, origin, size):
        x, y = origin
        w, h = size
        return cls(x, y, x+w, y+h)
        
        
    @classmethod
    def boundingRect(cls, *rects):
        return cls(min(*(r[0] for r in rects)), min(*(r[1] for r in rects)), max(*(r[2] for r in rects)), max(*(r[3] for r in rects)))
    
    @classmethod     
    def intersection(cls, *rects):
        x0  = max(*(r[0] for r in rects))
        y0  = max(*(r[1] for r in rects))
        x1  = min(*(r[2] for r in rects))
        y1  = min(*(r[3] for r in rects))
        
        if x0>=x1 or y0>=y1: return None
        
        return Rect(x0, y0, x1, y1)
    
    
    @property
    def origin(self):
        return Point(self[0], self[1])

    @property
    def size(self):
        return Size(self[2] - self[0], self[3] - self[1])
        
    @property
    def width(self):
        return self[2] - self[0]

    @property
    def height(self):
        return self[3] - self[1]
    
    left = property(operator.itemgetter(0))    
    right = property(operator.itemgetter(2))
    top = property(operator.itemgetter(1))
    bottom = property(operator.itemgetter(3))
            
    @property
    def center(self):
        return Point((self[2] + self[0])/2, (self[3] + self[1])/2)

    def __xor__(self, rect):
        """ 
            Tests intersection between rects
        """
        return self[0] <= rect[2] and self[2] >= rect[0] and self[1] <= rect[3] and self[3] >= rect[1]
        
    def __contains__(self, item):
        if item.__class__ is Rect:
            return item[0]>=self[0] and item[1]>=self[1] and item[2]<=self[2] and item[3]<=self[3]
        elif item.__class__ is Point:
            return item[0]>=self[0] and item[1]>=self[1] and item[0]<=self[2] and item[1]<=self[3]
        else:
            raise ValueError('I do not know how to test if %s is part of a rect' % item)
            
            
    def translate(self, point):
        x0, y0, x1, y1 = self
        x, y = point
        return Rect(x0+x, y0+y, x1+x, y1+y)
        
    def clip(self, rect):
        x0  = max(self[0], rect[0])
        y0  = max(self[1], rect[1])
        x1  = min(self[2], rect[2])
        y1  = min(self[3], rect[3])
        
        if x0 >= x1 or y0 >= y1: return None
        
        return Rect(x0, y0, x1, y1)
        
    
    def align(self, **kwargs):
        w, h = self.size
        x, y = self.origin
        
        for k, v in kwargs.iteritems():
            if k == 'left':
                x = v                
            elif k == 'right':
                x = v-w
            elif k == 'top':
                y = v
            elif k == 'bottom':
                y = v - h
                
        return Rect(x, y, v+w, y+h)
            
    # def __add__(self, rect):
    #     return Rect(self[0] + rect[0], self[1] + rect[1], self[2] + rect[2], self[3] + rect[3])
        
    def __interpolate__(self, target, t):
        invt = 1-t
        return Rect(self[0]*invt + target[0]*t, 
                    self[1]*invt + target[1]*t,
                    self[2]*invt + target[2]*t,
                    self[3]*invt + target[3]*t)
    
