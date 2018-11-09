##############################################################
# view.py
#
# Definition of the view base class

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



from Toolkit import Drawing
from Toolkit import Display, Rect, Point, Size


import unicodedata, platform, weakref, time

# PyGUI imports
from GUI import ScrollableView, Pixmap
from GUI import rgb as PyGUI_rgb

import logging


# check if we are on OS X, because only then we allow backing views
backing_is_on = (platform.system() == 'Darwin')

# these unicode categories will not generate a char event
rejected_unicode_categories = frozenset(['Cc','Cf', 'Co', 'Cs', 'Cn', 'Zl', 'Zp'])

        

#class NeedImmediateUpdate(Exception): pass

##############################################################
# A Toolkit display implementation as PyGUI ScrollableView class
class ToolkitScrollableView(Display, ScrollableView):
    def __init__(self, *args, **kwargs):
        ScrollableView.__init__(self, *args, **kwargs)
        Display.__init__(self)
        self.background_color = PyGUI_rgb(1, 1, 1)
        
        # the backing cache (only needed if we are on OS_X)
        if backing_is_on:
            self.__backing_cache = weakref.WeakKeyDictionary()
            
        # set up a standard size
        self.extent = (50, 50) 
        
        
        # ---- event handling
        
        # the mouseover view
        self.__mouseoverview_ref = None
        self.__mouseoverviews = weakref.WeakSet()
        
        # the last view where the mouse went down (drag origin view)
        self.__mousedownview_ref = None
        
        # the mouse position
        self.__mousepos = (0, 0)
        
        # is the mouse being dragged?
        self.__mousedragging = False
        
    def contentsViewChanged(self): 
        # reset stuff
        self.__mousedragging = False
        self.__mouseoverview_ref = None
        self.__mouseoverviews = weakref.WeakSet()
        self.__mousedownview_ref = None
    
    @property
    def mouseoverView(self): return None if self.__mouseoverview_ref is None else self.__mouseoverview_ref()    
        
        
    def dirty(self, *rects): 
        if len(rects) == 0:
            self.invalidate()
        else:
            for r in rects:
                self.invalidate_rect(r)
    
    def adaptDisplaySizeToContents(self): 
        x0, y0, x1, y1 = self.contentsView.rect
        w, h = self.extent
            
        if w < x1 + 100 or h != y1 + 100: 
            self.extent = (max(int(x1)+100, self.viewed_rect()[2] - self.viewed_rect()[0]),  int(y1) + 100)
        

    # ++++++++++++++++++ the geometry of the display +++++++++++++++++    
    @property
    def viewOrigin(self):
        return Point(*self.scroll_offset)
    
    @viewOrigin.setter
    def viewOrigin(self, value):
        self.scroll_offset = (int(value[0]), int(value[1]))
    
    @property
    def viewRect(self): 
        w, h = self.extent
        x0, y0, x1, y1 = self.viewed_rect()
        
        return Rect(x0, y0, min(x1, w), min(y1, h))
        
    @property
    def displaySize(self): return Size(*self.extent)   
    
    # ++++++++++++++++++ drawing +++++++++++++++++    
    def draw(self, canvas, update_rect):
        t0 = time.time()
        # erase the update rect
        canvas.erase_rect(update_rect)
        # canvas.pencolor= PyGUI_rgb(1, 0, 0)
        # canvas.stroke_rect(update_rect)
        
        
        #if self.contentsView is None: return
        
        # clip the update rect to the contents rect
        contents_rect = self.rootView.rect
        
        update_rect = (max(update_rect[0], contents_rect[0]), 
                       max(update_rect[1], contents_rect[1]),
                       min(update_rect[2], contents_rect[2]), 
                       min(update_rect[3], contents_rect[3]))
                       
                       
        # create a framework context
        context = ContextFromPyGUICanvas(canvas, (update_rect[0], update_rect[1]))
        
        # cache clipped view rects
        global_position_cache = {self.rootView:(0, 0)}
        clip_rect_cache = {self.rootView:self.rootView.rect}
        
        # draw the views
        # print '------'        
        # print 'invalidating global rect', update_rect
        # 
        views = list(self.hit(Rect(*update_rect)))
        
        # print ' ::: found views',  views
        # 
        
        for view in views:
            # compute the global rect for the view
            v_x0, v_y0, v_x1, v_y1 = view.rect
            s_x0, s_y0 = global_position_cache[view.superview]
            
            global_rect = (v_x0 + s_x0, v_y0 + s_y0, v_x1 + s_x0, v_y1 + s_y0)
            global_position_cache[view] = (global_rect[0], global_rect[1])
            
            # and now compute the clipped rect
            s_x0, s_y0, s_x1, s_y1 = clip_rect_cache[view.superview]
            cliprect = clip_rect_cache[view] = (max(s_x0, global_rect[0]), max(s_y0, global_rect[1]), min(s_x1, global_rect[2]), min(s_y1, global_rect[3]))
            
            if cliprect[2]<=cliprect[0] or cliprect[3]<=cliprect[1]:
                continue
            
            # clip the context to the rect
            canvas.gsave()
            #canvas.rectclip((cliprect[0]-1, cliprect[1]-1, cliprect[2]+1, cliprect[3]+1))
            canvas.rectclip(cliprect)
            
            # offset the context coordinates to match the view origin            
            context.canvas_offset = Point(global_rect[0], global_rect[1])
            
            # compute the local update rect
            local_update_rect = Rect(cliprect[0] - global_rect[0], cliprect[1] - global_rect[1], cliprect[2] - global_rect[0], cliprect[3] - global_rect[1])
            
            
            # draw the view
            with context:
                # try: 
                #     print 'drawing view', view
                #     print 'cliprect=', cliprect
                #     print 'global_rect=', global_rect
                #     print 'local_update_rect=', global_rect
                #     print 'update_rect=', update_rect
                # except: pass    
                view.draw(local_update_rect)
            
            # restore the context
            canvas.grestore()
            
        #logging.info('drawing in %s took %s (%s views drawn)', update_rect, time.time() - t0, len(views))    
            
            
    # ++++++++++++++++++ event handling +++++++++++++++++   
    @property
    def mouseDragged(self): return self.__mousedragging
    
    @property
    def mousePos(self): return self.__mousepos
    
    @property
    def mouseoverView(self): 
        if self.__mouseoverview_ref is None:
            return None
        else:
            return self.__mouseoverview_ref()
            
    @property
    def viewsUnderMouse(self):
        return tuple(self.__mouseoverviews)        
    
    def mousePosInView(self, view):
        return self.mousePos - view.globalPosition
    
     
    def mouse_move(self, event): 
        self.__mousepos = Point(event.position[0], event.position[1])
        
        if self.contentsView is None: 
            self.__mouseoverview_ref = None
            return
        
        # # get the old mouseover view
        old_mouseover_view = self.__mouseoverview_ref() if self.__mouseoverview_ref is not None else None
        
        
        # get the new mouseover view (its the last one in the hitlist)
        mouse_rect = Rect(event.position[0], event.position[1], event.position[0] +1, event.position[1] + 1)    
        mouseoverviews = self.hit(mouse_rect)
        new_mouseover_view = mouseoverviews[-1] if len(mouseoverviews)>0 else None
        mouseoverviews = set(mouseoverviews)
        
        # notify the views which have the mouse left the area
        for view in set(self.__mouseoverviews) - mouseoverviews:
            self.dispatchActionForEvent(view, 'action_mouseLeave')
            #view.mouseLeftArea()
        
        # notify the views which are now under the mouse    
        for view in mouseoverviews - set(self.__mouseoverviews):
            self.dispatchActionForEvent(view, 'action_mouseEnter')
            
            view.mouseEnteredArea()
            
        self.__mouseoverviews = weakref.WeakSet(mouseoverviews)    
            
        
        # no change here, so nothing to do
        if new_mouseover_view is old_mouseover_view: return
        
        # set the new mouseover view
        if  new_mouseover_view is not None:           
            self.__mouseoverview_ref = weakref.ref(new_mouseover_view)    
        else:
            self.__mouseoverview_ref = None

        
        # did the mouse leave the old view?
        if old_mouseover_view is not None:
            self.dispatchActionForEvent(old_mouseover_view, 'action_mouseHoverEnd')
        
        # did the mouse enter the new view?
        if new_mouseover_view is not None:
            self.dispatchActionForEvent(new_mouseover_view, 'action_mouseHoverBegin')
            # and save it    
            
    
    def mouse_down(self, event):        
        # make sure that mouseover view is properly updated
        self.mouse_move(event)
        
        # dispatch the down action on the mouseover view
        mouseover_view = self.mouseoverView
        if event.shift:
            action = 'action_mouseDownShift'
        else:
            action = 'action_mouseDown'
        
        if mouseover_view is not None:
            self.dispatchActionForEvent(mouseover_view, action)
            self.__mousedownview_ref = self.__mouseoverview_ref
        else:
            self.dispatchAction(action, None)

    def mouse_up(self, event):        
        # make sure that mouseover view is properly updated
        self.mouse_move(event)
        
        
        # dispatch the mouse up action on the mouseover view
        mouseover_view = self.mouseoverView
        if mouseover_view is not None:
            self.dispatchActionForEvent(mouseover_view, 'action_mouseUp')
            # if its the same view where the mouse was pressed, then we have a click
            if self.__mousedownview_ref is not None and self.__mousedownview_ref() is mouseover_view:
                #print 'dispatching click for', mouseover_view
                self.dispatchActionForEvent(mouseover_view, 'action_mouseClick')
            self.__mousedownview_ref = None
            if self.__mousedragging:
                self.__mousedragging = False
                self.dispatchAction('finishedDragging', None)
                
            
            
    def mouse_drag(self, event):
        if not self.__mousedragging: 
            self.__mousedragging = True
            self.dispatchAction('startedDragging', None)
        
        # we do not make distinction between dragging and moving here
        self.mouse_move(event)
        
        
    def key_down(self, event):
        key = event.key
        
        if event.char != '' and ord(event.char) == 27:
            key = 'esc'
        elif event.char != '' and ord(event.char) == 8:
            key = 'delete'
        
        self.__mousepos = Point(*self.global_to_local(event.global_position))        

        # dispatch a key down event
        self.dispatchAction('keyDown', None, key = key)
        
        # dispatch a char event
        if unicode(event.unichars) != '' and unicodedata.category(unicode(event.unichars)) not in rejected_unicode_categories: 
            self.dispatchAction('charInput', None, char = unicode(event.unichars))
        

    def key_up(self, event):
        key = event.key

        if event.char != '' and ord(event.char) == 27:
            key = 'esc'
        elif event.char != '' and ord(event.char) == 8:
            key = 'delete'
        
        self.__mousepos = Point(*self.global_to_local(event.global_position))        

        # dispatch a key up event
        self.dispatchAction('keyUp', None, key = key)
