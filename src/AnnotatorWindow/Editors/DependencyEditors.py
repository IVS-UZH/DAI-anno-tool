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
from AnnotatorWindow.Views import *


class DependencyRelationEditor(Responder):
  """ A controller responsible for editing a dependency relation """
  
  def __init__(self, dependencyController, member):
    # init the basic variables
    self.dependencyController = dependencyController
    self.dependency           = self.dependencyController.representedObject   
    self.window               = self.dependencyController.view.window
    self.member               = member
    
    
  # ----- responder hierarchy and activation  
  @property
  def nextResponder(self):
    # next responder is window
    return self.window
  
  @property
  def canBecomeFirstResponder(self):
    return True
  
  def becameFirstResponder(self):
    # we start editing
    # first of all, clear all the selection etc. state
    self.window.controller.selectedView   = self.dependencyController.view
    self.window.controller.highlightedView = None
    self.dependencyController.view.segmentsSelected = True
    self.dependencyController.view.segmentsFocused = True
    
    # create a transaction (if needed)
    if self.dependency.__db__.activeTransaction is not None:
      self.transaction = self.dependency.__db__.activeTransaction
    else:
      self.transaction = self.dependency.__db__.transaction()
    
    # save the original value of the dependency thing
    self.originalValue = getattr(self.dependency, self.member)
    
    # observe the hovered item
    observers(self.window.controller, 'primaryHighlightedView').after += self.highlightedItemChanged
    
    
    
      
  def yieldedFirstResponder(self):
    # delete the transaction object
    self.transaction = None
    self.originalValue = None    
    
    # clear the editor property
    self.dependencyController.editor = None
    
    
    # remove highlighting on the dependency view
    self.window.controller.selectedView    = None
    self.window.controller.highlightedView = None
    self.dependencyController.view.segmentsSelected = False
    self.dependencyController.view.segmentsFocused = False
    
    
    
    observers(self.window.controller, 'primaryHighlightedView').after -= self.highlightedItemChanged
    
  # ----- edit logic
  def commit(self):
    self.transaction.commit()
    # resign the first responder status
    self.window.firstResponder = None
  
  def cancel(self):
    self.transaction.abort()
    # resign the first responder status
    self.window.firstResponder = None
    
  def isValidTarget(self, view):
    try:
      return (view.controller.representedObject.span is self.dependency.span) and\
             (isinstance(view, TokenView) or isinstance(view, ConstituentView))
    except AttributeError:
      return False         
             
    
  # ---- highlighting support override  
  viewCanBeHighlighted = isValidTarget
  
  def viewCanBeSelected(self, view):
    return view is self.dependencyController.view or self.isValidTarget(view)

        
  # ----- event handling    
  def viewSelected(self, view):
    """ Catches the view selection message """    
    if not self.isValidTarget(view):
      view = None    
    
    if view is not None:
      assert(self.isValidTarget(view))
      with self.transaction:
        setattr(self.dependency, self.member, view.controller.representedObject)
      self.commit()
      
  
  def highlightedItemChanged(self, obj, context):
    """ Catches the however view message """   
    view = self.window.controller.primaryHighlightedView
    
    if not self.isValidTarget(view):
      view = None
    
    if view is not None:
      with self.transaction:
        setattr(self.dependency, self.member, view.controller.representedObject)
      
  
  def editableActivated(self, sender):
    pass
  

  def keyDown(self, event):
    if event.key in ('enter', 'return'):
      self.commit()
    elif event.key in ('esc', ):
      self.cancel()
    elif event.key == 'delete':
      with self.transaction:
        self.dependency.span.removeDependency(self.dependency)
      self.commit()
                  
 
