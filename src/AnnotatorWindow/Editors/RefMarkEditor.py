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
import logging
from AnnotatorWindow.Views import *

class RefMarkEditor(Responder):
  """ A controller responsible for editing a constituent span """
  
  def __init__(self, tokenController):
    # init the basic variables
    self.window          = tokenController.view.window
    self.refmark = tokenController.representedObject.refmark
    assert(self.refmark is not None)
    
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
    self.window.controller.selectedView   = None
    self.window.controller.highlightedView = None
    
    # create a transaction
    # self.transaction = self.token.__db__.activeTransaction
    # if self.transaction is None:
    #   self.transaction = self.token.__db__.transaction()
    #
    if self.refmark.__db__.activeTransaction is not None:
      self.transaction = self.refmark.__db__.activeTransaction
    else:
      self.transaction = self.refmark.__db__.transaction()
    
        
      
  def yieldedFirstResponder(self):
    # delete the transaction object
    self.transaction = None
        
    # remove highlighting on the dependency view
    self.window.controller.selectedView    = None
    self.window.controller.highlightedView = None
        
    
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
    return isinstance(view, TokenView) or isinstance(view, ConstituentView)
    
  # ---- highlighting support override  
  viewCanBeHighlighted = isValidTarget
  
  viewCanBeSelected = isValidTarget
  
    
  # ----- event handling    
  def viewSelected(self, view):
    """ Catches the view selection message """    
    if isinstance(view, TokenView) or isinstance(view, ConstituentView):
      assert(self.isValidTarget(view))
      
      # print "Toggling refmark on %s" % view.controller.representedObject
      
      token = view.controller.representedObject
      with self.transaction:
        if token.refmark is self.refmark:
          token.refmark = None
        else:
          token.refmark = self.refmark
      
  
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
            
