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



from observing import *
from UIToolkit.Drawing import *
from UIToolkit import View, PresentationProperty, Action, PresentationStateDelegate, Tasklet
from collections import namedtuple
from UIToolkit.Animation import Animator
from SafeCall import safecall


__all__ = ('EditorView', 'EditController', 'EditorOperationError')

# Ok, lets try it with this kind of model
#
# An editor view is exposed to an array of rectangular cells which hold content (could be pictures or other shit)
# Every letter is such a thing for example. But what about optimisation? Well, we can also say that we can go INTO
# the cells. The cells are then linked to a value via some sort of transformers. This can be done by a controller which 
# observes changes in both the data and the cells. Ok, so lets do that. A single editor view then manages these
# multiple cells. Is a cell a view? It almost must be, but we don't really want all the overhead. 
# No, its not a view! But we can copy parts of views functionality

# Notes: 
#  2. Editor cells can't overlap! 
#  3. Editor cells are organised in a stict linear order
#     It is then the job of the owner to position them properly
#  4. Editor draws the cursor, the cell only tells where to draw the cursor (is it so? shouldn't the cursor be drawn by the cell?)
#  5. A cell consists of glyphs - glyphs are basically what is individually navigable
#  6. Would be nice to have support for glyph or even cell shadowing, e.g. how would the cell look if it were changed (but its not actually being changed!) Maybe the editor can do that somehow. Can figure it out later

# I need to rethink it... yet again
#
# Ok, I will simplify it. Every cell is represented as text when edited. Better? Cell is still responsible
# for drawing itself. Yes, that is MUCH better. So basically skip the concept of glyphs. Cell will also track its
# own cursor position. Or do we want to leave this to the editor? How would that be managed? 
#
# Actually, it makes sense to leave glyphs intact. Let's leave glyphs intact. 

# Editor manages a list of cells, which the editor can place and order as appropriate
# The cells consist of glyphs, where a glyph is a minimal unit of edit. 
# Text editing is therefore performed at glyph level. An edit operation inserts of deletes at least one glyph.
# The cell is free to change its glyph structure whether its edited or not. Even more, 
# It does not make any sense to talk about glyphs is the cell is not being edited!
# 
#
# How can we deal all this complexity? Especially, how do we know when to add new stuff to cells and when not?
# Ok, so let us think about it
#
# At first, the editor is not in edit mode and no cells are being edited
# If we activate an editor it attempts to find a cell to be edited. If no such cell can be found (e.g.
# cells at the cursor do not want to be edited), the cursor is placed between cells. Otherwise, the
# cell starts being edited and a corresponding message is issued. 

# so basically, the editor needs to juggle between editing cells and editing in between the cells
# The controller is responsible for creating new cells if appropriate. Yes! That is exactl how it will be. 




class EditorOperationError(Exception): pass

# ----- edit controllers

class EditController(object):
  @property
  def value(self):
    """ Return the current text to be displayed in the editor """
    pass
    
  def insertTextAtPosition(self, text, position):
    """ Inserts the text at the given position and returns the at of the last modified character """  
    pass
    
  def deleteTextAtPosition(self, position):
    """ Removes the text at the given position and returns the offset of the last unmodified character """
    pass
    
  def replaceWith(self, contents):
    """ Replace the entire value with the given contents """
    pass
    
  def endEdit(self):
    """ Notify the controller that the edit has finished """
    
    
class StrEditController(EditController):
  def __init__(self, editView):
    self.editor = editView
    self.value = self.editor.value
    if self.value is None:
      self.value = ''
    
  @property 
  def value(self):
    return self.__value
    
  @value.setter
  def value(self, v):
    self.__value = v
    
  def insertTextAtPosition(self, text, position):
    if position < 0  or position > len(self.value):
      raise EditorOperationError("Insert position escapes the string")
      
    p0 = self.value[0:position]
    p1 = self.value[position:len(self.value)]  
    text = unicode(text)
    
    self.value = p0 + text + p1
    
    return len(p0 + text)
        
  def deleteTextAtPosition(self, position):
    if position < 0  or position > len(self.value):
      raise EditorOperationError("Delete position escapes the string")
      
    if position == 0:
      return 0
    
    p0 = self.value[0:(position-1)]  
    p1 = self.value[position:len(self.value)]  
    
    self.value = p0 + p1
      
    return position - 1  
    
  def endEditing(self):
    pass
    

class EditorPresentationStateDelegate(PresentationStateDelegate):
  textcolor  = PresentationProperty(Color, 'black')
  placeholdercolor = PresentationProperty(Color, 'gray')
  bcolor = PresentationProperty(Color, 'white')
  fcolor = PresentationProperty(Color, 'black')
  fwidth = PresentationProperty(int, 1)
  cursorVisible = PresentationProperty(bool, True)
  
  
  def __init__(self, *args, **kwargs):
    super(EditorPresentationStateDelegate, self).__init__(*args, **kwargs)
    self.animator = None 
    self.__cursorTask = None
  
  def __flipCursor(self, tasklet):
    #pass
    #print "-----------------------------------------"
    self.cursorVisible = not self.cursorVisible  
  
  def startEdit(self):
    # ignore if an animation is ongoing
    if self.animator is not None and self.animator.running:
      return
    
    self.__cursorTask = Tasklet(self.__flipCursor, 0.5).shedule()
    self.animator = Animator(self, duration=0.15)
    self.animator.fcolor = Color('cadetblue2')
    self.animator.fwidth = 3


  def endEdit(self):
    # ignore if an animation is ongoing
    if self.animator is not None and self.animator.running:
      return

    self.__cursorTask.complete()
    self.__cursorTask = None
    self.cursorVisible = True 
    self.animator = Animator(self, duration=0.15)
    self.animator.fcolor = Color('black')
    self.animator.fwidth = 1
    
  def error(self):
    if self.animator.running:
      self.animator.complete()
    
    self.animator = Animator(self, repeat=2, reset_value=True, duration= 0.25)
    self.animator.bcolor = Color('red')
      
      
    
  # def drawFrameAndBackground(self, rect):
  #   self.bcolor.makeFillcolor()
  #   self.fcolor.makeDrawcolor()
  #   thickness = self.fwidth
  #
  #   if self.editing:
  #     frameoffset = 0
  #   else:
      
    
    
    
    

class EditorView(View):  
  def __init__(self, *args, **kwargs):
    self.__editController = None
    self.__cursor = None
    self.__value = ''
    View.__init__(self, *args, **kwargs)
          
  # ----  presentation attributes
  presentationDelegateClass = EditorPresentationStateDelegate
  
  font     = PresentationProperty(Font.makeFont, Font.defaultFont)
  color    = PresentationProperty(Color, 'black')
  placeholderValue = PresentationProperty(unicode, "enter text here")  
  minWidth         = PresentationProperty(int, 120)  
  margins          = PresentationProperty(namedtuple('Margins', ('left', 'right', 'top', 'bottom'))._make, (10, 10, 5, 5))
  fstyle           = PresentationProperty(str, 'rounded')
          
  # ----  drawing
  @property
  def presentationDelegate(self):
    try:
      return self.__presentationDelegate
    except AttributeError:
      self.__presentationDelegate = self.presentationDelegateClass(self)
    
    return self.__presentationDelegate
  
  @View.presentationState.changed
  def presentationState(self, context):
    """ Recompute the size """
    font = Font.defaultFont
    left, right, top, bottom = self.margins
    self.size = (max(self.minWidth, font.getWidthForString(self.value) + left + right), font.ascent + font.descent + top + bottom)
    
    self.dirty()
    
  def draw(self, rect): 
    super(EditorView, self).draw(rect)
    w, h = self.size
    font = self.font
    
    
    # draw the frame
    self.presentationDelegate.fcolor.makeDrawcolor()
    self.presentationDelegate.bcolor.makeFillcolor()
    if self.fstyle == 'rounded':
      frame = Path.initWithRoundedRect(0, 0, *self.size, roundness=0.2)
    else:
      frame = Path.initWithRect(0, 0, *self.size)
      
    frame.thickness = self.presentationDelegate.fwidth
    
    if self.fstyle != 'none':
      frame.fillAndStroke()
    else:
      frame.fill()

    # compute the text position
    x = self.margins.left
    y = h - self.margins.bottom - font.descent
    
    # draw the text    
    font.makeCurrent()
    
    
    if self.showingPlaceholder:
      value = self.placeholderValue
      self.presentationDelegate.placeholdercolor.makeDrawcolor()
      if not self.editing:
        x = max((w - font.getWidthForString(value))/2, x)
    else:
      value = self.value
      if value is None:
        value = u''
      if self.editing:
        self.presentationDelegate.textcolor.makeDrawcolor()
      else:
        self.color.makeDrawcolor()
          
    Context.drawTextAtPosition(value, Point(x, y))    
    
    # draw the cursor
    if self.editing and self.presentationDelegate.cursorVisible:
      Color('black').makeDrawcolor()
      cursor_x = font.getWidthForString(value[0:self.cursorPosition])
      x = x + cursor_x
      Path().moveTo(x, 2).lineTo(x, h - 2).stroke()
    
    
  
  # ---- value 
  @observable_property
  def value(self):
    if self.__editController is not None:
      return self.__editController.value
    else:
      return self.__value
      
  @value.setter
  def value(self, new):
    willChange(self, 'presentationState', {})
    self.__value = new
    didChange(self, 'presentationState', {})
    self.dirty()
    
  @property
  def showingPlaceholder(self):
    return self.value is None or len(self.value.strip()) == 0 
   
  # ----- editing support  
  @observable_property
  def editing(self):
    return self.__editController is not None
  
  # ----- cursor support
  @property
  def cursorPosition(self):
    return self.__cursor
    
  def moveCursorToStart(self):
    p = self.cursorPosition
    if p is None:
      return

    self.__cursor = 0
    self.dirty()
  
  def moveCursorToEnd(self):
    p = self.cursorPosition
    if p is None:
      return

    self.__cursor = len(self.value)
    self.dirty()
    
  def moveCursorLeft(self):
    p = self.cursorPosition
    if p is None:
      return
    
    # guard agains being on the left
    if p == 0:
      safecall(self.__editController).cursorMovedBeforeText()
      return
      
    # try to find the next grapheme
    # we do it by moving backwards until the string width changes
    font = Font.defaultFont
    value = self.value[0:p]
    x = font.getWidthForString(value)  
    p = p - 1
    while font.getWidthForString(value[0:p]) == x:
      p = p - 1
    
    self.__cursor = p
    self.dirty()
    
  def moveCursorToPoint(self, (x, y)):
    p = self.cursorPosition
    if p is None:
      return

    value = self.value
    font = Font.defaultFont
    
    # find the last grapheme that ends before x
    p = 0
    while font.getWidthForString(value[0:(p+1)]) + self.margins.left < x and p < len(value):
      p = p + 1
          
    self.__cursor = p
    self.dirty()
    
    
  def moveCursorRight(self):
    p = self.cursorPosition
    if p is None:
      return
    
    # guard agains being on the left
    if p == len(self.value):
      safecall(self.__editController).cursorMovedAfterText()
      return
      
    # try to find the next grapheme
    # we do it by moving backwards until the string width changes
    font = Font.defaultFont
    value = self.value[0:p]
    x = font.getWidthForString(value)  
    p = p + 1
    while font.getWidthForString(value[0:p]) == x and p < len(value):
      p = p + 1
    
    self.__cursor = p  
    self.dirty()
    
  def moveCursorToCharacterAtPos(self, characterIndex):
    p = self.cursorPosition
    if p is None:
      return
    
    font = Font.defaultFont
    value = self.value
    
    # how long is the string up to that character
    w = font.getWidthForString(value[0:characterIndex])
    
    # now find the cursor position that would still satisfy that
    p = 0
    while font.getWidthForString(value[0:p]) != w and p < len(value): 
     p = p + 1
     
    self.__cursor = p
    self.dirty()
    
    
    
  # ----- event processing
  clickAction = Action('setFirstResponder')
  
  def mouseDown(self, event):
    self.clickAction()
    
    self.moveCursorToPoint(event.position)
  
  @property
  def canBecomeFirstResponder(self):
    return True
  
  def becameFirstResponder(self):
    self.__cursor = 0
    editController = safecall(self.controller).startEditAndGetEditControllerForView(self)
    if editController is None:
      editController = StrEditController(self)
      
    self.__editController = editController
    self.presentationDelegate.startEdit()
    
    
  def yieldedFirstResponder(self):    
    # stop editing and take over the new value
    safecall(self.__editController).endEdit()
    self.__value = self.__editController.value
    # reset the editing state
    self.__editController = None
    self.__cursor = None
    self.presentationDelegate.endEdit()
    
  def operationError(self):
    self.presentationDelegate.error()

  def keyDown(self, event):
    # let the controller handle this
    if safecall(self.__editController).keyEvent(event) == True:
      return
        
    # move cursor to the left
    if event.key == 'left_arrow':
      self.moveCursorLeft()
    # move the cursor to the right  
    elif event.key == 'right_arrow':
      self.moveCursorRight()
    # delete text
    elif event.key == 'delete':
      willChange(self, 'presentationState', {})
      self.moveCursorToCharacterAtPos(self.__editController.deleteTextAtPosition(self.cursorPosition))
      didChange(self, 'presentationState', {})
    elif event.key in ('enter', 'return', 'esc'):
      # resign the first responder status
      self.window.firstResponder = self.superview
    # insert text  
    elif event.unicodePoint is not None:
      willChange(self, 'presentationState', {})
      try:
        self.moveCursorToCharacterAtPos(self.__editController.insertTextAtPosition(event.unicodePoint, self.cursorPosition))
      except EditorOperationError:
        self.operationError()
      
      didChange(self, 'presentationState', {})

      
      
  

# class EditorCell(object):
#   def __init__(self, editor):
#     self.__editor = editor
#     self.__rect = Rect(0, 0, *self.computeSize())
#     self.editor.cellNeedsLayout(self)
#
#   # ---- owner (editor)
#   @property
#   def editor(self):
#     return self.__editor
#
#   # ---- rect and visual hierarchy
#   def computeSize(self):
#     """ computes the size of the cell, should be overriden by the ancestors"""
#     value = 'Cell'
#     font = Font.defaultFont
#     return (font.getWidthForString(value), font.ascent + font.descent)
#
#   @property
#   def rect(self):
#     return self.__rect
#
#   @property
#   def size(self):
#     return self.rect.size
#
#   @property
#   def position(self):
#     return self.rect.origin
#
#   @position.setter
#   def position(self, (x, y)):
#     w, h = self.size
#     rect = Rect(x, y, x+w, y+h)
#     if rect == self.__rect:
#       return
#
#     self.editor.dirty(self.rect)
#     willChange(self, 'presentationState', {})
#     self.__rect = Rect(x, y, x+w, y+h)
#     didChange(self, 'presentationState', {})
#     self.editor.dirty(self.rect)
#
#
#   # ---- drawing
#   presentationState = ObservableState()
#
#   @presentationState.changed
#   def presentationState(self, context):
#     w, h = self.computeSize()
#     x, y = self.rect.origin
#     rect = Rect(x, y, x+w, y+h)
#
#     if rect != self.rect:
#       self.__rect = Rect(x, y, x+w, y+h)
#       self.editor.cellNeedsLayout()
#
#
#   def dirty(self, *rects):
#     if len(rects) == 0:
#         self.editor.dirty(self.rect)
#     else:
#         rect_in_editor = self.rect
#         # translate and clip to the visible rect in the superview's coordinates
#         rects = [r for r in (r.translate(rect_in_editor.origin).clip(rect_in_editor) for r in rects) if r is not None]
#         # send it to the editor, if appropriate
#         if len(rects) > 0:
#             self.editor.dirty(*rects)
#
#   def draw(self, rect):
#     print self.rect
#
#     font = Font.defaultFont
#     value = 'Cell'
#
#     Color('teal').makeFillcolor()
#     #path = Path.initWithRoundedRect(*self.rect, roundness=0.3)
#     Path.initWithRect(*self.rect).stroke()
#
#     font.makeCurrent()
#     Color('white').makeDrawcolor()
#     Context.drawTextAtPosition(value, Point(self.rect.x0, self.rect.y1))
#
#
#   # ---- managing glyphs
#   @observable_property
#   def glyphCount(self):
#     return 1
#
#   def getGlyphAtPoint(self, (x, y)):
#     if Point(x,y) in self.rect:
#       return 0
#     else:
#       return 0
#
#   def getRectForGlyph(self, glyph):
#     if glyph == 0:
#       return self.rect
#     else:
#       return None
#
#   # ---- editing interface — this is what the editor view uses to navigate this thing
#   @observable_property
#   def editable(self):
#     """ Is it possible to edit the contents of this cell? Or is it monolitic? Example: images — can't edit it!"""
#     return False
#
#   @observable_property
#   def editing(self):
#     """ Set by the editor to indicate that the cell is currently being edited. The cell can react for instance by changing the way it is drawn """
#     return self.__editing
#
#   def startEdit(self):
#     """ Called by editor to tell the cell that it is starting to be edited """
#     if (not self.editable) or self.editing:
#       raise EditorOperationError()
#     self.__editing = True
#
#   def endEdit(self):
#     """ Called by editor to tell the cell that it is ends being edited """
#     if not self.editing:
#       raise EditorOperationError()
#
#     self.__editing = False
#
#   def canAppendTextAtFront(self, text):
#     """ Return true if the cell can add content at its start """
#     return False
#
#   def appendTextAtStart(self, text):
#     """ Add new glyphs at the start and return the index of the last modified glyph """
#     raise EditorOperationError()
#
#   def canAppendTextAtEnd(self, text):
#     """ Return true if the cell can add content at its end """
#     return False
#
#   def appendTextAtEnd(self, text):
#     """ Add new glyphs at the end and return the index of the last modified glyph """
#     raise EditorOperationError()
#
#   def insertTextAtGlyph(self, text, glyph):
#     """ Insert text at the glyph position and return the index of the last modified glyph """
#     raise EditorOperationError()
#
#   def deleteContentAtGlyph(self, glyph):
#     """ Delete the content at the glyph position and return the index of the glyph that will now occupy that position """
#     raise EditorOperationError()
#
#   def replaceCellContentsBy(self, contents):
#     raise EditorOperationError()
#
#
# CursorPos = namedtuple('CursorPos', ('cell', 'glyph'))
# class EditorView(View):
#     def __init__(self, *args, **kwargs):
#       super(EditorView, self).__init__(*args, **kwargs)
#
#       self.__cursorPos = CursorPos(0,0)
#       self.__editing = False
#       self.__cells = None
#       self.__cells = [EditorCell(self), EditorCell(self), EditorCell(self)]
#       self.cellNeedsLayout(self.__cells[0])
#
#
#     # ---- cell layout
#     def cellNeedsLayout(self, cell):
#       if self.__cells is None:
#         return
#
#       # find the new height
#       h = max(self.size.height, cell.size.height + 10)
#
#       # layout the cell and all the following cells (we use simple linear layout for this)
#       cell_index = self.cells.index(cell)
#       if cell_index == 0:
#         x = 0
#       else:
#         x = self.cells[cell_index-1].rect.x1
#
#       # adjust the position to make the cell visually distant
#       x += 8
#
#       for cell_index in xrange(cell_index, len(self.cells)):
#           self.cells[cell_index].position = (x, 0)
#           x = self.cells[cell_index].rect.x1 + 8
#
#       self.size = (x+8, h)
#
#     def draw(self, rect):
#       Color('black').makeDrawcolor()
#       Path.initWithRect(0, 0, *self.size).stroke()
#
#
#       for cell in self.cells:
#         clipped_rect = rect.clip(cell.rect)
#         if clipped_rect is not None:
#           cell.draw(clipped_rect.translate(-cell.position))
#
#
#
#     # ---- cells
#     @property
#     def cells(self):
#       return self.__cells
#
#     # # ---- editing interface
#     # @property
#     # def editing(self):
#     #   return self.__editing
#     #
#     # @property
#     # def editedCell(self):
#     #   if self.__cursorPos is not None:
#     #     return self.cells[self.__cursorPos[0]]
#
#     # ---- managing cursor
#     # @observable_property
#  #    def cursorPos(self):
#  #      return __cursorPos
#  #
#  #    @cursorPos.setter
#  #    def cursorPos(self, (cell, glyph)):
#  #      # check whether the cell position is ok
#  #      if cell < 0 or cell >= len(self.cells):
#  #        raise EditorOperationError('Invalid cell position')
#  #
#  #      # check whether the glyph position is ok
#  #      if glyph < 0 or glyph >= self.cells[cell].glyphCount:
#  #        raise EditorOperationError('Invalid glyph position')
#  #
#  #      oldcell = self.cursorPos.cell
#  #
#  #      if oldcell != cell:
#  #        willChange(self, 'cellUnderCursor', {})
#  #      self.__cursorPos = CursorPos(cell, glyph)
#  #      if oldcell != self.cursorPos.cell:
#  #        didChange(self, 'cellUnderCursor', {})
#  #        self.dirty(self.cells[oldcell])
#  #
#  #      self.dirty(cell)
#  #
#  #    @property
#  #    def cursorAtStart(self):
#  #      return self.cursorPos == (0, 0)
#  #
#  #    @property
#  #    def cursorAtEnd(self):
#  #      lastcell  = len(self.cells)-1
#  #      lastglyph = self.cells[lastcell].glyphCount-1
#  #
#  #      return self.cursorPos == (lastcell, lastglyph)
#  #
#  #
#  #    def moveCursorLeft(self):
#  #      if self.cursorAtStart:
#  #        return
#  #
#  #      cell, glyph = self.cursorPos
#  #
#  #      # we are already at the first glyph, so we need to move to the previous cell
#  #      if glyph == 0:
#  #        new_cell = cell-1
#  #        new_glyph = self.cells[new_cell].glyphCount-1
#  #        self.cursorPos = (new_cell, new_glyph)
#  #      # else we move within the cell
#  #      else:
#  #        self.cursorPos = (cell, glyph-1)
#  #
#  #    def moveCursorRight(self):
#  #      if self.cursorAtEnd:
#  #        return
#  #
#  #      cell, glyph = self.cursorPos
#  #
#  #      # we are already at the last glyph, so we need to move to the previous cell
#  #      if glyph == self.cells[cell].glyphCount-1:
#  #        self.cursorPos = (cell + 1, 0)
#  #      # else we move within the cell
#  #      else:
#  #        self.cursorPos = (cell, glyph-1)
#  #
#  #    def setCursorAtPoint(self, (x, y)):
#  #      """ Sets the cursor to the clicked location"""
#  #      pass
#  #
#  #    @property
#  #    def cellUnderCursor(self):
#  #      return self.cells[self.cursorPos.cell]
#  #
#
#
#
#
