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



from model import Document
import os, sys, json

def make_from_json(jsonData, filename, removeOld = False):
  if removeOld:
    try: os.remove(filename)
    except(OSError): pass
    
  # create the document
  document = Document(filename)  
  
  # set up a mock example
  trn = document.database.transaction()
  with trn:
    document.database.root['documentType'] = jsonData['documentType']
    document.database.root['variety'] = jsonData['variety']
    
    for i, spanData in enumerate(jsonData['spans']):
      span = Document.persistenceSchema.classes.Span(externalID = i, info = spanData['spanInfo'])
      for i, token in enumerate(spanData['tokens']):
        token = Document.persistenceSchema.classes.Token(token)
        try: 
          token.gloss = spanData['lemmas'][i]
        except: pass
        
        span.addToken(token)
      
      document.addSpan(span)
  
  trn.commit()
  document.close()
  
  
jsonfile = sys.argv[1]
outfile  = sys.argv[2]
# jsonData = json.load(sys.stdin)

# outfile = '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/db/ALT_AnCa_11_morf_gen_gramm_transcription.anno'
# jsonfile = '/Users/tzakharko/Documents/Projects/Loporcaro/test.json'

with open(jsonfile) as file:    
    jsonData = json.load(file)

make_from_json(jsonData, outfile, removeOld=True)

print "Created document"


