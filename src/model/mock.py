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



from model import Document
import os, sys

testfile = os.path.join(sys.path[0], '../test.anno')


MockData = (
  dict(id=1, info={}, tokens=tuple("The quick brown fox jumps over the lazy dog".split())),
  dict(id=2, info={}, tokens=tuple("The quick brown fox jumps over the lazy dog".split())),
  dict(id=3, info={}, tokens=tuple("The quick brown fox jumps over the lazy dog".split()))
)
# for i in range(7):
#   MockData = MockData + MockData


MockData1 = (
  dict(id=1, info={}, tokens=tuple(u"'rɔ:sa 'a 'mmɔrta".split())),
  dict(id=2, info={}, tokens=tuple(u"marI:a e  'rrɔ:sa s' a:na skravita pa 'ttand 'anna e ss 'a:na raspɔ:sa 'ɔppa 'bbɔ:ta".split())),
  dict(id=3, info={}, tokens=tuple(u"u 'b:ru:ta 'tjemba".split())) 
)

def makeMockDocument():
  try: os.remove(testfile)
  except(OSError): pass
  
  
  document = Document(testfile)  
  
  # set up a mock example
  trn = document.database.transaction()
  with trn:
    for spandata in MockData:
      span = Document.persistenceSchema.classes.Span(externalID = spandata['id'], info = spandata['info'])
      for tok in spandata['tokens']:
        span.addToken(Document.persistenceSchema.classes.Token(tok))
      document.addSpan(span)
    
    # make some constituents, cause why not  
    phrase = Document.persistenceSchema.classes.Constituent()
    phrase.add(document.spans[0].tokens[3])
    phrase.add(document.spans[0].tokens[2])
    phrase.add(document.spans[0].tokens[4])
    
    phrase = Document.persistenceSchema.classes.Constituent()
    phrase.add(document.spans[0].tokens[0])
    phrase.add(document.spans[0].tokens[1])
    phrase.add(document.spans[0].tokens[3])
    phrase.add(document.spans[0].tokens[4])

    phrase = Document.persistenceSchema.classes.Constituent()
    print phrase.refmark
    phrase.add(document.spans[1].tokens[1])
    phrase.add(document.spans[1].tokens[0])
    
    x = Document.persistenceSchema.classes.DependencyRelation(document.spans[0].constituents[0], document.spans[0].tokens[5])
    x = Document.persistenceSchema.classes.DependencyRelation(document.spans[0].tokens[1], document.spans[0].tokens[1])
    
    document.spans[0].tokens[0].variables['PoS'] = 'Noun'
    document.spans[0].tokens[0].variables['Number'] = 'singular'
    document.spans[0].tokens[0].variables['Gender'] = 'masculine'
    document.spans[0].tokens[0].variables['Focus'] = 'yes'
    
    
    mm = Document.persistenceSchema.classes.ReferenceMark()
    document.spans[0].tokens[0].refmark = mm
    document.spans[1].tokens[0].refmark = mm
    phrase.refmark = mm
    
    document.spans[0].tokens[4].refmark = Document.persistenceSchema.classes.ReferenceMark()
    
    
          
  trn.commit()
  
  return document
  
  
def makeMockDocument1():
  try: os.remove(testfile)
  except(OSError): pass
  
  
  document = Document(testfile)  
  
  # set up a mock example
  trn = document.database.transaction()
  with trn:
    for spandata in MockData1:
      span = Document.persistenceSchema.classes.Span(externalID = spandata['id'], info = spandata['info'])
      for tok in spandata['tokens']:
        span.addToken(Document.persistenceSchema.classes.Token(tok))
      document.addSpan(span)
    
  trn.commit()
  
  return document  