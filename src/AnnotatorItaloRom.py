#!/Users/tzakharko/Documents/Projects/UZH/Italo-Romance/python/pywrapper.sh
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



import sys
sys.dont_write_bytecode = True

from UIToolkit import *
from model import *
from AnnotatorWindow import *
import logging, sys, os
from weakref import ref


from GUI import ModalDialog, Label, Button, Task, application

import objc
objc.setVerbose(1)


class LoggerWriter:
    def __init__(self, level):
        # self.level is really like using log.debug(message)
        # at least in my case
        self.level = level

    def write(self, message):
        # if statement reduces the amount of newlines that are
        # printed to the logger
        if message != '\n':
            self.level(message)

    def flush(self):
        # create a flush method so things can be flushed when
        # the system wants to. Not sure if simply 'printing'
        # sys.stderr is the correct way to do it, but it seemed
        # to work properly for me.
        self.level(sys.stderr)
        
logfilename = os.path.expanduser("~/Desktop/annotation_tool.log")
logging.basicConfig(filename = logfilename, filemode='w', level=logging.INFO)
logging.info("Started up")

sys.stdout = LoggerWriter(logging.getLogger("STDOUT").debug)
sys.stderr = LoggerWriter(logging.getLogger("STDERR").error)      

class AppController(ApplicationController):
  def __init__(self, *args, **kwargs):
    self.__copyState = None
    self.__undoState = None
    ApplicationController.__init__(self, *args, **kwargs)
  
  def applicationLoaded(self):
    self.openDocument(self)
    
  def openDocument(self, sender):
    # open the document
    # document = Document('/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/db/ALT_MaMo_71_picture_story_alt_transcription.anno')
    #
    # create the window for the document
    # Window(controller = AnnotatorWindowController(mock.makeMockDocument()))
    #
    # return
    # #
    #
    from GUI.FileDialogs import request_old_file
    from GUI.Files import FileType
    # make an application window
    #Window(controller = AnnotatorWindowController(mock.makeMockDocument1()))
    ftype = FileType()
    ftype.name   = 'Corpus database'
    ftype.suffix =  'anno'
    
    # show open file window
    ref = request_old_file(file_types=[ftype])
    
    if ref is None:
      Application().quit()
      return
    
    filepath = os.path.join(ref.dir.path, ref.name)
    
    # open the document
    document = Document(filepath)
    
    # create the window for the document
    window = Window(controller = AnnotatorWindowController(document))
    window.title = ref.name
    
    
  # def chunkViewDoubleClick(self, chunkView):
  #   print "Chunk view has been double clicked!"
  #   print Application().firstResponder
  #   print Application().activeWindow
    
  def applicationQuitting(self):
    pass
    
  # ---- copy paste support
  def copyAnnotation(self, sender):
    try: source = Application().activeWindow.controller.selectedView.controller.representedObject
    except AttributeError: return
    
    self.__copyState = makeCopyState(source)
    

  def pasteAnnotation(self, sender):
    if self.__copyState is None: return
    
    try: target = Application().activeWindow.controller.selectedView.controller.representedObject
    except AttributeError: return False
    
    if not self.__copyState.canPaste(target): return
    
    # paste and save the undo state
    self.__undoState = self.__copyState.paste(target)
    
    
  def canCopyAnnotation(self):
    # check the origin
    try: source = Application().activeWindow.controller.selectedView.controller.representedObject
    except AttributeError: return False
    
    return (makeCopyState(source) is not None)
    

  def canPasteAnnotation(self):
    # check the target
    try: target = Application().activeWindow.controller.selectedView.controller.representedObject
    except AttributeError: return False
    
    return (self.__copyState is not None) and (self.__copyState.canPaste(target))
    
  def canUndo(self):
    return (self.__undoState is not None) and (self.__undoState.canUndo())
    
  def undo(self, sender):
    self.__undoState.undo()
    self.__undoState = None
    
  def getStateForMenuItem(self, item):
    if item.name == 'Copy':
      return self.canCopyAnnotation()
    elif item.name == 'Paste':
      return self.canPasteAnnotation()
    elif item.name == 'Undo':
      return self.canUndo()  
  
  
        

mainMenu = MenuList()
mainMenu.addMenu(Menu("File"))
mainMenu['File'].addItem("Open", action = 'openDocument')
mainMenu['File'].addSeparator()
mainMenu['File'].addItem('Close', action = 'closeWindow')
mainMenu.addMenu(Menu("Edit"))
mainMenu['Edit'].addItem('Copy', action = 'copyAnnotation', key='C')
mainMenu['Edit'].addItem('Paste', action = 'pasteAnnotation', key='V')
mainMenu['Edit'].addItem('Undo', action = 'undo', key='Z')
mainMenu.addMenu(Menu("View"))      
mainMenu['View'].addItem('Show lemmas', action = 'toggleShowGloss')

app = Application()
app.menu = mainMenu
app.controller = AppController()
app.run()
