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



from UIToolkit import Action, Responder
from observing import observable, willChange, didChange, observers, changes

class Menu(object):
  # ---- item subclasses
  class Item(object):
    def __init__(self, menu):
      self.__menu = menu
      
    @property
    def menu(self): return self.__menu

  class Separator(Item):
    pass
  
  class ActionItem(Item):
    def __init__(self, name, menu):
      Menu.Item.__init__(self, menu)
      self.__name = name
      
    @property
    def name(self): return self.__name
    
    def __repr__(self):
      return "Item(name=%s, action=%s)" % (self.name, self.action.action)
    
    action = Action()
    
    key = None

  # ---- menu implemenation
  def __init__(self, name):
    self.__items = []
    self.__name  = name
  
  @observable  
  @property
  def items(self):
    return iter(self.__items) 
    
  def __iter__(self):
    return self.items  
    
  @property
  def name(self):
    return self.__name
    
  def __getitem__(self, name):
    for item in self.__items:
      if isinstance(item, Menu.ActionItem) and item.name == name:
        return item  
    
  # --- adding new items  
  @changes(items)
  def addItem(self, name, action = None, key = None):
    item = Menu.ActionItem(name, self)
    if action is not None:
      item.action = action
    item.key = key  
    self.__items.append(item)      
    return item
  
  @changes(items)
  def addSeparator(self):
    item = Menu.Separator(self)     
    self.__items.append(item)      
    return item
    
    
class MenuList(object):
  def __init__(self):
    self.__items = []
    
  def __menu_changing(self, menu, context):
    willChange(self, 'items', context)

  def __menu_changed(self, menu, context):
    didChange(self, 'items', context)
    
    
  @observable  
  @property
  def items(self):
    return iter(self.__items)
    
  def __iter__(self):
    return self.items
  
    
  def __getitem__(self, name):
    for menu in self.__items:
      if menu.name == name:
        return menu
            
  @changes(items)          
  def addMenu(self, menu, after = None, before = None):
    # find the anchor (if nessesary)
    anchor = None
    if after is not None:
      anchor = self[after]
      offset = +1
    elif before is not None:
      anchor = self[before]
      offset = 0
    if anchor is not None:
      index = self.__items.index(anchor) + offset
      self.__items.insert(index, menu)
    else:
      self.__items.append(menu)
      
    observers(menu, 'items').after += self.__menu_changed  
    observers(menu, 'items').before += self.__menu_changing  

  @changes(items)
  def removeMenu(self, menu):
    self.__items.remove(menu)
    
    observers(menu, 'items').after -= self.__menu_changed  
    observers(menu, 'items').before -= self.__menu_changing  
    
  
