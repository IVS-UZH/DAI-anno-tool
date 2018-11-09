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
from Editors.ConstituentEditors import *
from VariableController import *
from Editors.RefMarkEditor import *



class ConstituentController(ViewController):
  def __init__(self, constituent, spanController):
    self.spanController = spanController
    self.representedObject = constituent
    self.view = ConstituentView(superview = spanController.view, controller=self)
    self.editor = None
    self.variableController = None
    self.annotationChoiceView = None
    self.refMarkView = None
    
    
    # set up the selection and the highlight bindings
    #bindings(self.view).selected = ValueBinding(spanController.annotationController, 'selectedView', lambda selectedView: self.view is selectedView)
    observers(self.view, 'selected').after += self.viewSelectionChanged
    #bindings(self.view).highlighted = ValueBinding(spanController.annotationController, 'highlightedViews', lambda highlightedViews: self.view in highlightedViews)
    # bindings(self.view).highlightable = ValueBinding(self.view.window, 'firstResponder', lambda responder: False if safecall(responder).dispatchCall('viewCanBeHighlighted', self.view) == False else True)
    observers(self.representedObject, 'refmark').after += self.__refmark_changed
    self.__refmark_changed(None, None)
    
    
  @property
  def annotationController(self):
    return self.spanController.annotationController  

  # ---- subview manipulation logic
  def addedSubview(self, view):
    if hasattr(view, 'highlighted'):
      annotationController = view.window.controller
      # bindings(view).highlighted = ValueBinding(annotationController, 'highlightedViews', lambda highlightedViews: view in highlightedViews)

  # ----- refmark handling
  def __refmark_changed(self, obj, context):
    if self.refMarkView is not None:
      self.refMarkView.anchor = None
      self.refMarkView = None
    
    if self.representedObject.refmark is not None:
      self.refMarkView = RefMarkView(anchor = self.view, controller = self, anchorPosition="bottom right")
      bindings(self.refMarkView).value = ValueBinding(self.representedObject.refmark, 'index', lambda i, *args: u"ref%s" % (i+1) if i is not None else "")
      #bindings(self.refMarkView).highlighted = ValueBinding(self.annotationController, 'highlightedViews', lambda highlightedViews: self.refMarkView in highlightedViews)
      bindings(self.refMarkView).selected = ValueBinding(self.view.window, 'firstResponder', lambda responder: getattr(responder, 'refmark', None) is self.representedObject.refmark)

  def createReferenceLabel(self, sender):
    transaction = transaction = self.representedObject.__db__.transaction()
    document = self.representedObject.__db__.document
    with transaction:
      refmark = document.persistenceSchema.classes.ReferenceMark()
      self.representedObject.refmark = refmark
    self.view.window.firstResponder = RefMarkEditor(self)

  # -------- constituent editing support
  def edit(self):
    if self.editor is not None:
      return
    
    if self.annotationChoiceView is not None:
      self.annotationChoiceView.anchor = None
      self.annotationChoiceView = None  
      
    safecall(self.variableController).detach()
    self.variableController = None
    
    self.editor = ConstituentSpanEditor(self)
    self.view.window.setFirstResponder(self.editor)
    
  
  def editableActivated(self, sender):
    # start editing the refmark if needed
    if sender is self.refMarkView:
      self.view.window.firstResponder = RefMarkEditor(self)
    else:
      self.edit()
    
  # ---- new annotation creation
  def createDependencyAnnotation(self, sender):
    # create a new dependency relation
    transaction = transaction = self.representedObject.__db__.transaction()
    document = self.representedObject.__db__.document
    with transaction:
      dependency = document.persistenceSchema.classes.DependencyRelation(self.representedObject, self.representedObject)
    transaction.commit()
      
    # start editing the newly created dependency relation
    depController = self.spanController.getControllerForObject(dependency)
    safecall(depController).edit('target')  
    
    
  # ---- selection support
  def viewSelectionChanged(self, view, context):
    if self.annotationChoiceView is not None:
      self.annotationChoiceView.anchor = None
      self.annotationChoiceView = None
    safecall(self.variableController).detach()
    self.variableController = None
    
    
    if self.view.selected and self.editor is None:  
      self.variableController = VariableController(self, self.view, anchorPosition='right')
      self.annotationChoiceView = ChoiceView(
        itemsPerLine = 1, 
        anchor = self.variableController.view, 
        anchorPosition='above',
        controller = self,
        hotkeysEnabled = False)
      self.annotationChoiceView.choices = ['new agreement relation', 'new reference label']
      self.annotationChoiceView.getViewForChoice('new agreement relation').choiceAction = self.createDependencyAnnotation
      self.annotationChoiceView.getViewForChoice('new reference label').choiceAction = self.createReferenceLabel
      
      
      
      
    