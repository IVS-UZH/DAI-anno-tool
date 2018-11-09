# encoding: utf-8

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


from UIToolkit import *
from observing import *
from SafeCall import safecall
import itertools

ItalicFont = Drawing.Font(Drawing.Font.defaultFont.familyname, Drawing.Font.defaultFont.size, ['italic'])


class SimpleSpanView(View):
  """
    The simple, non annotable span view. 
  """
      
  @observable_property
  def views(self):
    return itertools.chain([self.headerLabel, self.translationLabel])
    
    
  def addView(self, view, after = None, before = None):
    pass
    
  def removeView(self, view):
    pass
    
    
  # ----- layout logic
  performsLayout = True
  
  tokenInitialOffset  = PresentationProperty(int, 50)
  
        
  def computeLayout(self):
    """ Arrange the subviews """        
    # position the labels
    self.headerLabel.position = (15, 0)
    self.translationLabel.position = (self.tokenInitialOffset, self.headerLabel.rect.y1 + 15)
    
  
    # adjust the size of the span
    self.size = (max(500, max(v.rect.x1 for v in self.views)), self.translationLabel.rect.y1 + 25)
   
    # ============= Layouting is finished
    self.dirty()
    self.needsLayout = False
  
  def draw(self, drawRect):
    Drawing.Color('black').makeDrawcolor()
    y = self.headerLabel.rect.center.y
    x0 = self.headerLabel.rect.x0
    x1 = self.headerLabel.rect.x1
    xmax = 500
    
    Drawing.Path().moveTo(0, y).lineTo(x0, y).stroke()
    if xmax > x1:
      Drawing.Path().moveTo(x1, y).lineTo(xmax, y).stroke()
    #Drawing.Path.initWithRect(0, 0, *self.size).stroke()
    
  
  # ----- initializer
  def __init__(self, *args, **kwargs):
    self.__tokenViews = []
    self.__nodeViews  = []
    self.headerLabel = UI.Label(margins=(10, 10, 0, 0))
    self.translationLabel = UI.Label(margins=(5, 0, 0, 0), font=ItalicFont)
    super(SimpleSpanView, self).__init__(*args, **kwargs)  
    
    
    self.headerLabel.superview = self
    self.headerLabel.value = self.controller.representedObject.headerLabel
  
    self.translationLabel.superview = self
    tokenstring = u" ".join(token.transcription for token in self.controller.representedObject.tokens)
    self.translationLabel.value = u"%s\n%s" % (tokenstring, self.controller.representedObject.translation)
    
    
