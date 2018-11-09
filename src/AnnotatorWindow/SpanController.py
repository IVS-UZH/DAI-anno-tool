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
from TokenController import *
from ConstituentController import *
from DependencyController import *
from operator import attrgetter
import itertools
import model
from Editors.StrValueController import *
from Views.SpanHeaderEditDialog import editSpanHeader
from VariableController import *



class SpanController(ViewController):
  """
    Controls the connection between the span model and the span visualisation
  
    The task of the span controller is to create and update the view in accordance
    to model changes and also update the model in accordance with user interactions 
    with the UI
  """
  
  
  def getViewForSpanObject(self, object):
    """ Retrieve the view for a given object in the span. It is an error if no such object exists  """
    return self.__controllerMap[object].view
  

  def updateModelViewState(self):
    """ Makes sure that the UI reflects the last changes in the model """
    
    # do nothing if model is not loaded
    if not self.modelLoaded:
      self.view.needsLayout = True
      self.view.dirty()
      return
    
    
    # optimise layout process — we only want to lay out once!
    windowLayoutInProgress = self.view.window.layoutInProgress
    self.view.window.layoutInProgress = True
    
    # all objects currently in the model
    span_objects = set(self.representedObject.tokens) | set(self.representedObject.constituents) | set(self.representedObject.dependencies)
    
    # which view state objects should we remove?
    for obj in set(self.__controllerMap.keys()) - span_objects:
      del self.__controllerMap[obj]
      
    # which view state objects should we add?
    for obj in span_objects - set(self.__controllerMap.keys()):
      if isinstance(obj, model.Token):
       controller = TokenController(obj, self)
      elif isinstance(obj, model.Constituent):
        controller = ConstituentController(obj, self)
        observers(controller.view, 'dependentViews').after += self.__modelChanged
      elif isinstance(obj, model.DependencyRelation):
        controller = DependencyController(obj, self)
        observers(controller.view, 'dependentViews').after += self.__modelChanged
      else:
        raise TypeError("Unknown model object %s" % obj)
      
      self.__controllerMap[obj]  = controller
    
    # 4. update the span view state
    self.view.tokenViews = map(attrgetter('view'), sorted(filter(lambda o: isinstance(o, TokenController), self.__controllerMap.values()), key=lambda o: o.representedObject.index))
    self.view.nodeViews = map(attrgetter('view'), filter(lambda o: not isinstance(o, TokenController), self.__controllerMap.values()))
    
    self.view.window.layoutInProgress = windowLayoutInProgress
          
    # force layout and presentation change of all tokens  
    self.view.needsLayout = True
    self.view.dirty()
    
      
  def __modelChanged(self, obj, context):
    self.updateModelViewState()
  
  # ----- lazy content loading
  @property
  def modelLoaded(self):
    try:   return self.__modelLoaded
    except: return False
  
  @modelLoaded.setter
  def modelLoaded(self, value):
    self.__modelLoaded = value
    if self.representedObject.spanInfo.get("type", None) == 'Question':
      return
    
    # clear/create state on every model change
    
    # clear the view map (mapping from span objects to corresponding views)
    self.__viewMap = dict()
  
    # clear the map from objects to controllers
    self.__controllerMap = dict()
  
    # clear the subcontroller lists
    # remove all refmarks
    
    for tcontroller in self.__tokenControllers:
      if tcontroller.refMarkView is not None:
        tcontroller.refMarkView.anchor = None
        tcontroller.refMarkView = None
      
    self.__tokenControllers = []
    self.__dependencyControllers = []
    self.__constituentControllers = []
    self.view.tokenViews = []
    self.view.nodeViews = []
    
    
    # if model is loaded, we start observing the changes etc.
    if value:
      # subscribe to changes
      observers(self.representedObject, 'tokens').after += self.__modelChanged
      observers(self.representedObject, 'dependencies').after += self.__modelChanged
      observers(self.representedObject, 'constituents').after += self.__modelChanged
    
      self.updateModelViewState()
    else:
      observers(self.representedObject, 'tokens').after -= self.__modelChanged
      observers(self.representedObject, 'dependencies').after -= self.__modelChanged
      observers(self.representedObject, 'constituents').after -= self.__modelChanged      
      
    self.view.modelLoaded = value
  
  # ----- initialization
  def __init__(self, span, annotationController, loadModel = True):
    # prepare the state and the initial view
    self.representedObject = span
    self.annotationController =  annotationController
    
    
    if span.spanInfo.get("type", None) in ('Q', 'q', 'Question'):
      # use simple view
      self.view = SimpleSpanView(controller = self, superview=annotationController.containerView)
    else:  
      self.view = SpanView(controller = self, superview=annotationController.containerView)

    # init the view map (mapping from span objects to corresponding views)
    self.__viewMap = dict()
    
    # the possible menu
    self.spanChoiceView = None
    
    
    # map from objects to controllers
    self.__controllerMap = dict()
    
    # setup the subcontroller lists
    self.__tokenControllers = []
    self.__dependencyControllers = []
    self.__constituentControllers = []

    
    self.modelLoaded = loadModel
    
  def getControllerForObject(self, object):
    return self.__controllerMap.get(object, None)

  # --- span menu
  def viewSelectionChanged(self, view, context):
    pass
    
  # def viewSelectionChanged(self, view, context):
 #    print "selection changed"
 #    if self.spanChoiceView is not None:
 #      self.spanChoiceView.anchor = None
 #      self.spanChoiceView = None
 #
 #    if self.view.headerLabel.selected:
 #      self.spanChoiceView = ChoiceView(
 #        itemsPerLine = 1,
 #        anchor = self.view.headerLabel,
 #        anchorPosition='above',
 #        controller = self,
 #        hotkeysEnabled = False)
 #      self.spanChoiceView.choices = ['Copy annotation structure', 'Paste annotation structure']
 #      self.spanChoiceView.getViewForChoice('Copy annotation structure').choiceAction = self.copyAnnotationStructure
 #      self.spanChoiceView.getViewForChoice('Paste annotation structure').choiceAction = self.pasteAnnotationStructure
 #
 #  def copyAnnotationStructure(self, sender):
 #    print "Copy annotation structure"
 #
 #  def pasteAnnotationStructure(self, sender):
 #    print "Paste annotation structure"
    
      

  # --- edit support
  def editableActivated(self, sender):
#    print "Editable activated", sender
    
    
    if sender is None: return
    if self.view.auxiliaryLabel.editing: return
    
    if sender is self.view.auxiliaryLabel:
      self.view.window.firstResponder = sender
      
    if sender is self.view.headerLabel:
      editSpanHeader(self.representedObject, self.view)
  
  
  
  def startEditAndGetEditControllerForView(self, view):
    # this is ungly, but what should I do?
    return StrValueEditController(view, self.representedObject, view.targetVariable)
    # print view, "requests edit controller"
    # raise Exception(11)
    # self.annotationController.selectedView = None
    # return TranscriptionEditController(self)
  
    