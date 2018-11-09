# 
#  model/model.py
#
#  Corpus database definitions
#


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

from observing import *
import logging, persistentdb
import variables



# ======================  The document  structure =================
class Document(object):
  """ The root interface class for interacting with the corpus storage """
  persistenceSchema = persistentdb.PersistenceSchema()
  schemaVersion     = 0.1
  variableDefinitions       = variables.Variables
  variableDefinitionsLookup = dict(((decl.key,decl.value), decl) for decl in variableDefinitions)
  
  def __init__(self, file):
    # load the database
    self.database = persistentdb.DB(file,
                                     persistentdb.SQLStorageEngine, 
                                     schema = Document.persistenceSchema)
                                     
    # make sure that the key variables are initialised
    if self.database.root['__version__'] is None: 
      transaction = self.database.transaction()
      with transaction:
         self.database.root['__version__'] = Document.schemaVersion
         self.database.root['spans'] = []
         self.database.root['constituents'] = []
         self.database.root['dependencies'] = []
         self.database.root['refmarks'] = []
         self.database.root['documentType'] = None
         self.database.root['variety'] = None
      transaction.commit()
      
    if self.database.root['__version__'] > Document.schemaVersion:
      raise ValueError('Database is of newer version that this application can support, please update to the most recent release')   
    
    # link back the document
    self.database.document = self
    
  def close(self):
    self.database.close()
    self.database = None
                               
  # ---- document properties
  @observable_property
  def variety(self):
    return self.database.root['variety']

  @observable_property
  def documentType(self):
    return self.database.root['documentType']
                               
                                     
  # ---- working with spans
  @observable_property 
  def spans(self):
    return tuple(self.database.root['spans'])
    
  def indexOfSpan(self, span):
    return self.database.root['spans'].index(span)
    
  def addSpan(self, span):
    """ Requires an active transaction """    
    self.database.root['spans'] = self.database.root['spans'] + [span]
    return span      
  
  # ---- working with constituents
  @observable_property
  def constituents(self):
    return tuple(self.database.root['constituents'])
  
  def findConstituentsForSpan(self, span):
    return tuple(o for o in self.database.root['constituents'] if o.span is span)
    
  def removeConstituent(self, constituent):
    if constituent not in self.database.root['constituents']:
      raise ValueError("Constituent not in the database")
    
    # if there are any relations over this constituent, we can't delete
    if len(tuple(r for r in self.dependencies if (r.controller is constituent) or (r.target is constituent)))>0:
      raise ValueError("Cannot delete a constituent that is part of a dependency relation")
      
      
    span = constituent.span  
    if span is not None:
      willChange(span, 'constituents', ObservingContext(action = 'remove', object = constituent))
    willChange(self, 'constituents', ObservingContext(action = 'remove', object = constituent))
    constituent._tokens=[]
    constituents = self.database.root['constituents']
    constituents.remove(constituent)
    self.database.root['constituents']= constituents
    didChange(self, 'constituents', ObservingContext(action = 'remove', object = constituent))
    if span is not None:
      didChange(span, 'constituents', ObservingContext(action = 'remove', object = constituent))
    
    
  # ---- working with dependencies
  @observable_property
  def dependencies(self):
    return tuple(self.database.root['dependencies'])
    
  def findDependenciesForSpan(self, span):
    return tuple(o for o in self.database.root['dependencies'] if o.span is span)
  
  def removeDependency(self, dependency):
    willChange(self, 'dependencies', ObservingContext(action = 'remove', object = dependency))
    willChange(dependency.span, 'dependencies', ObservingContext(action = 'remove', object = dependency))
    dependencies = list(self.database.root['dependencies'])
    dependencies.remove(dependency)
    self.database.root['dependencies'] = dependencies
    didChange(dependency.span, 'dependencies', ObservingContext(action = 'remove', object = dependency))
    didChange(self, 'dependencies', ObservingContext(action = 'remove', object = dependency))

  # ---- working with refmarks
  @observable_property
  def refmarks(self):
    return tuple(self.database.root['refmarks'])
  

# ======================  Corpus tokenization =================
@Document.persistenceSchema.Persistent
class Token(object):
  """ Describes a token in a corpus """
  
  # ---- properties
  @observable_property 
  def span(self):
    """ The span this token belongs to """
    return getattr(self, '_span', None)
    
  @property 
  def externalID(self):
    """ The ID of the token in the external text """
    return getattr(self, '_externalID', None)

  # @observable_property
  # def transcription(self):
  #   """ The unicode transcription of the token """
  #   return getattr(self, '_transcription', u"")
  #
  # @transcription.setter
  # def transcription(self, value):
  #   guard(isinstance(value, basestring), TypeError("Token transcription must be a string, got %s" % value))
  #
  #   self._transcription = unicode(value)
    
  @observable_property 
  def index(self):
    """ Get the index of the token in the span"""
    if self.span is None:
      return None
    else:
      return self.span.indexOfToken(self)
      

  # ---- representation (mostly for debugging)
  def __repr__(self):
    return '"%s"' % self.transcription
    
  # ---- business logic    
  def __init__(self, transcription):
    guard(isinstance(transcription, basestring), TypeError("Token transcription must be a string, got %s" % transcription))
    self.transcription = unicode(transcription)
    
    
  # ---- variables      
  @observable_property
  def variables(self):
    return VariablesAccessor(self)
  
  @variables.changing
  def variables(self, context):
    willChange(self, 'mnemonic', {})

  @variables.changed
  def variables(self, context):
    didChange(self, 'mnemonic', {})
    
    
  @observable_property
  def mnemonic(self):
    return self.variables.getMnemonic()
    
  # ---- refmarks
  @observable_property
  def refmark(self):
    return getattr(self, '_refmark', None)
    
  @refmark.setter
  def refmark(self, value):
    # change the refmark
    old = self.refmark
    self._refmark = value
    
    # update the refmark state, if needed
    if (old is not None and not old.isReferenced) or value is not None:
      willChange(self.__db__.document, 'refmarks', {})
      refmarks = self.__db__.root['refmarks']
      if value is not None and value not in refmarks: refmarks.append(value)
      for refmark in refmarks: willChange(refmark, 'index', {})
      if old in refmarks and not old.isReferenced: refmarks.remove(old)
      self.__db__.root['refmarks'] = refmarks
      didChange(self.__db__.document, 'refmarks', {})
      for refmark in refmarks: didChange(refmark, 'index', {})
    
    
# ======================  Reference labels =================
@Document.persistenceSchema.Persistent
class ReferenceMark(object):
  @observable_property
  def index(self):
    try:
       return self.__db__.root['refmarks'].index(self)
    except:
      return None    
      
  @property
  def tokens(self):
    for span in self.__db__.root['spans']:
      for token in span.tokens:
        if token.refmark is self:
          yield token
          
  @property
  def isReferenced(self):
    for span in self.__db__.root['spans']:
      for token in span.tokens:
        if token.refmark is self:
          return True
    
    return False
    
      
    
    
@Document.persistenceSchema.Persistent  
class Span(object):
  """ Describes a unit of text (span) that can be annotated """
  
  # ---- properties
  @property 
  def externalID(self):
    """ The ID of the span in the external text """
    return self._externalID

  @property 
  def spanInfo(self):
    """ Auxiliary information such as translation, speaker etc. """
    return getattr(self, '_spanInfo', {})

  @property
  def headerLabel(self):
    spanInfo = self.spanInfo
    spantype = spanInfo.get("type", "Utterance")
    spanid   = spanInfo.get("id", self.index)
    subid    = spanInfo.get("subid", '')
    return u"%s %s%s" % (spantype, spanid, subid)


  @property
  def auxiliaryLabel(self):
    spanInfo = self.spanInfo
    speaker = spanInfo.get("speakerCode", None)
    translation   = spanInfo.get("translation", "(no translation)")
    if speaker is None:
      return translation
    else:
      return u"%s: %s" % (speaker, translation)

  @observable_property 
  def tokens(self):
    """ The span tokens """
    return tuple(self._tokens)

  @observable_property 
  def index(self):
    """ The index of this span in the document """
    return self.__db__.document.indexOfSpan(self)
    
  def indexOfToken(self, token):
    guard(token in self._tokens, KeyError("Token %s not in the span" % token))
    return self._tokens.index(token)
    
  @observable_property
  def constituents(self):
    return self.__db__.document.findConstituentsForSpan(self)

  @observable_property
  def dependencies(self):
    return self.__db__.document.findDependenciesForSpan(self)
  
    
  # ---- representation (mostly for debugging)
  def __repr__(self):
    tokenline = " ".join(t.transcription for t in self.tokens)
    
    return '<"%s">(id=%s)' % (tokenline, self.externalID)
    
  # ---- business logic    
  def __init__(self, externalID = None, info = None):
    """ Create a new span with tokens. Token should be specified as tuple of (id, transcription) """
    if externalID is not None: self._externalID = externalID
    if info is not None: self._spanInfo   = info
    
    self._tokens = []
    
  def removeToken(self, token):
    """ Remove a token from span """
    guard(token in self._tokens, KeyError("Token %s not in the span" % token))
    guard(len(self._tokens)>1, RuntimeError("Cannot create empty span"))

    token._span = None
    
    # remove teh token
    willChange(self, 'tokens', ObservingContext(action = 'remove', object = token))
    tokens = list(self._tokens)
    tokens.remove(token)
    self._tokens = tokens
    didChange(self, 'tokens', ObservingContext(action = 'remove', object = token))
    
      
  def addToken(self, token, after = None, before = None, at = None):
    """ Adds a token to the span """
    guard(token not in self._tokens, KeyError("Token %s is already part of the span" % token))
    guard(token.span is None, RuntimeError("Token %s is part of another span, can't insert" % token))
    
    # different styles of insertion
    if (after is not None) and (before is None) and (at is None):
      at = self.indexOfToken(after)+1
      after = None
    elif (after is None) and (before is not None) and (at is None):
      at = self.indexOfToken(before)
      before = None
    elif (after is None) and (before is None) and (at is None):  
      at = len(self._tokens)
      
    guard((after is None) and (before is None) and (at is not None), RuntimeError("Invalid operation"))
    
    # add the token
    willChange(self, 'tokens', ObservingContext(action = 'add', object = token))
    tokens = list(self._tokens)
    tokens.insert(at, token)
    self._tokens = tokens
    token._span = self
    didChange(self, 'tokens', ObservingContext(action = 'add', object = token))
    
  

  
# ======================  Constituent =============
@Document.persistenceSchema.Persistent
class Constituent(object):
  """ 
    Describes a constituent (a collection of one or more tokens).
    
    Constituents can be discontinuous (but lets hope they are not).
    Constituents are automatically removed from the db if they don't contain 
    any tokens. Constituents can't span across spans (bah)  
  """
  # ---- properties
  @property 
  def span(self):
    """ The tokens contained in this constituent, left to right """
    if self.isEmpty: 
      return None
    else:
      return self._tokens[0].span
      
  @observable_property
  def isEmpty(self): 
    return len(self._tokens) == 0

  @observable_property 
  def tokens(self):
    """ The span tokens """
    return tuple(self._tokens)
 
  def indexOfToken(self, token):
    """ The index of this span in the document """
    return self._tokens.index(token)
    
  def __contains__(self, token):
    return token in self._tokens
    
  def __len__(self):
    return len(self._tokens)
    
  # ---- representation (mostly for debugging)
  def __repr__(self):
    tokenline = " ".join(t.transcription for t in self.tokens)
    
    return '[%s]' % tokenline
    
  # ---- business logic    
  def __init__(self):
    self._tokens = []
    
  # def __state_changed(self):
  #   """ Make the object persistent if it contains information and remove if it contains none """
  #   constituents = list(self.__db__.root['constituents'])
  #   if self.isEmpty and (self in constituents):
  #     constituents.remove(self)
  #     self.__db__.root['constituents'] = constituents
  #   elif (not self.isEmpty) and (self not in constituents):
  #     constituents.append(self)
  #     self.__db__.root['constituents'] = constituents
      
    
  def add(self, token):
    """ Add a token to the constituent """  
    # can't add the same token twice
    if token in self: return
    
    # make sure that the span is corrent
    guard((self.span is None) or (self.span is token.span), ValueError("Constituent cannot cross spans!"))
    
    # check if the constituent will become valid (non empty), 
    # which means that it needs to be added to the constituent list
    willBecomeNonEmpty = self.isEmpty
    
    if willBecomeNonEmpty:
      willChange(self.__db__.document, 'constituents', ObservingContext(action = 'add', object = self))
      willChange(token.span, 'constituents', ObservingContext(action = 'add', object = self))
    
    # insert the token in sorted order
    willChange(self, 'tokens', ObservingContext(action = 'add', object = token))
    tokens = self._tokens + [token]
    tokens.sort(key=lambda t: t.index)
    self._tokens = tokens
    didChange(self, 'tokens', ObservingContext(action = 'add', object = self))
    
    if willBecomeNonEmpty:
      self.__db__.root['constituents'] += [self]
      
      didChange(self.__db__.document, 'constituents', ObservingContext(action = 'add', object = self))
      didChange(token.span, 'constituents', ObservingContext(action = 'add', object = self))
    
    return self
  
  def remove(self, token):
    """ Add a token from the constituent. """  
    # can't add the same token twice
    guard(token in self, KeyError("Token %s not part of the constituent" % token))
        
    # check if the constituent will become invalid ( empty), 
    # which means that it needs to be removed from the constituent list
    willBecomeEmpty = len(self._tokens) == 1
    
    if willBecomeEmpty:
      # if there are any relations over this constituent, we can't delete
      if len(tuple(r for r in self.__db__.document.dependencies if (r.controller is self) or (r.target is self)))>0:
        raise ValueError("Cannot delete a constituent that is part of a dependency relation")
      
      willChange(self.__db__.document, 'constituents', ObservingContext(action = 'remove', object = self))
      willChange(token.span, 'constituents', ObservingContext(action = 'remove', object = self))
        
        
    # remove the token
    willChange(self, 'tokens', ObservingContext(action = 'remove', object = token))
    tokens = list(self._tokens)
    tokens.remove(token)
    self._tokens = tokens
    didChange(self, 'tokens', ObservingContext(action = 'remove', object = token))
    
    if willBecomeEmpty:
      l = list(self.__db__.root['constituents'])
      l.remove(self)
      self.__db__.root['constituents'] = l
      
      didChange(self.__db__.document, 'constituents', ObservingContext(action = 'remove', object = self))
      didChange(token.span, 'constituents', ObservingContext(action = 'remove', object = self))

    
    return self   
    
  # ---- variables      
  @observable_property
  def mnemonic(self):
    return self.variables.getMnemonic(separator=', ')  
    
  @observable_property
  def variables(self):
    return VariablesAccessor(self)

  @variables.changing
  def variables(self, value):
    willChange(self, 'mnemonic', {})

  @variables.changed
  def variables(self, value):
    didChange(self, 'mnemonic', {})
  
  
# ======================  Dependency relation =================    
@Document.persistenceSchema.Persistent
class DependencyRelation(object):
  """ 
    A dependency relation between two constituents. 
    Tokens also count as constituents for this purpose
  """
  @observable_property
  def span(self):
    controller = self.controller
    target = self.target
    
    guard((controller.span is not None) and (controller.span is target.span), ValueError("Dependency relation cannot cross spans"))
    
    return controller.span
  
  # ---- representation (mostly for debugging)
  def __repr__(self):
    return 'Dependency(%s --> %s)' % (self.controller, self.target)
    
  # ---- business logic    
  def __init__(self, controller, target):
    guard((controller.span is not None) and (controller.span is target.span), ValueError("Dependency relation cannot cross spans"))
    self.controller = controller
    self.target     = target  
    
    
    willChange(self.__db__.document, 'dependencies', ObservingContext(action = 'add', object = self))
    willChange(self.span, 'dependencies', ObservingContext(action = 'add', object = self))
    dependencies = list(self.__db__.root['dependencies'])
    dependencies.append(self)
    self.__db__.root['dependencies'] = dependencies
    didChange(self.span, 'dependencies', ObservingContext(action = 'add', object = self))
    didChange(self.__db__.document, 'dependencies', ObservingContext(action = 'add', object = self))
    
    
    
  # ---- variables      
  @observable_property
  def mnemonic(self):
    return self.variables.getMnemonic(separator=', ')  
    
  @observable_property
  def variables(self):
    return VariablesAccessor(self)

  @variables.changing
  def variables(self, value):
    willChange(self, 'mnemonic', {})

  @variables.changed
  def variables(self, value):
    didChange(self, 'mnemonic', {})



  
# ======================  Variables =================  
class VariablesAccessor(object):
  def __init__(self, obj):
    self.obj = obj
    
  def __getitem__(self, key):
    """ Return value for the given key """  
    value = getattr(self.obj, '_variables', {}).get(key, None)
    return value
    
  def __setitem__(self, key, value):
    """ Set the value for the given key """  
    if not (value is None or value in self.getValidValuesForKey(key)):
      raise ValueError("Invalid value")
      
    # get the variable dictionary  
    variables = getattr(self.obj, '_variables', {})
    if variables.get(key, None) == value:
      return
      
    context = ObservingContext(key = key, old = variables.get(key, None), new = value )
    willChange(self.obj, 'variables', context)
    if value is None:
      del variables[key]
    else:
      variables[key] = value
      
    # set the new variables dictionary
    if len(variables) == 0: 
      del self.obj._variables
    else:
      self.obj._variables = variables
    didChange(self.obj, 'variables', context)
    
    
  @property
  def __conditionEnvironment(self):
    """ Construct the environment for evaluating the condition """
    return  dict(
      # flags of object type
      isToken       = isinstance(self.obj, Token),
      isConstituent = isinstance(self.obj, Constituent),
      isDependency  = isinstance(self.obj, DependencyRelation),
      # variable accessor (this object)
      variables     = self,
      # dialect variety, TODO
      variety       = self.obj.__db__.document.variety,
      documentType  = self.obj.__db__.document.documentType
    )

  def getValidValuesForKey(self, key):
    """ Return all valid values for the given key, given the current state """
    # setup the condition evaluation environment
    env = self.__conditionEnvironment
    
    # enumerate all the valid values for the key
    varlist = self.obj.__db__.document.variableDefinitions
    values  = (decl.value for decl in varlist if decl.key == key and eval(decl.condition, env))
    
    return tuple(values)
    
  def enumeratePossibleKeys(self):
    """ Return all keys that can be set for the object, given the current state """
    env = self.__conditionEnvironment
    
    keys = []
    
    varlist = self.obj.__db__.document.variableDefinitions
    
    for decl in varlist:
      if decl.key in keys: continue
    
      if eval(decl.condition, env): keys.append(decl.key)
        
    return  keys
    
  def __iter__(self):
    """ Iterates all relevant keys and their values """
    for key in self.enumeratePossibleKeys():
      yield (key, self[key])
    
    
  def getMnemonic(self, separator=u"."):
    """ Create the short menmonic description of the variables """
    mnemonic = []
    
    varlist = self.obj.__db__.document.variableDefinitionsLookup
    
    for keyvalue in self:
      decl = varlist.get(keyvalue, None)
      if decl is None or decl.mnemonic == "": continue
      
      mnemonic.append(decl.mnemonic)
      
    if len(mnemonic) == 0:
      return ""
    else:
      return separator.join(mnemonic)
       
    

  
  
# ======================  Error handling =================
def guard(condition, exception):
  if not condition:
    raise exception
  
