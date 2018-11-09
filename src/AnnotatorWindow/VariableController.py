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
from Views import *
from AnnotatorWindow.Views import ChoiceView


class VariableController(ViewController):
  def __init__(self, masterController, anchorView, anchorPosition = 'below'):
    self.masterController = masterController
    self.view = VariableView(anchor=anchorView, anchorPosition=anchorPosition, controller=self)     
    self.editor = None
  
  @property
  def representedObject(self):
    return self.masterController.representedObject      
        
  @property
  def annotationController(self):
    """ The master controller for this window """      
    return self.masterController.annotationController  
        
  def detach(self):
    if self.editor is not None:
      self.view.window.firstResponder = None
    self.view.anchor = None
    
  def addedSubview(self, view):    
    if hasattr(view, 'highlighted'):
      bindings(view).highlighted = ValueBinding(self.annotationController, 'highlightedViews', lambda highlightedViews: view in highlightedViews)

    if isinstance(view, ValueLabel): 
      view.clickAction = self.variableViewClicked

    if isinstance(view, ChoiceLabel):
      view.choiceAction = self.valueSelected
      
    
  # ----- variable selection support
  @observable_property
  def selectedKey(self): 
    try: return self.__selectedKey
    except: return None
  
  @selectedKey.setter
  def selectedKey(self, value):
    """ Selects a new variable to be edited """
    # make sure to deselect the previous key and remove the coice window
    if self.selectedKey is not None:
      self.view.getValueViewForKey(self.selectedKey).selected = False
      self.editor.anchor = None
      self.view.window.firstResponder = None
      self.editor = None
      
    self.__selectedKey = value
    
    # set up the new selection
    if self.selectedKey is not None:
      valueView = self.view.getValueViewForKey(self.selectedKey)
      self.editor = ChoiceView(controller=self, anchor = valueView, anchorPosition='above')
      self.editor.choices = self.representedObject.variables.getValidValuesForKey(self.selectedKey)
      self.editor.cancelAction = self.clearSelection
      self.editor.deleteAction = self.deleteKey
      self.view.window.firstResponder = self.editor
          
  def variableViewClicked(self, sender):
    assert(isinstance(sender, ValueLabel))
    self.selectedKey = sender.key
    
  def deleteKey(self, sender):
    transaction = self.representedObject.__db__.transaction()
    with transaction:
      try:
        self.representedObject.variables[self.selectedKey] = None
      except:
        pass
    
    transaction.commit()
    
    self.selectedKey = None
      
    
  def clearSelection(self, sender):
    self.selectedKey = None
    
  def valueSelected(self, sender):
    assert(isinstance(sender, ChoiceLabel))
    value = sender.choice
    
    # set the value
    transaction = self.representedObject.__db__.transaction()
    with transaction:
      try:
        self.representedObject.variables[self.selectedKey] = value
      except:
        pass
    
    transaction.commit()
    
    self.selectedKey = None
    
    
    
  
  