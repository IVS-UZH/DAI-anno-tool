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



from UIToolkit import View, PresentationProperty
from UIToolkit.Drawing import *
from collections import namedtuple
import sys

__all__ = ('Label', )

class Label(View):
  # --- presentation
  font     = PresentationProperty(Font.makeFont, Font.defaultFont)
  color    = PresentationProperty(Color, 'black')
  margins  = PresentationProperty(namedtuple('Margins', ('left', 'right', 'top', 'bottom'))._make, (10, 10, 5, 5))
  value    = PresentationProperty(unicode, 'label')
  align    = PresentationProperty(str, 'center')
  minWidth = PresentationProperty(int, 0)

  @View.presentationState.changed
  def presentationState(self, context):
    """ Recompute the size """
    left, right, top, bottom = self.margins
    
    font = self.font
    value = self.value
    
    textw = font.getWidthForString(value)
    linesn = len(value.split('\n'))
    texth = (font.ascent + font.descent)*linesn + font.leading*(linesn-1)
    
    self.size = Size(max(self.minWidth, left+right+textw), top+bottom+texth)
    self.dirty()
        
  # ++++++++++++++++++ drawing +++++++++++++++++   
  # OS X handles multi-lien drawing and all otehr shizzle correctl
  # Windows implementation sucks, so we need to do it manually
  # 
  if sys.platform == 'darwin':
    def draw(self, rect): 
      super(Label, self).draw(rect)
      w, h = self.size
      font = self.font
      left, right, top, bottom = self.margins
      value = self.value
    
      # compute the x coordinate        
      if self.minWidth == 0:
        x = left
      else:
        align = self.align
        
        if   align == 'left': x = left
        elif align == 'center': x = left + ((w - left - right) - font.getWidthForString(value))/2
        elif align == 'right': x = (w - right) - font.width(value)
        else: raise ValueError('align must be one of center, left, right')
          
          
      font.makeCurrent()
      self.color.makeDrawcolor()   
      Context.drawTextAtPosition(value, Point(x, top + font.ascent)) 
  else:
    def draw(self, rect): 
      super(Label, self).draw(rect)
      w, h = self.size
      font = self.font
      left, right, top, bottom = self.margins
      value = self.value
    
      # compute the x coordinate        
      if self.minWidth == 0:
        x = left
      else:
        align = self.align
        
        if   align == 'left': x = left
        elif align == 'center': x = left + ((w - left - right) - font.getWidthForString(value))/2
        elif align == 'right': x = (w - right) - font.width(value)
        else: raise ValueError('align must be one of center, left, right')
          
          
      font.makeCurrent()
      self.color.makeDrawcolor()   
      y = top + font.ascent
      for line in value.split('\n'):
        Context.drawTextAtPosition(line, Point(x, y))
        y += font.ascent + font.descent

  

