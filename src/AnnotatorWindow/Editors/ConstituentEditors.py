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
import logging


class ConstituentSpanEditor(Responder):
  """ A controller responsible for editing a constituent span """
  
  def __init__(self, constituentController):
    # init the basic variables
    self.constituentController = constituentController
    self.constituent           = self.constituentController.representedObject   
    self.window                = self.constituentController.view.window
    
    
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
    self.window.controller.selectedView   = self.constituentController.view
    self.window.controller.highlightedView = None
    self.constituentController.view.segmentsSelected = True
    self.constituentController.view.segmentsFocused = True
        
    # create a transaction
    if self.constituent.__db__.activeTransaction is not None:
      self.transaction = self.constituent.__db__.activeTransaction
    else:
      self.transaction = self.constituent.__db__.transaction()
    
        
      
  def yieldedFirstResponder(self):
    # delete the transaction object
    self.transaction = None
    self.originalValue = None    
    self.constituentController.editor = None
        
    # remove highlighting on the dependency view
    self.window.controller.selectedView    = None
    self.window.controller.highlightedView = None
    self.constituentController.view.segmentsSelected = False
    self.constituentController.view.segmentsFocused = False
        
    
  # ----- edit logic
  def commit(self):
    self.transaction.commit()
    # resign the first responder status
    Application().firstResponder = None
  
  def cancel(self):
    self.transaction.abort()
    # resign the first responder status
    Application().firstResponder = None
    
  def canAddOrRemoveToken(self, token):
    return (token.span is not None) and (token.span is self.constituent.span)
           
  
  def isValidTarget(self, view):
    return isinstance(view, TokenView) and self.canAddOrRemoveToken(view.controller.representedObject)             
    
  # ---- highlighting support override  
  viewCanBeHighlighted = isValidTarget
  
  def viewCanBeSelected(self, view):
    return view is self.constituentController.view or self.isValidTarget(view)
  
    
  # ----- event handling    
  def viewSelected(self, view):
    """ Catches the view selection message """    
    if not self.isValidTarget(view): return
    
    if isinstance(view, TokenView):
      assert(self.isValidTarget(view))
      with self.transaction:
        try:
          token = view.controller.representedObject
          if token in self.constituent and len(self.constituent)>1: 
            self.constituent.remove(token)
          else:
            self.constituent.add(token)
        except ValueError:
          logging.error("Cannot remove the consituent")
      
  
  # def highlightedItemChanged(self, view, context):
  #   """ Catches the however view message """
  #   self.window.controller.highlightedView = view
  
  def editableActivated(self, sender):
    pass
  

  def keyDown(self, event):
    if event.key in ('enter', 'return'):
      self.commit()
    elif event.key in ('esc', ):
      self.cancel()
    elif event.key == 'delete':
      success = True
      with self.transaction:
        try:
          self.constituent.span.removeConstituent(self.constituent)
        except ValueError:
          logging.error("Cannot remove the consituent")
          success = False
      if success:
        self.commit()
            
