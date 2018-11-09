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


import model, weakref

class CopyState(object):
  def canPaste(self, target):
    return False
    
  def paste(self, target):
    pass
    
    
class UndoState(object):
  def undo(self):
    pass
    
    
# token copy support
class TokenUndoState(UndoState):
  def __init__(self, target):
    assert(isinstance(target, model.Token))
    self.variables = dict(iter(target.variables))
    self.target = weakref.ref(target)

  def canUndo(self):
    target = self.target()
    
    return target is not None and target.__valid__
    
  def undo(self):
    target = self.target()
    
    assert(self.canUndo())
    
    trx = target.__db__.transaction()
    with trx:
      target.variables.copyFrom(self.variables)
    trx.commit()
    
    

class TokenCopyState(CopyState):
  def __init__(self, source):
    assert(isinstance(source, model.Token))
    self.variables = dict(iter(source.variables))
    
  def canPaste(self, target):
    return isinstance(target, model.Token)
    
  def paste(self, target):
    assert(self.canPaste(target))
    
    undoState = TokenUndoState(target)
    
    trx = target.__db__.transaction()
    with trx:
      target.variables.copyFrom(self.variables)
    trx.commit()
    
    return undoState
    
    
# span copy support
class SpanCopyState(CopyState):
  def __init__(self, source):
    assert(isinstance(source, model.Span))
    
    # self.tokens =
    
  

    
    
def makeCopyState(obj):
  if (isinstance(obj, model.Token)):
    return TokenCopyState(obj)
  elif (isinstance(obj, model.Span)):
    print "Attempt to copy a span"
      
  return None
