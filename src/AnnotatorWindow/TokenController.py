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
from SafeCall import safecall
from VariableController import *
from Editors.DependencyEditors import *
from Editors.RefMarkEditor import *
from Editors.TranscriptionEditController import *
from Editors.StrValueController import *


class TokenController(ViewController):
  def __init__(self, token, spanController):
    self.spanController = spanController
    self.representedObject = token
    self.view = TokenView(controller = self, superview = spanController.view)
    self.refMarkView = None
    self.variableController = None
    self.annotationChoiceView = None

    # bind the selection 
    # bindings(self.view).selected = ValueBinding(spanController.annotationController, 'selectedView', lambda selectedView: self.view is selectedView)
    # bindings(self.view).selectable = ValueBinding(self.view.window, 'firstResponder', lambda responder: False if safecall(responder).viewCanBeSelected(self.view) == False else True)
    observers(self.view, 'selected').after += self.viewSelectionChanged
        
    # bind the highlighting 
    # bindings(self.view).highlighted = ValueBinding(spanController.annotationController, 'highlightedViews', lambda highlightedViews: self.view in highlightedViews)
#    bindings(self.view).highlightable = ValueBinding(self.view.window, 'firstResponder', lambda responder: False if safecall(responder).dispatchCall('viewCanBeHighlighted', self.view) == False else True)
    
    # update refmark binding
    observers(self.representedObject, 'refmark').after += self.__refmark_changed
    self.__refmark_changed(None, None)
    
    # link the show glosses state
    bindings(self.view).showsGloss = ValueBinding(self.annotationController, 'showsGloss', lambda x: x)
    
  @property
  def annotationController(self):
    return self.spanController.annotationController  
    
  # ---- subview manipulation logic
  def addedSubview(self, view):
    if hasattr(view, 'highlighted'):
      annotationController = view.window.controller
      # bindings(view).highlighted = ValueBinding(annotationController, 'highlightedViews', lambda highlightedViews: view in highlightedViews)
    
  # ---- new annotation creation
  def createDependencyAnnotation(self, sender):
    # create a new dependency relation
    transaction = transaction = self.representedObject.__db__.transaction()
    document = self.representedObject.__db__.document
    with transaction:
      dependency = document.persistenceSchema.classes.DependencyRelation(self.representedObject, self.representedObject)
      
    # start editing the newly created dependency relation
    depController = self.spanController.getControllerForObject(dependency)
    safecall(depController).edit('target')
    
  def createConstituentAnnotation(self, sender):
    # create a new dependency relation
    transaction = transaction = self.representedObject.__db__.transaction()
    document = self.representedObject.__db__.document
    with transaction:
      constituent = document.persistenceSchema.classes.Constituent()
      constituent.add(self.representedObject)
      
    # start editing the newly created dependency relation
    conController = self.spanController.getControllerForObject(constituent)
    safecall(conController).edit()  
  
  def createReferenceLabel(self, sender):
    transaction = transaction = self.representedObject.__db__.transaction()
    document = self.representedObject.__db__.document
    with transaction:
      refmark = document.persistenceSchema.classes.ReferenceMark()
      self.representedObject.refmark = refmark
    self.view.window.firstResponder = RefMarkEditor(self)
      
  # ----- refmark handling
  def __refmark_changed(self, obj, context):
    if self.refMarkView is not None:
      self.refMarkView.anchor = None
      self.refMarkView = None
    
    if self.representedObject.refmark is not None:
      self.refMarkView = RefMarkView(anchor = self.view.transcriptionLabel, controller = self, anchorPosition="above right")
      bindings(self.refMarkView).value = ValueBinding(self.representedObject.refmark, 'index', lambda i, *args: u"ref%s" % (i+1) if i is not None else "")
      #bindings(self.refMarkView).highlighted = ValueBinding(self.annotationController, 'highlightedViews', lambda highlightedViews: self.refMarkView in highlightedViews)
      bindings(self.refMarkView).selected = ValueBinding(self.view.window, 'firstResponder', lambda responder: getattr(responder, 'refmark', None) is self.representedObject.refmark)

  def editableActivated(self, sender):
    if sender is None: return
    if self.view.transcriptionLabel.editing: return
        
    # start editing the refmark if needed
    if sender is self.refMarkView:
      self.view.window.firstResponder = RefMarkEditor(self)
    elif sender is self.view.transcriptionLabel:
      self.view.window.firstResponder = sender#TokenEditController
    elif sender is self.view.secondaryLabel:
      print "Is it so?"
      self.view.window.firstResponder = sender
      # self.annotationController.selectedView = None
      #
      # print "Wants to edit the token!"
  
  def startEditAndGetEditControllerForView(self, view):
    if view is self.view.transcriptionLabel:
      self.annotationController.selectedView = None
      return TranscriptionEditController(self)
    elif view is self.view.secondaryLabel:
      self.annotationController.selectedView = None
      return StrValueEditController(view, self.representedObject, view.targetVariable)
      
      
  # ---- if the token controller is in the responder chain, we ignore all selection etc. events
  def viewSelected(self, view):
    pass
  
  def viewCanBeSelected(self, view):
    return False
  
  viewCanBeHighlighted = viewCanBeSelected
      
  # ---- selection support
  def viewSelectionChanged(self, view, context):
    safecall(self.variableController).detach()
    self.variableController = None
    if self.annotationChoiceView is not None:
      self.annotationChoiceView.anchor = None
      self.annotationChoiceView = None
    
    if self.view.selected:  
      self.variableController = VariableController(self, self.view.transcriptionLabel)
      self.annotationChoiceView = ChoiceView(
        itemsPerLine = 1, 
        anchor = self.view, 
        anchorPosition='above',
        controller = self,
        hotkeysEnabled = False)
      self.annotationChoiceView.choices = ['new agreement relation', 'new constituent', 'new reference label']
      self.annotationChoiceView.getViewForChoice('new agreement relation').choiceAction = self.createDependencyAnnotation
      self.annotationChoiceView.getViewForChoice('new constituent').choiceAction = self.createConstituentAnnotation
      self.annotationChoiceView.getViewForChoice('new reference label').choiceAction = self.createReferenceLabel
      
      # self.annotationChoiceView.choiceAction = self.annotationChoiceSelected