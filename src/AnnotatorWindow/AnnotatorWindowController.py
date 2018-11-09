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
from SafeCall import safecall
from observing import *
from SpanController import *
from weakref import WeakSet, ref

class AnnotatorWindowController(WindowController):
  """ 
    The annotator window controller represents a view into the corpus.
    It also controls the interaction with the corpus
  """
  
  def __init__(self, document):
    super(AnnotatorWindowController, self).__init__()
    self.document = document
    self.__highlightedViews = frozenset([])
    self.__selectedView    = None
    self.__selectibleViews = WeakSet()
    self.__highlightableViews = WeakSet()
    self.__showsGloss = False
    
  def windowLoaded(self):
    self.window.visible = True
    
    self.window.layoutInProgress = True
    # init the span views
    spanContainer = UI.SimpleLayoutContainer(position = (25, 50), controller = self)
    self.containerView = spanContainer
    self.window.contents.addView(spanContainer)
    self.spanControllers = [SpanController(span, self) for span in self.document.spans]
    self.window.layoutInProgress = False
    
    # observe the mouseover view
    observers(self.window, 'mouseoverView').after += self.mouseoverViewChanged
    
    # observe the visible rect
    observers(self.window.contents, 'visibleRect').after += self.visibleRectChanged
    
  def windowClosing(self):
    self.document.close()
    
  # ---- display state
  @observable_property
  def showsGloss(self):
    return self.__showsGloss
    
  @showsGloss.setter
  def showsGloss(self, value):
    self.__showsGloss = value  
    
  # ---- scrolling and lazy element loading
  def visibleRectChanged(self, sender, context):
    pass
    # visibleRect = self.window.contents.visibleRect
    #
    # # find the visible spans
    # first_visible_span_i = None
    # last_visible_span_i  = None
    #
    # for i, controller in enumerate(self.spanControllers):
    #   if controller.view.rect.y1 >= visibleRect.y0:
    #     first_visible_span_i = i
    #     break
    #
    # for i, controller in reversed(list(enumerate(self.spanControllers))):
    #   if controller.view.rect.y0 <= visibleRect.y1:
    #     last_visible_span_i = i
    #     break
    #
    # first_visible_span_i = 0 if first_visible_span_i is None else first_visible_span_i
    # last_visible_span_i = len(self.spanControllers)-1 if last_visible_span_i is None else last_visible_span_i
    #
    # print "Visible spans between %s and %s" % (first_visible_span_i, last_visible_span_i)
    #
    # # if nothing is selected etc., we can safely unload spans
    # can_unload = (self.selectedView is None and len(self.highlightedViews) ==0)
    #
    # for i, controller in enumerate(self.spanControllers):
    #   if i >= first_visible_span_i and i <= last_visible_span_i:
    #     if not controller.modelLoaded: controller.modelLoaded = True
    #   elif can_unload:
    #     if controller.modelLoaded: controller.modelLoaded = False
        
      
    #
    # # load the visible span controllers
    # for controller in self.spanControllers[first_visible_span_i:(last_visible_span_i+1)]:
    #   if controller.modelLoaded: break
    #   controller.modelLoaded = True
    
    
    
  # ---- editable support
  def editableActivated(self, sender):
    safecall(sender.controller).editableActivated(sender)


  # ---- support for element selection  
  @observable_property
  def selectedView(self):
    return self.__selectedView
    
  @selectedView.setter
  def selectedView(self, view):    
    if self.selectedView is not None:
      self.selectedView.selected = False

    self.__selectedView = view

    if self.selectedView is not None:
      self.selectedView.selected = True
    
    self.computeHighlights()
      
  def viewSelected(self, view):      
    self.selectedView = view
    
       
  # ---- support for element highlighting (more then one element can be highlighted at the same time!)
  @observable_property
  def primaryHighlightedView(self):
    try:
      return self.__primaryHighlightedView
    except:
      return None
      
  @observable_property
  def highlightedViews(self):
    return self.__highlightedViews
    
  def mouseoverViewChanged(self, view, context):
    self.computeHighlights()
      
  def computeHighlights(self):
    # we want to highlight the mouseover view, but only if the view 
    # or one of its superviews are highlightable
    highlightedView = self.window.mouseoverView
    while highlightedView is not None and not getattr(highlightedView, 'highlightable', False):
      highlightedView = getattr(highlightedView, 'masterView', highlightedView.superview)
      
    highlightedView = highlightedView if getattr(highlightedView, 'highlightable', False) else None
    
    if highlightedView is not self.primaryHighlightedView:
      willChange(self, 'primaryHighlightedView', {})
      # print "primaryHighlightedView = %s" % highlightedView
      self.__primaryHighlightedView = highlightedView
      didChange(self, 'primaryHighlightedView', {})
    
    # get the hierachy of views that also need to be highlighted
    views = [v for v in (highlightedView, self.selectedView) if v is not None]
    
    i = 0
    while i < len(views):
      views.extend(getattr(views[i], 'dependentViews', []))
      i = i + 1
      
    views = frozenset(views)
    if views == self.__highlightedViews: return  
      
    willChange(self, 'highlightedViews', {})
    
    # change highlights on views
    for view in self.__highlightedViews - views:
      view.highlighted = False
    for view in views - self.__highlightedViews:  
      view.highlighted = True
    
    self.__highlightedViews = frozenset(views)
    didChange(self, 'highlightedViews', {})
      
  # ---- default event handling
  def keyDown(self, event):
    if event.key in ('enter', 'return', 'esc'):
      self.selectedView = None
        
          
 
    
  def toggleShowGloss(self, sender):
    self.window.layoutInProgress = True
    self.showsGloss = not self.showsGloss
    self.window.layoutInProgress = False
    
    
  def getStateForMenuItem(self, item):
    if item.name == 'Show lemmas':
      if self.showsGloss:
        return 1
      else:
        return 0
      
  
    
          
          
  
  