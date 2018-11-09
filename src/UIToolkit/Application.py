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



from SafeCall import safecall
from observing import observable_property, observers, didChange, willChange

class Application(object):
  __singleton = None
  
  def __new__(cls):
    if cls.__singleton is None:
      return super(Application, cls).__new__(cls)  
    else:
      return cls.__singleton
    
  def __init__(self):
    # make sure we initalise only ONCE
    if type(self).__singleton is not None: return
    
    self.__app = GUI_App()
    self.__app.app = self
    self.__controller = None
    
    from UIToolkit import MenuList
    
    self.__menu = MenuList()
    self.__app.gui_menu_map = {}
    
    type(self).__singleton = self

  def run(self):
    self.__app.run()
    
  def quit(self):    
    # close all windows
    for window in self.windows:
      window.close()
    # quit the application  
    safecall(self.controller).applicationQuitting()
    self.__app._quit()
    
  # --- menu support  
  @observable_property
  def menu(self):
    return self.__menu   
  
  def __menu_will_change(self, menu, context):
    willChange(self, 'menu', context)

  def __menu_has_changed(self, menu, context):
    didChange(self, 'menu', context)

  @menu.setter
  def menu(self, menu):
    if self.__menu is not None:
      observers(self.__menu, 'items').before -= self.__menu_will_change
      observers(self.__menu, 'items').after  -= self.__menu_has_changed
    self.__menu = menu
    if self.__menu is not None:
      observers(self.__menu, 'items').before += self.__menu_will_change
      observers(self.__menu, 'items').after  += self.__menu_has_changed
    
  @menu.changed
  def menu(self, context):
    self.__app.menus, self.__app.gui_menu_map = buildPyGUIMenu(self.menu)
    
  @observable_property
  def controller(self):
    return self.__controller
  
  @controller.setter
  def controller(self, value):
    self.__controller = value
    
  @property
  def windows(self):
    for w in list(self.__app.windows):
      yield w.windowWrapper
    
  @property
  def activeWindow(self):
    w = self.__app.target_window
    if w is None:
      return None
    else:
      return w.windowWrapper
      
  @property
  def firstResponder(self):
    w = self.activeWindow
    
    if w is not None:
      return w.firstResponder
    else:
      return self.controller
  
  @firstResponder.setter
  def firstResponder(self, value):
    w = self.activeWindow
    
    if w is not None:
      w.firstResponder = value
    
      
    
  

# ------ PyGUI components wrappers
import GUI
from GUI.Files import FileType

class GUI_App(GUI.Application):
  def __init__(self):
    super(GUI_App, self).__init__()
    #super(Application, self).__init__(self)
    self.file_type = FileType(name = "", suffix = "*")
    
  def open_app(self):
    safecall(self.app.controller).applicationLoaded()
    
  def setup_menus(self, menu_config):
    super(GUI.Application, self).setup_menus(menu_config)
    for cmd_name, item in self.gui_menu_map.iteritems():
      #print "%s.enabled=%s" % (item, item.action.hasResponder)
      invokable = item.action.canBeInvoked()
      if not invokable:
        menu_config[cmd_name].enabled = False
      else:
        # get the state of the menu item
        responder = item.action.getCurrentTarget()
        state = safecall(responder).getStateForMenuItem(item)
        if state is None:
          state = True
        
        # set the state accordingly
        menu_config[cmd_name].enabled = state is not False
        menu_config[cmd_name].checked = state is 1    
  
  def handle(self, msg, *args, **kwargs):    
    if msg == "_setup_menus":
      self.setup_menus(*args, **kwargs)
      return
    elif msg == "quit_cmd":
      self.app.quit()
      return
        
    # check if its a custom menu item
    item = self.gui_menu_map.get(msg, None)
    if item is not None:
      item.action()
        
    # try to dispatch the message based on the table  
    # print "%s(%s, %s)" % (msg, args, kwargs)
    
  def handle_here(self, msg, *args, **kwargs):
    print 'Handle here is called?'
    self.handle(msg, *args, **kwargs)
    

def buildPyGUIMenu(menu_list):
  """
    Constructs a pyGUI menu from a menu list
    
    Returns a pyGUI menu and a map of commands to menu items (and via versa)
  """  
  from UIToolkit import Menu
  
  pyGUI_menus = [GUI.StdMenus.basic_menus()[0]]
  menumap     = {}
  
  for menu in menu_list:
    pygui_Menu = GUI.Menu(menu.name, ())
    for item in menu:
      if isinstance(item, Menu.Separator):
        pygui_Menu.append('-')
      else:
        if item.key is not None:
          item_name = u"%s/%s" % (item.name, item.key)
        else:
          item_name = item.name
        
        
        cmd_name = "menu_cmd_%s" % id(item)
        menumap[cmd_name] = item
        pygui_Menu.append([item_name, cmd_name])
        
    pyGUI_menus.append(pygui_Menu) 
     
  return (GUI.MenuList(pyGUI_menus), menumap)