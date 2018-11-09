##############################################################
# context.py
#
# Defines the graphics context API
# Ok, for now we are using pygui

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



from GUI import Font as PyGUIFont
import GUI.StdFonts

from UIToolkit.Drawing import Context


class Font(object):
    __fontmap = {}
    
    @classmethod
    def makeFont(cls, value):
      if isinstance(value,Font):
        return value
      
      # interpret value as family
      return Font(value, size, ())
    
    @classmethod
    def _makeWithPyGUIFont(cls, pyguifont):
        self = object.__new__(cls)
        self._pyguifont = pyguifont
        return self       
    
    def __new__(cls, family, size, style):
        style = frozenset(style)
        
        try:
            self = cls.__fontmap[(family, size, style)]
        except KeyError:
            pyguifont = PyGUIFont(family, size, style)
            self = cls.__fontmap[(family, size, style)] = cls._makeWithPyGUIFont(pyguifont)
            self._pyguifont = pyguifont

        return self
        
    def makeCurrent(self):
        Context.font = self    
    
    def getWidthForString(self, string):
        return self._pyguifont.width(string)
    
    @property
    def leading(self): return self._pyguifont.leading
        
    @property
    def descent(self): return self._pyguifont.descent

    @property
    def ascent(self): return self._pyguifont.ascent

    @property
    def height(self): return self._pyguifont.line_height
    
    @property
    def familyname(self): return self._pyguifont.family

    @property
    def size(self): return self._pyguifont.size
        
        
Font.defaultFont = Font._makeWithPyGUIFont(GUI.StdFonts.application_font)
Font.defaultFont = Font(Font.defaultFont.familyname, int(Font.defaultFont.size*1.4), [])



