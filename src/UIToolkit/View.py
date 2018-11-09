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



from UIToolkit import Responder, Rect, Point, Size
from SafeCall import safecall
from observing import *
from weakref import WeakKeyDictionary, WeakSet


# exports
__all__ = ('View', 'PresentationProperty', 'PresentationAttribute', 'PresentationStateDelegate')


class dependentobservableproperty(property, ObservableAttribute):
  """ 
    A utility property class that is also an observable attribute but with 
    the observation protocol managed by its owner
  """ 
  pass
  
  

      
  
class View(Responder):
  """
    Implements a visible UI element that the user can interact with 
  """
  def __init__(self, superview = None, **kwargs):
    self.__superview  = None
    self.__rect       = Rect(0, 0, 0, 0)
    self._views      = []
    self.__controller = None
    
#    disableObserving(self)
          
    # set the properties
    for k, v in kwargs.iteritems():
      setattr(self, k, v)
      # prop = getattr(self.__class__, k, None)
      # if prop is not None and hasattr(prop, '__set__'):
      #   prop.__set__(self, v)
      # else:
      #   setattr()
      
 #   enableObserving(self)
    
        
    # set the optional superview
    if superview is not None:
      self.__superview = superview
      superview.addView(self)    
      
    # notify the cotroller that the view has loaded
    safecall(self.controller).viewLoaded()

    # and mark the presentation state as changed to make sure that everything is set up correctly
    # this is conservtive, but I know of no better way to do it
    self.needsLayout = True
    didChange(self, 'presentationState', {})
    
        
  def __repr__(self):
    return "%s at %s" % (self.__class__.__name__, self.globalRect)
    
  # --------- presentation state ---     
  @ObservableState
  def presentationState(self, context):
    self.dirty()
  
  # --------- state changing notifications (for subclasses) --- 
  def addingSubview(self, view): pass
  def removingSubview(self, view): pass
  def addedSubview(self, view): pass
  def removedSubview(self, view): pass

  def subviewRectChanged(self, view, old_rect, new_rect): pass
  
  # --------- layout calculation ---------
  performsLayout = False
  
  viewsThatNeedLayout = WeakSet()
  
      
  def computeLayout(self):
    """ Perform layout computation. Subclasses can override this to do layout """
    safecall(self.controller).computeLayoutForView(self)
    self.needsLayout = False
    
  
  @observable_property
  def needsLayout(self):
    return self in View.viewsThatNeedLayout
    
  @needsLayout.setter
  def needsLayout(self, value):
    if not isinstance(value, bool):
      raise ValueError('needsLayout must be boolean')
      
    if value and self.performsLayout:
      View.viewsThatNeedLayout.add(self)
    else:
      View.viewsThatNeedLayout.discard(self)   
    

      
    # self.dirty() 
    
  @staticmethod
  def changes_layout(method):
    """
        This is a decorator for methods which force layout computation
    """
    def _(self, *args, **kwargs):
        v = method(self, *args, **kwargs) 
        self.needsLayout = True
        return v
    
    _.__name__ = method.__name__
    return _  
  
  # --------- controller mechanism ---------
  @property
  def controller(self):
    return self.__controller
    
  @controller.setter
  def controller(self, controller):
    self.__controller = controller
    
    
  def findControllerForMethod(self, method):
    """
      Attempts to find a controller that implements a given method
      The preferred implementor is the view controller. If no such implementor exists, 
      we look in the responder chain chain.
    
      The purpose of this method is to provide flexible interface
      for the view to adjust to the current state. Another way
      would be to use KVO, no? 
    """  
    controller = None
    
    # check the controller
    if controller is None and self.controller is not None:
      controller = self.controller if self.controller.respondsToAction(method) else None
    
    # look in the first responder hierarchy
    if controller is None and self.window is not None: 
      controller = self.window.firstResponder.findResponderForAction(method)
    
      
    return controller
    
  #---------- responder chain -------------
  @property
  def nextResponder(self):
    if self.controller is not None:
      return self.controller
    else:
      return self.superview
      
  # @property
  # def responderChain(self):
  #   yield self
  #   if self.controller is not None:
  #     yield self.controller
  #
  #   superview = self.superview
  #   if superview is None:
  #     return
  #
  #   for responder in superview.responderChain:
  #     yield responder
      
  #---------- first responder protocol -------------
  @property
  def canBecomeFirstResponder(self):
    return False
  
  def becameFirstResponder(self):
    safecall(self.controller).viewBecameFirstResponder()
    
  def yieldedFirstResponder(self):
    safecall(self.controller).viewYieldedFirstResponder()        
    
  # --------- view hierarchy ---------
  @property
  def superviewChain(self):
    view = self.superview
    while view:
      yield view
      view = view.superview
  
  @observable_property
  def superview(self):
    return self.__superview  

  @superview.setter
  def superview(self, value):
    willChange(self, 'globalRect', {})
    self.__superview  = value
    didChange(self, 'globalRect', {})

    
  @observable_property
  def views(self):
    return iter(self._views)
    
  def addView(self, view, after = None, before = None, atPosition= None):
    safecall(self.controller).addingSubview(view)
    self.addingSubview(view)
    willChange(view, 'superview', {})
    willChange(view, 'globalRect', {})
    
    view.__superview = self
    
    if atPosition is not None:
      i = atPosition
    elif after is not None:
      i = self._views.index(after)+1
    elif before is not None:
      i = self._views.index(before)
    else:
      i = len(self._views)
    
    
    self._views.insert(i, view)
    view.dirty()
    didChange(view, 'superview', {})
    didChange(view, 'globalRect', {})
    self.addedSubview(view)
    safecall(self.controller).addedSubview(view)
    self.needsLayout = True
    
    
  def removeView(self, view):
    if view not in self._views:
      ValueError("%s not a subview of this view")
      
    safecall(self.controller).removingSubview(view)
    self.removingSubview(view)
    rect = view.rect
    willChange(view, 'globalRect', {})
    willChange(view, 'superview', {})
    view.__superview = None
    self._views.remove(view)
    view.dirty()
    didChange(view, 'globalRect', {})
    didChange(view, 'superview', {})
    self.removedSubview(view)
    safecall(self.controller).removedSubview(view)
    self.dirty(rect)
    self.needsLayout = True
  
  @property  
  def window(self):
    if self.superview is None:
      return None
    else:
      return self.superview.window
    
  # --------- view rect ---------
  @observable_property
  def rect(self):
      return self.__rect
      
  @rect.setter
  def rect(self, rect):
      if rect.__class__ is not Rect: rect = Rect(*rect)

      # get the old rect
      old = self.__rect
      
      # test changes
      changes_position = old.origin != rect.origin
      changes_size = old.size != rect.size
      
      # set the rect
      if changes_position:
        willChange(self, 'position', {})
      if changes_size:
        willChange(self, 'size', {})
      willChange(self, 'presentationState', {})
      willChange(self, 'globalRect', {})

      self.__rect = rect
      
      if changes_position:
        didChange(self, 'position', {})
      if changes_size:
        didChange(self, 'size', {})
        self.needsLayout = True
      didChange(self, 'globalRect', {})
      didChange(self, 'presentationState', {})
      
      
      safecall(self.controller).viewRectChanged(old, rect)
        
      # if we have a superview, we must perform all the nessesary notifications
      if self.superview is not None:
        self.superview.needsLayout = True
        self.superview.subviewRectChanged(self, old, rect)
        self.superview.dirty(old, rect)
        
        
          
  @dependentobservableproperty
  def position(self): return self.rect.origin
  
  @position.setter
  def position(self, (x, y)): 
      if Point(x, y) == self.position: return
    
      w, h = self.rect.size
      self.rect = Rect(x, y, x+w, y+h)    

  @dependentobservableproperty
  def size(self): return self.rect.size
  
  @size.setter
  def size(self, (w, h)):
      if Size(w, h) == self.size: return
    
      x, y = self.rect.origin
      self.rect = Rect(x, y, x+w, y+h)
      
  #--------- hit testing ---------
  def getViewsInRect(self, rect):
    """
      Return all views that are covered by the rect, including their subviews, excluding self
    """  
    # this list stores the hits
    hitlist = []
      
    # record hits for all views in the hierarchy
    for view in self.views:
      if view.rect ^ rect:
        hitlist.extend([view] + view.getViewsInRect(rect.clip(view.rect).translate(-view.position)))
    
    return hitlist
    
  def hit(self, point):
    """
      Return the view in the hierarchy that is hit by the point
    """
    # guard agains point being outside the view area
    if point not in Rect(0, 0, *self.size):
      return None
    
#    print "-------- Doing hit test on %s with subviews %s" % (self, list(self.views))
    
    # try to find a subview that is hit 
    for view in reversed(tuple(self.views)):
 #     print ("Testing if %s is hit by %s = %s" % (view, point, point in view.rect))
      if point in view.rect:
        return view.hit(point - view.position)  
      
    # if no subview has been found, return self  
    return self
      
    
    
    
    
        
  #------- coordinate system conversion ----
  @observable_property        
  def globalRect(self):
    rect = self.rect
    s = self.superview
    while s is not None:
      rect = rect.translate(s.rect.origin)
      s = s.superview
      
    return rect
    
  @globalRect.changing
  def globalRect(self, context):
    for v in self.views: willChange(v, 'globalRect', {})

  @globalRect.changed
  def globalRect(self, context):
    for v in self.views: didChange(v, 'globalRect', {})
    
  def rectToViewSpace(self, view):
    """
      Convert the view rect into the coordinate system of another view
      Only makes sense if the views are part of the same hierarchy
    """
    return Rect.fromOriginPointWithSize(self.globalRect.origin - view.globalRect.origin, self.size)       
  
  
  #------- event handling
  def mouseDown(self, event):
    # translate the mouse coordinates from local to superview rect
    if self.superview is not None:
      pos = event.position
      pos = pos + (self.superview.position - self.position)
      self.superview.mouseDown(event.eventReplacing(position = pos))

  def mouseUp(self, event):
    # translate the mouse coordinates from local to superview rect
    if self.superview is not None:
      pos = event.position
      pos = pos + (self.superview.position - self.position)
      self.superview.mouseUp(event.eventReplacing(position = pos))
      
  def rightMouseDown(self, event):
    # translate the mouse coordinates from local to superview rect
    if self.superview is not None:
      pos = event.position
      pos = pos + (self.superview.position - self.position)
      self.superview.rightMouseDown(event.eventReplacing(position = pos))

  def rightMouseUp(self, event):
    # translate the mouse coordinates from local to superview rect
    if self.superview is not None:
      pos = event.position
      pos = pos + (self.superview.position - self.position)
      self.superview.rightMouseUp(event.eventReplacing(position = pos))    

  def mouseEnteredArea(self, event):
    pass #safecall(self.controller).mouseEnteredView(self)

  def mouseLeftArea(self, event):
    pass #safecall(self.controller).mouseLeftView(self)

  #--------- drawing mechanism ---
  def draw(self, rect): 
    pass
      
  @staticmethod
  def dirtying(method):
    """
        This is a decorator for methods which force redraw of the object
    """
    def _(self, *args, **kwargs):
        v = method(self, *args, **kwargs) 
        self.dirty()
        return v
    
    _.__name__ = method.__name__
    return _
      
  def dirty(self, *rects):   
    # only makes sence if we have somewhere to propagate those redraw notifications
    #print("%s is dorty at %s with super %s" % (self, rects, self.superview))
    
    if self.superview is None: return
    
    if len(rects) == 0:
      #if self in View.dirtyViews: return
      #self.superview.dirty()
      self.superview.dirty(self.rect)
      #View.dirtyViews.add(self)
    else:
        rect_in_superview = self.rect
        # translate and clip to the visible rect in the superview's coordinates
        rects = [r.translate(rect_in_superview.origin) for r in rects if r is not None]
        #rects = [r for r in (r.translate(rect_in_superview.origin).clip(rect_in_superview) for r in rects) if r is not None]
        # send it to the superview, if appropriate
        if len(rects) > 0:
            self.superview.dirty(*rects)
            
# ----- presentation state            
_emptydict = {}

class PresentationAttribute(ObservableAttribute):
  def __changing__(self, obj, context):
    ObservableAttribute.__changing__(self, obj, context)
    willChange(obj, 'presentationState', context)

  def __changed__(self, obj, context):
    ObservableAttribute.__changed__(self, obj, context)
    didChange(obj, 'presentationState', context)

            
class PresentationProperty(PresentationAttribute):
  """ 
    An observable property that holds presentation state (e.g. color)
    Setting this property triggers a redraw
    
    To be used in view-derived classes like this:
    
      color = PresentationProperty(Color, 'black')
      
    Color is the class the value will be coerced to, 'black' is the default value
  """
  
  def __init__(self, wrapper, default, triggersLayout = False):
    self.__wrapper = wrapper
    self.default = self.transformValue(default)
    self.__dict = WeakKeyDictionary()
    self.__triggers_layout    = triggersLayout
    
    
  def override(self, default):
    return PresentationProperty(self.__wrapper, default, triggersLayout = self.__triggers_layout)
    
    
    
  def __findkey(self, cls):
    # find the name for this property
    allkeys = dir(cls)
    for key in allkeys:
      try:
        if getattr(cls, key) is self:
          return key
      except: pass
        
    return None
    
  def transformValue(self, value):
    # if self.__wrapper is None:
    #   return value
    # else:
    return self.__wrapper(value)
  
  def __get__(self, obj, cls = None):
    if obj is None:
      return self
    else:
      return self.__dict.get(obj, self.default)
    
  def __set__(self, obj, value):
    value = self.transformValue(value)
    
    old = self.__get__(obj)
    
    # guard against unnessesary change
    if old == value:
      return
      
    self.__changing__(obj, {})
    
    
    #print "Setting %s.%s to %s" % (obj, self.__findkey(obj.__class__), value)
    
    if value == self.default:
      self.__dict.pop(obj)
    else:
      self.__dict[obj]  = value

    if self.__triggers_layout:
      obj.needsLayout = True
      
    self.__changed__(obj, {})
    
      
            
class PresentationStateDelegate(object):
  """ 
    A class that handles presentation state for an object in case
    this state should not be exposed to the user (e.g. buttons)
  """
  def __init__(self, view):
    self.view = view
  
  @property
  def needsLayout(self):
    return self.view.needsLayout
    
  @needsLayout.setter
  def needsLayout(self, value):  
    self.view.needsLayout = value
        
  @ObservableState  
  def presentationState(self, context):
    didChange(self.view, 'presentationState', context)
    
  @presentationState.changing
  def presentationState(self, context):
    willChange(self.view, 'presentationState', context)
