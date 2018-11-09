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
from SafeCall import safecall
import itertools
from StrEditor import *

ItalicFont = Drawing.Font(Drawing.Font.defaultFont.familyname, Drawing.Font.defaultFont.size, ['italic'])


class HeaderLabel(UI.Label):
  # --- actions      
  dblClickAction    = Action(Behaviors.Actions.EditableActivated)
  clickAction       = Action(Behaviors.Actions.ViewSelected)
  # shiftClickAction  = Action('shiftClickToken')
  
  selected           = PresentationProperty(bool, False)
  
  @View.presentationState.changed
  def presentationState(self, context):
    color = HeaderLabel.color.default
    
    if self.selected:
      color = 'green'
      
    self.color = color
    
    UI.Label.presentationState.__changed__(self, context)
  
  
  
  def mouseDown(self, event):
    if event.numClicks >= 2:
      self.dblClickAction()
    else:
      self.clickAction()
  

class SpanView(View):
  """
    The span view displays the tokens and the annotation. 
    
    
    There are two modes for the span view. First is the compact one, where only soem basic information
    is displayed. Second is the expanded one, where we see the detailed annotations.
    
    Span view hosts a number of token views as well as segments and stuff. It is the job of
    the span view to make sure that the nodes are positioned properly. However, it is the job of the nodes 
    to draw themselves, no? The main thing is that the lines do not intersect. Also prefer shorter lines. 
    
    This is the most tricky thing to do. 
    
    So, how would the algorithm work?
    
    First, lets define some informal protocols. We have the tokens, which are all on a single line.
    And then we have nodes, which have nodes/tokens in their scope.
    
    I want to find a configuration of tokens and nodes so that
    
    1. the nodes are in the middle over the the nodes it encompases (or close to it)
    2. if a node contains other node, it has to be over it
    3. minimize the configuration of nodes that overlap
    
    Ok, so how does the span view gets its subviews?
    
    It queries the controller, no? No, the controller is responsible for the logic
    
    BTW, the algorithm needs to be deterministic. Which means that no sudden changes
    
  """
  
  # ----------- the subviews
  # Controller is responsible for keeping this in order
  
  @observable_property
  def tokenViews(self):
    return iter(self.__tokenViews)
    
  @tokenViews.setter
  @View.changes_layout
  def tokenViews(self, value):
    self.__tokenViews = list(value)
    self.needsLayout = True
    
  @observable_property
  def nodeViews(self):
    return iter(self.__nodeViews)
    
  @nodeViews.setter
  def nodeViews(self, value):
    self.__nodeViews = list(value)
    self.needsLayout = True
    
  @property
  def segments(self):
    for view in itertools.chain(self.__tokenViews, self.__nodeViews):
      view_segments = getattr(view, 'segments', ())
      for s in view_segments:
        yield s
    
  @observable_property
  def views(self):
    if self.modelLoaded:
      return itertools.chain([self.headerLabel, self.auxiliaryLabel], self.__tokenViews, self.__nodeViews, self.segments)
    else:
      return ()
    
  @property
  def viewsWithoutSegments(self):
    return itertools.chain([self.headerLabel, self.auxiliaryLabel], self.__tokenViews, self.__nodeViews)
    
  def addView(self, view, after = None, before = None):
    pass
    
  def removeView(self, view):
    pass
    
  # ----- lazy content loading
  @property
  def modelLoaded(self):
    try:   return self.__modelLoaded
    except: return False
  
  @modelLoaded.setter
  def modelLoaded(self, value):
    self.__modelLoaded = value
    
    # if model is loaded, we need to set up labels
    if value:
      self.headerLabel.superview = self
      self.headerLabel.value = self.controller.representedObject.headerLabel
      # self.headerLabel.clickAction = self.controller.spanMenuClicked
      #

      # print(self.headerLabel.clickAction)

      observers(self.headerLabel, 'selected').after += self.controller.viewSelectionChanged
      
      
    
      self.auxiliaryLabel.superview = self
      self.auxiliaryLabel.value = self.controller.representedObject.translation
      
    
    self.needsLayout = True
    
  # ----- layout logic
  #
  #  The view logic is fairly simple. The nodes are positioned in the middle
  #  over the elements they encompass. We layout the items in such way that they don't 
  #  intersect, which means tweaking their vertical coordinate
  #  
  #  What are the criteria of organising the items?
  #
  #  1. A node is always higher than all of the nodes it connects to
  #  2. If two nodes are connected, there should be no node that interjects
  #  3. 
  #
  # for every node, compute the nodes that it has to be lower than 
  # 
  # furthermore, for every node compute its 'x zone', which is the span 
  # between the nodes or tokens that it is connected to.
  # Find all groups of nodes whose x zones partially intersect
  # 
  # within eath group of such nodes, arrange the nodes accordingly   
  performsLayout = True
  
  tokenInitialOffset  = PresentationProperty(int, 50)
  tokenSeparator      = PresentationProperty(int, 30)
  
  
  def __groupNodesBasedOnX(self, nodeXZones):
    # saves a list of zones as a tuple of node list + x span that the
    # nodes occupy jointly
    zoneList = []
    
    # a helper function to check if two zones intersect
    def zones_intersect(a, b):
      a_node, (a_x0, a_x1) = a
      b_node, (b_x0, b_x1) = b
  
      return not ((a_x0 > b_x1) or (b_x0 > a_x1))      
      
    # a helper function to merge two zones
    def merge_zones(a, b):
      a_node, (a_x0, a_x1) = a
      b_node, (b_x0, b_x1) = b
      
      return (a_node+b_node, (min(a_x0, b_x0), max(a_x1, b_x1)))
    
    # iterate through the nodes
    # we create a new zone for every node and merge the zones in that 
    # intersect with it
    # this is a recursive process
    for nodeView in self.nodeViews:
      node_zone = ([nodeView], nodeXZones[nodeView])
      # the new zone partition
      zones_new = []
      
      for zone in zoneList:
        if zones_intersect(node_zone, zone):
          node_zone = merge_zones(node_zone, zone)
        else:
          zones_new.append(zone)
          
      # add the node zone to the new list
      zones_new.append(node_zone)
      
      # and reset the list
      zoneList = zones_new 
      
    # the zone list is ready at this point
    return [zone[0] for zone in zoneList]
    
  def __sortNodeViews(self, views):
    # Ok, the algorithm i use here is fairly simple
    # I will just insert stuff as it comes
    # If there is an element that needs to be below, I will insert it
    
    # first, sort the views based on the layout priority
    views = sorted(views, key = lambda v: v.layoutPriority)
    
    # this is a view such that there is NO view that it needs to be higher as
    def hasDependenciesView(view):
      for v in views:
        if v is not view:
          if view.shouldBeHigherThanNode(v):
            return True
            
      return False
    
    
    while len(views) > 0:
      # pick the next view to insert
      for i in xrange(len(views)):
        # we pick this view if this is the last view that we can check
        # OR if it has no dependencies
        if (i == len(views)-1) or (not hasDependenciesView(views[i])):
          # this view has no dependencies, insert it
          yield views[i]
          del views[i]
          break
      
      
      
  def __layoutNodesVertically(self, nodeViews, nodeXZones):    
    # layouts the nodes in a set vertically
    
    # basically, the idea here is to sort the nodes so that
    # if any specific node should be lower than the other one
    #
    # it should kind of work like priorities
    # if the node has the lowest priority, it should go on top
    # if one node is supposed to be higher then the other one, it should 
    # also be as close as possible to the other one
    

        
    def zones_intersect(a, b):
      a_x0, a_x1 = nodeXZones[a]
      b_x0, b_x1 = nodeXZones[b]
  
      return not ((a_x0 > b_x1) or (b_x0 > a_x1))      
    
    
    # first, we sort the views based on their layout priority
    # then, we sort again based on whether they should be higher then other nodes
    # nodeViews = sorted(nodeViews, key = lambda v: v.layoutPriority)
    # nodeViews = sorted(nodeViews, cmp = cmp_fun)
    nodeViews = list(self.__sortNodeViews(nodeViews))
    
    # split the nodes into groups that can coexist at the same x level
    def generateNodeGroups():
      current = []
      
      for view in nodeViews:
        for v1 in current:
          if zones_intersect(v1, view):
            yield current
            current = []
            break
        
        current.append(view)
        
      if len(current)>0:
        yield current
    
    # start arranging them
    y = min(v.rect.y0 for v in self.tokenViews)
    
    for nodeViewGroup in generateNodeGroups():
      ynew = y
      for nodeView in nodeViewGroup:
        x, yold = nodeView.position
        nodeView.position = (x, y - getattr(nodeView, 'preferredNodeDistance', 25) - nodeView.size.height)
        ynew = min(ynew, nodeView.rect.y0 )
        
      y = ynew
  
  #deferLayout = False  
    
        
  def computeLayout(self):
    """ Arrange the subviews """        
    # if model is not loaded, basically do nothing
    if not self.modelLoaded:
      self.size = (500, 50)
      self.dirty()
      self.needsLayout = False
      return
        
    # ============= 1. Arrange the tokens
    # this happens deterministically, so if the tokens did not change, their 
    # positions will be identical between runs
    # also, we do not move tokens around!
    x = self.tokenInitialOffset
    for tokenView in self.tokenViews:
      # x = x + tokenView.size.width/2
      tokenView.position = (x, 0)
      x = tokenView.rect.x1 + self.tokenSeparator
    
      
    # ============= 2. Determine the x coordinates and x zones for the nodes
    # The middle of the node should be at the middle of its x zone
    nodeXZones = dict()
    for nodeView in sorted(self.nodeViews, key = lambda v: getattr(v, 'positionPriority', 10)):
      nodeView.position = ((min(v.rect.center.x for v in nodeView.dependentViews) + max(v.rect.center.x for v in nodeView.dependentViews) - nodeView.size.width)/2, 0)
      
      x0 = min(min(v.rect.x0 for v in nodeView.dependentViews), nodeView.rect.x0)
      x1 = max(max(v.rect.x1 for v in nodeView.dependentViews), nodeView.rect.x1)
      
      nodeXZones[nodeView] = (x0, x1)
      
          
    
    # ============= 3. Group the nodes based on their x zones
    nodeLayoutGroups = self.__groupNodesBasedOnX(nodeXZones)
    for layoutGroup in nodeLayoutGroups:
      self.__layoutNodesVertically(layoutGroup, nodeXZones)
      
    # ============= 3. Resize the container view to fit all the annotations etc. 
  
    # place the label views so taht they don't mess stuff up
    self.headerLabel.position = (15, 0)
    self.auxiliaryLabel.position = (0, self.headerLabel.size.height + 15)
    
    
    # adjust the node views 
    # we want the highest element be 25 pixels under the header
    ymin = min(v.rect.y0 for v in self.views) - 25 - self.headerLabel.size.height
    
    # move all the view vertical coordinates so that y0 becomes 0
    for view in self.viewsWithoutSegments:
      (x, y) = view.position
      view.position = (x, y - ymin)
    
    ymax = max(v.rect.y1 for v in self.viewsWithoutSegments)
    
    # position the labels
    self.headerLabel.position = (15, 0)
    self.auxiliaryLabel.position = (self.tokenInitialOffset, ymax)    
  
    # adjust the size of the span
    self.size = (max(500, max(v.rect.x1 for v in self.viewsWithoutSegments)), self.auxiliaryLabel.rect.y1 + 25)
   
    # ============= 4. Reset all the segments
    for nodeView in self.nodeViews:
      safecall(nodeView).setupSegments()
     
    for s in self.segments: 
      willChange(view, 'globalRect', {})
      willChange(s, 'superview', {})
      s._View__superview = self
      willChange(s, 'superview', {})
      didChange(view, 'globalRect', {})
   
   
    # ============= Layouting is finished
    self.dirty()
    self.needsLayout = False
  
  def draw(self, drawRect):
    if not self.modelLoaded: 
      Drawing.Color('red').makeDrawcolor()
      Drawing.Path().moveTo(0, 5).lineTo(200, 5).stroke()
      return
    
    Drawing.Color('black').makeDrawcolor()
    y = self.headerLabel.rect.center.y
    x0 = self.headerLabel.rect.x0
    x1 = self.headerLabel.rect.x1
    xmax = 500
    
    Drawing.Path().moveTo(0, y).lineTo(x0, y).stroke()
    if xmax > x1:
      Drawing.Path().moveTo(x1, y).lineTo(xmax, y).stroke()
    #Drawing.Path.initWithRect(0, 0, *self.size).stroke()
    
  
  # ----- initializer
  def __init__(self, *args, **kwargs):
    self.__tokenViews = []
    self.__nodeViews  = []
    self.headerLabel = HeaderLabel(margins=(10, 10, 0, 0))
    self.auxiliaryLabel = StrEditor(margins=(5, 0, 0, 0), font=ItalicFont, fstyle='none', targetVariable='translation')
    super(SpanView, self).__init__(*args, **kwargs)  

    self.auxiliaryLabel.controller = self.controller
    self.headerLabel.controller = self.controller