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
from UIToolkit.UI.Editors import EditorOperationError

class TranscriptionEditController(UI.Editors.EditController):
  def __init__(self, tokenController):
    self.tokenController = tokenController
    self.transaction = self.token.__db__.activeTransaction
    if self.transaction is None:
      self.transaction = self.token.__db__.transaction()

  @property
  def editor(self):
    return self.tokenController.view.transcriptionLabel
    
  @property
  def spanController(self):
    return self.tokenController.spanController  
    

  @property
  def token(self):
    return self.tokenController.representedObject    
      
  @property
  def value(self):
    try:
      return self.token.transcription
    except:
      return 'sadasd'
        
    
  @value.setter
  def value(self, v):
    try: 
      with self.transaction:
        self.token.transcription = v
    except:
      pass
    
  def insertTextAtPosition(self, text, position):
    if position < 0  or position > len(self.value):
      raise UI.Editors.EditorOperationError("Insert position escapes the string")
      
    p0 = self.value[0:position]
    p1 = self.value[position:len(self.value)]  
    text = unicode(text)
    
    
    
    
    # if we have a space, the user wants us to split the tokens
    if text == ' ':  
      # if the space has ocured in the beginning or the end, we do nothing
      if len(p0) == 0 or len(p1) == 0:
        return(len(p0))
      
      
      # set the token to the value
      self.value = p0
      
      #  add the new token
      with self.transaction:
        span = self.spanController.representedObject
        new_token = span.__db__.document.persistenceSchema.classes.Token(p1)
        span.addToken(new_token, after = self.token)
      
      # remove the current transaction
      self.transaction = None
        
      # give control to the new edit window
      new_tokenController = self.spanController.getControllerForObject(new_token)
      new_view = new_tokenController.view.transcriptionLabel
      new_view.window.firstResponder = new_view
      new_view.moveCursorToStart()
    else:
      self.value = p0 + text + p1
    
    return len(p0 + text)  

    
  def cursorMovedAfterText(self):
    # get the next token
    try:
      next_token = self.token.span.tokens[self.token.index + 1]
    except IndexError:
      next_token = None
      
    if next_token is not None:
      next_tokenController = self.spanController.getControllerForObject(next_token)
      next_view = next_tokenController.view.transcriptionLabel
      next_view.window.firstResponder = next_view
      next_view.moveCursorToStart()
    
    
  def cursorMovedBeforeText(self):
    # get the previous token
    try:
      previous_token = self.token.span.tokens[self.token.index - 1]
    except IndexError:
      previous_token = None
      
    if previous_token is not None:
      previous_tokenController = self.spanController.getControllerForObject(previous_token)
      previous_view = previous_tokenController.view.transcriptionLabel
      previous_view.window.firstResponder = previous_view
      previous_view.moveCursorToEnd()
    
        
  def deleteTextAtPosition(self, position):
    if position < 0  or position > len(self.value):
      raise UI.Editors.EditorOperationError("Delete position escapes the string")
      
    if position == 0:
      return 0
    
    p0 = self.value[0:(position-1)]  
    p1 = self.value[position:len(self.value)]  
    
    value = p0 + p1
    if len(value) == 0:
      # delete the token
      window = self.editor.window
      refmark = self.token.refmark
      
      with self.transaction:
        try:
          self.token.refmark = None  
          self.spanController.representedObject.removeToken(self.token)
        except ValueError:
          self.token.refmark = refmark
          return position
      
      window.firstResponder = None    
      return 0
    else:
      self.value = value
      return position -1 
 
    
  def keyEvent(self, event):
    if event.key in ('enter', 'return'):
      self.transaction.commit()
      self.transaction = None
      self.editor.window.firstResponder = None
      return True
    elif event.key in ('esc', ):
      self.transaction.abort()
      self.transaction = None
      self.editor.window.firstResponder = None
      return True      
    
  def endEdit(self):
    if self.transaction is not None:
      self.transaction.commit()
      self.transaction = None
