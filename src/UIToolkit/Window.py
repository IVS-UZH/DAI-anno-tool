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



import UIToolkit
import UIToolkit.Drawing as Drawing
from observing import observable_property, ObservableAttribute, willChange, didChange
from UIToolkit import Responder, Action, Event
from UIToolkit import Application
from UIToolkit import Rect, Point
from SafeCall import safecall
from weakref import WeakSet

class dependentobservableproperty(property, ObservableAttribute): 
  pass



class Window(Responder):
  def __init__(self, **kwargs):
    self.__window = self.www  = GUI_Window(size=(900, 700))
    self.__window.windowWrapper = self
    self.__contents = ScrollView(self, self.__window.scrollview)
    self.__firstResponder = self
    self.__defaultFirstResponder = None
    
    self.__controller = kwargs.get('controller')
    if self.__controller is not None:
      self.__controller.window = self
    
    safecall(self.controller).windowLoaded()
    
  @property
  def contents(self):
    return self.__contents  
      
  @observable_property  
  def visible(self):  
    return self.__window.visible

  @observable_property  
  def title(self):  
    return self.__window.title

  @title.setter  
  def title(self, value):  
    self.__window.title = value

    
  @visible.setter
  def visible(self, value):  
    self.__window.visible = value
    
  @observable_property  
  def statusMessage(self):
    return self.__window.statusbar.message
    
  @statusMessage.setter
  def statusMessage(self, value):
    self.__window.statusbar.message = value
    
  # ---- controller
  @property
  def controller(self):
    return self.__controller
    
  # ---- layout support
  @property
  def layoutInProgress(self):
    return self.contents.layoutInProgress
    
  @layoutInProgress.setter
  def layoutInProgress(self, value):
    self.contents.layoutInProgress = value      
    
  # -- responder chain and first responder
  @property
  def defaultFirstResponder(self):
    return self.__defaultFirstResponder
  
  @defaultFirstResponder.setter
  def defaultFirstResponder(self, value):
    self.__defaultFirstResponder = value
  
  
  @property
  def canBecomeFirstResponder(self):
    return True
  
  @property
  def nextResponder(self):
    if self.controller is not None:
      return self.controller
    else:
      return Application().controller
    
  @observable_property
  def firstResponder(self):
    return self.__firstResponder
    
  def setFirstResponder(self, responder):
    self.firstResponder = responder
    
    return self.firstResponder is responder

  @firstResponder.setter
  def firstResponder(self, responder):
    if responder is None:
      responder = self
    
    # find the item in the hierarchy that is willing to become first responder
    for responder in getattr(responder, 'responderChain', ()):
      if responder.canBecomeFirstResponder:
        break
        
    # check if the item is actually willing to become first responder
    if not responder.canBecomeFirstResponder:
      return
      
    # change the first responder
    safecall(self.firstResponder).yieldedFirstResponder()
    self.__firstResponder = responder
    safecall(self.firstResponder).becameFirstResponder()  
        
  # -- mouseover view
  @observable_property
  def mouseoverView(self):
    return self.__window.scrollview.mouseoverView
  
  # -- commands  
  def closeWindow(self, sender):
    self.close()
  
  def close(self):
    self.__window.close_cmd()
    


# ------ ScrollView implementation

class ScrollView(UIToolkit.View):
  """
    A proxy class that implements View protocol backed by a PyGUI ScrollableView
  """
  def __init__(self, window, backing_view):
    self.dirtyRects = WeakSet()
    self.__layoutInProgress = False
    self.__window = window
    self.__backing_view = backing_view
    backing_view.delegate_view = self
    super(ScrollView, self).__init__()
    
    
  # --------- view hierarchy ---------
  @property
  def superview(self):
    return None

  @property
  def window(self):
    return self.__window
    
    
    
    
  # --------- layout computation ---------
  @property
  def layoutInProgress(self):
    return self.__layoutInProgress
    
  @layoutInProgress.setter
  def layoutInProgress(self, value):
    if value == self.layoutInProgress: return
        
    self.__layoutInProgress = value
    if not value:
      self.computePendingLayouts()
  
  def computePendingLayouts(self):
    if self.layoutInProgress or len(UIToolkit.View.viewsThatNeedLayout) == 0: return
    
    # we want to keep computing layouts for views until no view
    # needs layout. To reduce the layout recomputation to minimum,
    # we want to layout the views down in the hierarchy first
    # There are multiple optimisations that one can perform here, 
    # but at this point I assume that layouting is expensive 
    self.__layoutInProgress = True
    
    while len(UIToolkit.View.viewsThatNeedLayout)>0:
      # these are the views marked for doing layout
      views = list(UIToolkit.View.viewsThatNeedLayout)
      # sort the views so that superviews get layouted after the subviews
      views.sort(cmp = lambda v1, v2: -1 if v2 in set(v1.superviewChain) else 1)
      # do layout on all views
      for view in views:
        view.computeLayout()
      # repeat if there are still some pending views
      
    # adjust the size of the extents to the containers
    w = 0
    h = 0
    for view in self.views:
      w = max(view.rect.x1 + 250, w)
      h = max(view.rect.y1 + 250, h)
      
    self.size = (w, h)
    
    self.__layoutInProgress = False
          
  #---------- responding -------------
  @property
  def nextResponder(self):
    return self.__window
      
  @property
  def responderChain(self):
    yield self
    for responder in self.__window.responderChain:
      yield responder
    
  # --------- view rect ---------    
  @dependentobservableproperty
  def rect(self):
    return  Rect(0, 0, *self.__backing_view.extent) 

  @dependentobservableproperty
  def position(self):
    return (0, 0)
    
  @dependentobservableproperty  
  def size(self):
    return self.rect.size
    
  @dependentobservableproperty
  def visibleRect(self):
    return Rect(*self.__backing_view.viewed_rect())  
    
  @size.setter
  def size(self, (w, h)):
    # guard agains unnessesary change
    if (w, h) == self.size:
      return
      
    willChange(self, 'rect', {})   
    willChange(self, 'size', {})   
    
    self.__backing_view.extent = (w, h)
    
    didChange(self, 'rect', {})   
    didChange(self, 'size', {})   
  
  # --------- draw support ---------    
  def dirty(self, *rects):     
    if len(rects) == 0:
      self.__backing_view.invalidate()
    else:
      for r in rects:
        self.__backing_view.invalidate_rect(r)    
    
    self.computePendingLayouts()
      
        
          
  def draw(self, rect):    
    self.computePendingLayouts()
    #assert(len(UIToolkit.View.viewsThatNeedLayout)==0)
    
    # get the context
    context = Drawing.Context.activeContextNotNone
    canvas = context.canvas
    canvas.erase_rect(rect)    
    
    # draws a view hierarchy
    # offset is the global coordinate offset of the superview
    # rect is the rect to be drawn in local coordinates
    def draw_view_hierarchy(view, offset, rect):
      # save canvas parameters
      canvas.gsave()
      
      # view global rect is its rect translated by the offset
      view_global_rect = view.rect.translate(offset)
      
      # clip the canvas to the view rect
      canvas.rectclip(view_global_rect)
      
      # move the drawing area into the view local system
      context.transform = view_global_rect.origin
      
      # draw the view
      view.draw(rect)
      
      # draw all the subviews
      for v in view.views:
        clipped_rect = rect.clip(v.rect)
        if clipped_rect is not None:
          draw_view_hierarchy(v, offset + view.position, clipped_rect.translate(-v.position))
          
      # restore canvas parameters
      canvas.grestore()
      
    #print "Requested to draw %s" % (rect,)
      
    for view in self.views:
      clipped_rect = rect.clip(view.rect)
      if clipped_rect is not None:
        draw_view_hierarchy(view, (0, 0), clipped_rect.translate(-view.position))
    

# ------ PyGUI components wrappers
import GUI
import GUI.Label, GUI.Window, GUI.View, GUI.ScrollableView 
from GUI import rgb as PyGUI_rgb
import unicodedata
rejected_unicode_categories = frozenset(['Cc','Cf', 'Co', 'Cs', 'Cn', 'Zl', 'Zp'])

_deadkey_map = {"`": u"\u0300", 'u' : u"\u0308", 'e' : u"\u0301", '6': u"\u0302"}

def _extract_modifiers_from_pygui_event(event):
  modifiers = []
  if event.shift:
    modifiers.append('shift')
  if event.control:
    modifiers.append('control')
  if event.option:
    modifiers.append('option')
    
  return frozenset(modifiers)

class GUI_Window(GUI.Window):
  def __init__(self, *args, **kwargs):
    super(GUI_Window, self).__init__(*args, **kwargs)
    self.auto_position = True
    
    # create the toolbar
    self.toolbar = toolbar = GUI_Toolbar()
    
    self.statusbar = statusbar = GUI_StatusBar()
    
    self.scrollview = scrollview = GUI_ScrollableView(extent = (2000, 2000))
    
    self.place(toolbar,  top = 0, left=0, right=0, sticky='new')
    self.place(statusbar, left=0, right=0, bottom=0, sticky='ews')
    self.place(scrollview, top = toolbar, left=0, right=0, bottom=statusbar, sticky='news')
    
    self.__deadkey = None
  
  def subview_resized(self): 
    # make sure that the invariant holds
    if self.scrollview.top != self.toolbar.bottom:
      self.scrollview.top = self.toolbar.bottom
    if self.scrollview.bottom != self.statusbar.top:
      self.scrollview.bottom = self.statusbar.top
        
  def close_cmd(self):
    safecall(self.windowWrapper.controller).windowClosing()
    super(GUI.Window, self).close_cmd()
    if len(GUI.application().windows) == 0:
      Application().quit()
      
  def key_down(self, gui_event):
    # if command key is pressed down, this is a shortcut and we need to forward it to 
    # the normal system
    # if getattr(gui_event, 'command', False) or gui_event.control:
  #     # print getattr(GUI.MessageHandler, gui_event.kind)#
  #     # print getattr(GUI_Window, gui_event.kind)
  #     # return getattr(GUI.MessageHandler, gui_event.kind)(self, gui_event)
  #     print 'passing event to next handler'
  #     self.pass_event_to_next_handler(gui_event)
  #     return
    
    # translate the PyGUI Event into our Event
    if gui_event.kind == 'key_down':
      eventClass = Event.Key.Down
      method     = 'keyDown'
    elif gui_event.kind == 'key_up':
      eventClass = Event.Key.Up
      method     = 'keyUp'
    else:
      return # don't know how to handle this one
      
    # get the key code (need to do some additional translation)
    key = gui_event.key
        
    if gui_event.char != '' and ord(gui_event.char) == 27:
      key = 'esc'
    elif gui_event.char != '' and ord(gui_event.char) == 8:
      key = 'delete'
      
    if unicode(gui_event.unichars) not in ('', 'None')  and unicodedata.category(unicode(gui_event.unichars)) not in rejected_unicode_categories: 
      unicodePoint = gui_event.unichars
    else:
      unicodePoint = None
    
    # translate euro character to schwa
    if unicodePoint == u'€':
      unicodePoint = u'ə'
      
    
    # handle dead keys (if appropriate)    
    if gui_event.option:
      self.__deadkey = _deadkey_map.get(key, None)
    else:
      if self.__deadkey is not None and unicodePoint is not None:
        unicodePoint = unicodedata.normalize('NFC', unicodePoint + self.__deadkey)
      self.__deadkey = None  
    
          
    event = eventClass(key = key, unicodePoint = unicodePoint)
    
    # dispatch it to the first responder
    getattr(self.windowWrapper.firstResponder, method)(event)
    

  key_up = key_down
  
      
    
      

class GUI_ScrollableView(GUI.ScrollableView):
  __mouseoverView = None
  old_viewed_rect = None
  
  def resized(self, (dw, dh)):
    pass
  
  def draw(self, canvas, update_rect):
    # check if the viewed rect has changed
    viewed_rect = self.viewed_rect()
    old_viewed_rect = self.old_viewed_rect
    if old_viewed_rect is None or old_viewed_rect[0] != viewed_rect[0] or old_viewed_rect[1] != viewed_rect[1] or old_viewed_rect[2] != viewed_rect[2] or old_viewed_rect[3] != viewed_rect[3]:
      willChange(self.delegate_view, 'visibleRect', {})
      didChange(self.delegate_view, 'visibleRect', {})
      self.old_viewed_rect = viewed_rect
    
    context = Drawing.Context.fromPyGUICanvas(canvas)
    canvas.rectclip(update_rect)
    with context:
      self.delegate_view.draw(Rect(*update_rect))
      
  def mouse_down(self, gui_event):        
    # translate the PyGUI Event into our Event
    if gui_event.kind == 'mouse_down' and gui_event.button == 'left':
      eventClass = Event.Mouse.Down
      method     = 'mouseDown'
    elif gui_event.kind == 'mouse_down' and gui_event.button == 'right':
      eventClass = Event.Mouse.RightDown
      method     = 'rightMouseDown'
    elif gui_event.kind == 'mouse_up' and gui_event.button == 'left':
      eventClass = Event.Mouse.Up
      method     = 'mouseUp'
    elif gui_event.kind == 'mouse_up' and gui_event.button == 'right':
      eventClass = Event.Mouse.RightUp
      method     = 'rightMouseUp'
    else:
      return # don't know how to handle this one
      

     
    position = Point(*gui_event.position)  
    
    
    # locate the view that is has been clicked
    hit = self.delegate_view.hit(position)
    
    # guard agains no hit
    if hit is None:
      return
      
    # translate the position into the view coordinates
    position = position - hit.globalRect.origin
      
    event = eventClass(position = position, numClicks = gui_event.num_clicks, modifierKeys = _extract_modifiers_from_pygui_event(gui_event))
    getattr(hit, method)(event)
    
  mouse_up = mouse_down
  
  @property
  def mouseoverView(self):
    return self.__mouseoverView
    
  @mouseoverView.setter
  def mouseoverView(self, value):
    # it can't be the scrll view
    if value is self.delegate_view:
      value = None
    
    # guard agains no changes
    if value is self.__mouseoverView:
      return
      
    willChange(self.delegate_view.window, 'mouseoverView',{})
    
    # get all the views that previously were under the mouse
    if self.mouseoverView is not None:
      views_previously_under_mouse = set(self.mouseoverView.superviewChain)
      views_previously_under_mouse.add(self.mouseoverView)
    else:
      views_previously_under_mouse = set()
      
    # get all the views that will be under the mouse now   
    if value is not None:
      views_now_under_mouse = set(value.superviewChain)
      views_now_under_mouse.add(value)
    else:
      views_now_under_mouse = set()
      
      
    # inform all views that used to be under mouse but no more that they are no longer needed
    for view in  views_previously_under_mouse - views_now_under_mouse:
       view.mouseLeftArea(Event.Area.Left(rect = view.globalRect, view = view))
    
    # inform all views were not under mouse but are now
    for view in  views_now_under_mouse - views_previously_under_mouse:
       view.mouseEnteredArea(Event.Area.Entered(rect = view.globalRect, view = view))
      
    self.__mouseoverView = value
    # print "Mouseoverview is now %s" % value
    
    didChange(self.delegate_view.window, 'mouseoverView',{})  
  
  def mouse_move(self, gui_event):
    # get the mouse position
    position = Point(*gui_event.position)
    
    # get the view under the mouse
    # can't be the scroll view (for obvious reasons)
    self.mouseoverView = self.delegate_view.hit(position)
    
  
  mouse_drag = mouse_move
    #
    # if mouseover_view is self.delegate_view:
    #   mouseover_view = None
    #
    # self.m
    #
    # # ok, now we need to send the mouse left event to all the views no longer under the mouse
    # if self.backing_view.window.
    # views_previously_under_mouse = frozenset(superviewChain)
    #
    #
    # print mouseover_view
        
      # # make sure that mouseover view is properly updated
      # self.mouse_move(event)
      #
      # # dispatch the down action on the mouseover view
      # mouseover_view = self.mouseoverView
      # if event.shift:
      #     action = 'action_mouseDownShift'
      # else:
      #     action = 'action_mouseDown'
      #
      # if mouseover_view is not None:
      #     self.dispatchActionForEvent(mouseover_view, action)
      #     self.__mousedownview_ref = self.__mouseoverview_ref
      # else:
      #     self.dispatchAction(action, None)
    
  
class GUI_Panel(GUI.View):
  __bcolor = Drawing.Color(0.8, 0.8, 0.8)
  preferred_height = 32
  
  @property
  def bcolor(self):
    return self.__bcolor
  
  @bcolor.setter
  def bcolor(self, value):
    self.__bcolor = value
    self.invalidate()
  
  def autosize(self):
    if len(self.contents) == 0:
      self.height = self.preferred_height
    else:
      self.shrink_wrap()  
    
  def draw(self, canvas, update_rect):
    canvas.fillcolor =  PyGUI_rgb(*self.bcolor)
    canvas.fill_rect(update_rect)
    
  def resized(self, (dw, dh)):
    getattr(self.container, 'subview_resized', lambda : None)() 
    
  def handle_event(self, event):
    pass
    
  def handle_event_here(self, event):
    if event.kind == 'mouse_down' and event.num_clicks >= 1:
      try:
        self.click()
      except:
        import traceback, sys
        traceback.print_exc()
        sys.exit()
    
  click = Action()
    
    
class GUI_Toolbar(GUI_Panel):
  preferred_height = 0
  
  def __init__(self, *args, **kwargs):
    super(GUI_Toolbar, self).__init__(*args, **kwargs)
    
    self.autosize()

class GUI_StatusBar(GUI_Panel):
  preferred_height = 16

  def __init__(self, *args, **kwargs):
    super(GUI_StatusBar, self).__init__(*args, **kwargs)
    
    self.label = GUI.Label()
    self.label.text = ''
    self.place(self.label, top=4, left=8, sticky = 'nes')
    
    self.autosize()
  
  @property
  def message(self):
    return self.label.text
  
  @message.setter
  def message(self, value):
     self.label.width = self.label.font.width(value) + 8
     self.label.text = value
    
