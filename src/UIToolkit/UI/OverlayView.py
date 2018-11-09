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


class OverlayView(View):
  """ A view that attaches itself to another view """
  
  # ----- presentation 
  anchorPosition = PresentationProperty(str, "above")
  distance = PresentationProperty(int, 0)
  distanceToEdge = PresentationProperty(int, 15)
  
  @observable_property
  def anchor(self):
    try:
      return self.__anchor
    except AttributeError:
      return None
      
  @anchor.setter
  def anchor(self, value):
    if self.anchor is not None and self.anchor is not value:
      observers(self.anchor, 'globalRect').after -= self.__anchor_rect_changed
      self.superview.removeView(self)
    
    self.__anchor = value
    
    if self.anchor is not None:
      self.anchor.window.contents.addView(self)
      observers(self.anchor, 'globalRect').after += self.__anchor_rect_changed
      observers(self.anchor, 'rect').after += self.__anchor_rect_changed
      didChange(self, 'presentationState', {})
      
      # print "Added overlay view, views are now %s" % list(self.superview.views)
      # print "Overla view views are %s" % (tuple(self.views),)
      
  
  def __anchor_rect_changed(self, obj, context):
    if obj is not self.anchor: return
    
    didChange(self, 'presentationState', {})
  
  @View.presentationState.changed
  def presentationState(self, context):
    """ Computes the new position for the overlay view """
    if self.anchor is None or self.superview is None: return
    
    w, h = self.size
    x0, y0, x1, y1 = self.anchor.globalRect
    
    # find the suitable location for the overlay view
    if self.anchorPosition == "above":
      x = (x0 + x1)/2 - w/2
      y = (y0 - h - self.distance)      
    elif self.anchorPosition == "bottom right":
      x = x1
      y = y1 - h
    elif self.anchorPosition == "below":
      x = (x0 + x1)/2 - w/2
      y = (y1  + self.distance)
    elif self.anchorPosition == "above right":
      x = x1 
      y = y0 - h/2
    elif self.anchorPosition == "right":
      x = x1 
      y = y0 
    elif self.anchorPosition == "over":
      x = (x0+x1)/2 - w/2
      y = (y0+y1)/2 - h/2
    else:
      raise ValueError("Unknown anchorPosition paramenter %s" % self.anchorPosition)  
      
    # adjust the width and height
    if x < self.distanceToEdge: 
      x = self.distanceToEdge
    if x + w > self.superview.size.width - self.distanceToEdge: 
      x = self.superview.size.width - self.distanceToEdge - w
    
    #print("------ self.rect = %s, new.rect = %s, equal = %s" % (self.rect, rect, self.rect == rect))
    if abs(self.position.x - x) > 0.5 or abs(self.position.y - y) > 0.5:
      self.position = (x, y)
    
    
  