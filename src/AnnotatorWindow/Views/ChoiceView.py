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
from AnnotatorWindow import PresentationSettings
import Behaviors


choiceFont = Drawing.Font(Drawing.Font.defaultFont.familyname, int(Drawing.Font.defaultFont.size*0.8), ['bold'])

class ChoiceLabel(UI.Label):
  color    = PresentationProperty(Drawing.Color, 'white')
  font     = PresentationProperty(Drawing.Font.makeFont, choiceFont)
  
  choiceAction = Action(None)
  

  highlighted  = PresentationProperty(bool, False)
  
  @View.presentationState.changed
  def presentationState(self, context):
    if self.highlighted:
      self.color = 'dodgerblue'
    else:
      self.color = ChoiceLabel.color.default
    
    UI.Label.presentationState.__changed__(self, context)

  @property
  def highlightable(self):
    return True
      
  # ------ event handling
  def mouseDown(self, event):
    self.choiceAction()

class ChoiceView(UI.OverlayView):
  fcolor          = PresentationProperty(Drawing.Color, 'slategray')
  bcolor          = PresentationProperty(Drawing.Color, Drawing.Color('gray', alpha=0.9))
  margin          = PresentationProperty(int, 5)
  itemsPerLine    = PresentationProperty(int, 5, triggersLayout = True)

  # ----- action
  cancelAction = Action(None)
  deleteAction = Action(None)

  # ----- action
  @observable_property
  def hotkeysEnabled(self):
    try:
      return self.__hotkeysEnabled
    except:
      return True
      
  @hotkeysEnabled.setter
  def hotkeysEnabled(self, value):
    self.__hotkeysEnabled = value
    self.__recreateSubviews()
  
  
  @observable_property
  def choices(self):
    try:
      return tuple(self.__choices)
    except:
      return ()
      
  @choices.setter
  def choices(self, value):
    self.__choices = value
    self.__recreateSubviews()

  def __recreateSubviews(self):
    for view in self.views:
      view.superview = None
    
    # recreate the views
    hotkeysEnabled = self.hotkeysEnabled and len(self.choices)<=10
    for i, choice in enumerate(self.choices):
      if hotkeysEnabled:
        label = u"%s %s" % (i+1 if i <10 else 0, choice)
      else:
        label = choice
    
      view = ChoiceLabel(value = label, superview = self, controller = self.controller)
      view.choice = choice
    
    self.needsLayout = True
    self.dirty()

  # ----- responding
  @property
  def canBecomeFirstResponder(self):
    return True
    
  def keyDown(self, event):
    if event.key in ('enter', 'return', 'esc'):
      self.cancelAction()
    elif event.key == 'delete':
      self.deleteAction()
    else:
      choice = self.getChoiceForHotkey(event.key)
      if choice is not None:
        self.getViewForChoice(choice).choiceAction()
    
  def getChoiceForHotkey(self, hotkey):
    if hotkey not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
      return None
      
    # transform the hotkey into index  
    index = int(hotkey)
    if index == 0: index = 10
    index = index -1
    
    if index >= len(self.choices):
      return None
      
    return self.choices[index]
  
  # ----- view to choice mapping
  def getViewForChoice(self, choice):
    for view in self.views:
      if view.choice == choice:
        return view
      
    return None
      
  # ----- layout
  performsLayout = True
  
  def computeLayout(self):
    """ Arrange the views """    
    views = tuple(self.views)
    if len(views) == 0:
      self.needsLayout = False
      return
    
      
    # split the view list into sublists of size itemsPerLine
    viewsPerLine = [views[i:(i+self.itemsPerLine)] for i in range(0, len(views), self.itemsPerLine)]
    
    # print('---')
    # print(viewsPerLine)
    
    # compute the width of every column
    columns = [[v for v in (vs[i] for vs in viewsPerLine if len(vs)>i)] for i in range(min(len(views), self.itemsPerLine))]
    columnWidth = [max(v.size.width for v in vs) for vs in columns]
    
    # compute the heights of every row
    rowHeights  = [max(v.size.height for v in vs) for vs in viewsPerLine]
    
    # arrange the views
    x = self.margin
    y = self.margin
    w = 0
    for row_i, views in enumerate(viewsPerLine):
      for col_i, view in enumerate(views):
        view.position = (x, y)
        x = x + columnWidth[col_i]
      
      w = max(w, x+self.margin)
      y = y + rowHeights[row_i]
      x = self.margin
      
    self.size = (w, y+self.margin)
  
    # layout is done, trigger redraw
    self.needsLayout = False
    self.dirty()
    
      
  # ----- drawing
  def draw(self, rect):
    frame = Drawing.Path.initWithRoundedRect(0, 0, *self.size, roundness=0.2)
    
    if self.bcolor is not None:
      self.bcolor.makeFillcolor()
      frame.fill()
    
    if self.fcolor is not None:
      self.fcolor.makeDrawcolor()
      frame.stroke()
      
      
      
  
    
    