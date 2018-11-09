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
from Editors.DependencyEditors import *
from VariableController import *


class DependencyController(ViewController):
  def __init__(self, dependency, spanController):
    self.spanController = spanController
    self.representedObject = dependency
    self.view = DependencyView(superview = spanController.view, controller=self)
    self.editor = None
    self.variableController = None
        
    # set up the selection and the highlight bindings
    #bindings(self.view).selected = ValueBinding(spanController.annotationController, 'selectedView', lambda selectedView: self.view is selectedView)
    observers(self.view, 'selected').after += self.viewSelectionChanged    
    #bindings(self.view).highlighted = ValueBinding(spanController.annotationController, 'highlightedViews', lambda highlightedViews: self.view in highlightedViews)
    # bindings(self.view).highlightable = ValueBinding(self.view.window, 'firstResponder', lambda responder: False if safecall(responder).dispatchCall('viewCanBeHighlighted', self.view) == False else True)
    
  @property
  def annotationController(self):
    """ The master controller for this window """      
    return self.spanController.annotationController  
         
  # -------- relation editing support
  def edit(self, member):
    if self.editor is not None:
      return
      
    safecall(self.variableController).detach()
    self.variableController = None  
    
    self.editor = DependencyRelationEditor(self, member)
    self.view.window.setFirstResponder(self.editor)
    
  
  def editableActivated(self, editableView):
    # this can be either the target or the controller
    tag = getattr(editableView, 'tag', None)
    
    if tag in ('target','controller'):
      self.edit(tag)
    
    
  # ---- selection support
  def viewSelectionChanged(self, view, context):
    safecall(self.variableController).detach()
    self.variableController = None
    
    if self.view.selected and self.editor is None:  
      self.variableController = VariableController(self, self.view, anchorPosition = 'over')
    
    
  