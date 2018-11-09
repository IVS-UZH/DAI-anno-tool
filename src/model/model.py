# encoding: utf-8
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
import logging, persistentdb, weakref
import variables as variables
from gloss import make_gloss_for_token
import xml.etree.cElementTree as ET


# ======================  The document  structure =================
class Document(object):
  """ The root interface class for interacting with the corpus storage """
  persistenceSchema = persistentdb.PersistenceSchema()
  schemaVersion     = 0.2
  variableDefinitions       = variables.Variables
  variableDefinitionsLookup = dict(((decl.key,decl.value), decl) for decl in variableDefinitions)
  variableKeys              = sorted(tuple(set(decl.key for decl in variableDefinitions)))
  variableValues              = sorted(tuple(set(decl.value for decl in variableDefinitions)))
  
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
         self.database.root['documentType'] = None
         self.database.root['variety'] = None
      transaction.commit()
      
    if self.database.root['__version__'] > Document.schemaVersion:
      raise ValueError('Database is of newer version that this application can support, please update to the most recent release')   
    
    # link back the document
    self.database.document = self
    
    # run migrations
    self.__migration()
    
    
    # refmark index support
    self._refmarkList = {}
    
  def close(self):
    self.database.close()
    self.database = None
                                   
  # ---- document properties
  @observable_property
  def variety(self):
    return self.database.root['variety']

  @observable_property
  def documentType(self):
    if self.database.root['documentType'] == "Questionnaire":
      return "questionnaire"
    else:
      return "(semi-)spontaneous speech"
                               
                                     
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
  
  # ---- migrations
  def __migration(self):
    transaction = self.database.transaction()
    with transaction:
      # add refmarks
      for constituent in self.constituents:
        if not hasattr(constituent, 'refmark'):
          constituent.refmark = None
          
      # replace perfect by past for participles
      for span in self.spans:
        for token in span.tokens:
          if (token.variables.get_value_without_checks('PoS') == 'Verb') and (token.variables.get_value_without_checks('Mode') == 'participle') and (token.variables.get_value_without_checks('Tense/Aspect') == 'perfect'):
            logging.info((u"Migrating %s tense/aspect" % token).encode("utf-8"))
            token.variables['Tense/Aspect'] = 'past'
            
          if (token.variables.get_value_without_checks('PoS') == 'Pronoun') and (token.variables.get_value_without_checks('Type') == 'WH'):
            logging.info((u"Migrating %s WH pronoun" % token).encode("utf-8"))
            token.variables['Type'] = 'interrogative'
            
          
            
              
              
      # change PhraseType:Clause to PhraseType:Complement Clause
      # for constituent in self.constituents:
      #   if constituent.variables.get_value_without_checks('PhraseType') == "Clause":
      #     logging.info((u"Migrating PhraseType:Clause to  PhraseType:Complement Clause for %s" % constituent).encode("utf-8"))
      #     constituent.variables['PhraseType'] = u"Complement clause"

      # change PhraseType:Complement clause to PhraseType:Clause
      for constituent in self.constituents:
        if constituent.variables.get_value_without_checks('PhraseType') == "Complement clause":
          logging.info((u"Migrating PhraseType:Complement clause to  PhraseType:Clause for %s" % constituent).encode("utf-8"))
          constituent.variables['PhraseType'] = u"Clause"
          
      # replace Default=No by Default=no 
      for span in self.spans:
        for token in span.tokens:
          if (token.variables.get_value_without_checks('Default') == 'No'):
            logging.info((u"Migrating %s Default No to no" % token).encode("utf-8"))
            token.variables['Default'] = 'no'
          
              
    transaction.commit()
    
  @property
  def constituents(self):
    return self.database.objectsByClass(Constituent)
    
  @property
  def dependencies(self):
    return self.database.objectsByClass(DependencyRelation)
    
  
  # # ---- working with constituents
  # @observable_property
  # def constituents(self):
  #   return tuple(self.database.root['constituents'])
  #
  # def findConstituentsForSpan(self, span):
  #   return tuple(o for o in self.database.root['constituents'] if o.span is span)
  #
  # def removeConstituent(self, constituent):
  #   if constituent not in self.database.root['constituents']:
  #     raise ValueError("Constituent not in the database")
  #
  #   # if there are any relations over this constituent, we can't delete
  #   if len(tuple(r for r in self.dependencies if (r.controller is constituent) or (r.target is constituent)))>0:
  #     raise ValueError("Cannot delete a constituent that is part of a dependency relation")
  #
  #
  #   span = constituent.span
  #   if span is not None:
  #     willChange(span, 'constituents', ObservingContext(action = 'remove', object = constituent))
  #   willChange(self, 'constituents', ObservingContext(action = 'remove', object = constituent))
  #   constituent._tokens=[]
  #   constituents = self.database.root['constituents']
  #   constituents.remove(constituent)
  #   self.database.root['constituents']= constituents
  #   didChange(self, 'constituents', ObservingContext(action = 'remove', object = constituent))
  #   if span is not None:
  #     didChange(span, 'constituents', ObservingContext(action = 'remove', object = constituent))
  #
  #
  # # ---- working with dependencies
  # @observable_property
  # def dependencies(self):
  #   return tuple(self.database.root['dependencies'])
  #
  # def findDependenciesForSpan(self, span):
  #   return tuple(o for o in self.database.root['dependencies'] if o.span is span)
  #
  # def removeDependency(self, dependency):
  #   willChange(self, 'dependencies', ObservingContext(action = 'remove', object = dependency))
  #   willChange(dependency.span, 'dependencies', ObservingContext(action = 'remove', object = dependency))
  #   dependencies = list(self.database.root['dependencies'])
  #   dependencies.remove(dependency)
  #   self.database.root['dependencies'] = dependencies
  #   didChange(dependency.span, 'dependencies', ObservingContext(action = 'remove', object = dependency))
  #   didChange(self, 'dependencies', ObservingContext(action = 'remove', object = dependency))

  # ---- working with refmarks
  @observable_property
  def refmarks(self):
    return self.database.objectsByClass(ReferenceMark)
    
  def __refmarkDisapeared(self, wref):
    print wref, 'dissapeared'
    
    index = self._refmarkList[wref]
    del self._refmarkList[wref]
    
    # adjust the refmark indices
    refmark_with_changed_indices = [kv[0] for kv in self._refmarkList.iteritems() if kv[1] > index]
    for ref in refmark_with_changed_indices:
      refmark = ref()
      if refmark is not None:
        willChange(refmark, 'index', {})
      self._refmarkList[ref] = self._refmarkList[ref] - 1
      if refmark is not None:  
        didChange(refmark, 'index', {})  
  
  def getRefmarkIndex(self, refmark):
    if refmark not in self._refmarkList:
      ref = WeakKey(refmark, self.__refmarkDisapeared)
      self._refmarkList[ref] = len(self._refmarkList)
          
    return  self._refmarkList[refmark]
 
  # ---- variables
  @classmethod
  def all_variable_names(cls):
    return sorted(tuple(frozenset(key for key,val in variables.Variables)))
    
  # ---- XML generation
  def constructXMLTree(self):
    # core elements
    root = ET.Element("AnnoToolDocument", version="1.0", variety = self.variety, type = self.documentType)
    tokens_xml = ET.SubElement(root, "Tokens")
    spans_xml = ET.SubElement(root,"Spans")
    constituents_xml = ET.SubElement(root,"Constituents")
    dependencies_xml = ET.SubElement(root,"DependencyRelations")

    item_id = 1
    span_id = 1
    dependency_id = 1

    span_id_map = dict()
    item_id_map = dict()
    
    # TODO: relations
    # TODO: refmarks
    
    for span in self.spans:
      span_xml = span.toXML()
      span_xml.set("id", str(span_id))
  
      for token in span.tokens:
        token_xml = token.toXML()
        token_xml.set("id", str(item_id))
        token_xml.set("span_id", str(span_id))
    
        item_id_map[token] = item_id
    
        tokens_xml.append(token_xml)
        item_id = item_id + 1
    
      span_id_map[span] = span_id
  
      spans_xml.append(span_xml)
      span_id = span_id + 1

    for constituent in self.constituents:
      constituent_xml = constituent.toXML(item_id_map)
      constituent_xml.set("id", str(item_id))
  
      item_id_map[constituent] = item_id
  
      constituents_xml.append(constituent_xml)
      item_id = item_id + 1
       

    for dependency in self.dependencies:
      dependency_xml = dependency.toXML(item_id_map)
      dependency_xml.set("id", str(dependency_id))
  
      dependencies_xml.append(dependency_xml)
      dependency_id = dependency_id + 1
      
    
    # assemble the tree
    return ET.ElementTree(root)
    
    
    
    

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
    self.refmark = None
    
    
  # ---- variables      
  @observable_property
  def gloss(self):
    return getattr(self, '_gloss', '')
  
  @gloss.setter
  def gloss(self, value):
    value = unicode(value)
    self._gloss = value  
  
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
    gl = make_gloss_for_token(self)
    if gl is None: 
      if self.gloss is not None:
        return self.gloss
      else:
        return u""
    else:
      return gl
    
    #return u"%s -- %s" % (self.variables.getMnemonic(), make_gloss_for_token(self)) 
    
  def getClosestConstituent(self):
    # find the constituents that contain this token
    constituents = [c for c in self.span.constituents if self in set(c.tokens)]
    # and now only consider consituents which do not contain other constituents
    result = []
    for constituent in constituents:
      t0 = set(constituent.tokens)
      minimal = True
      for c in constituents:
        t1 = set(c.tokens)
        if len(t1)<len(t0): minimal = minimal and not (t1 < t0)
      if minimal:
        result.append(constituent)
    return result
    
  def toXML(self):
    element = ET.Element("Token", transcription = self.transcription, lemma = self.gloss, gloss = self.mnemonic, index_in_span=str(self.index))
    if(self.refmark is not None):
      element.set("refmark", str(self.refmark.index))
    element.append(self.variables.toXML())

    return element


    
# ======================  Reference labels =================
@Document.persistenceSchema.Persistent
class ReferenceMark(object):
  @observable_property
  def index(self):
    return self.__db__.document.getRefmarkIndex(self)
      
  # @property
  # def tokens(self):
  #   for span in self.__db__.root['spans']:
  #     for token in span.tokens:
  #       if token.refmark is self:
  #         yield token
          
    
  
    
    
@Document.persistenceSchema.Persistent  
class Span(object):
  """ Describes a unit of text (span) that can be annotated """
  # ---- change notification
  def __beforeRollback__(self):
    willChange(self, 'tokens', ObservingContext(action='rollback'))
    willChange(self, 'constituents', ObservingContext(action='rollback'))
    willChange(self, 'dependencies', ObservingContext(action='rollback'))
    
  def __afterRollback__(self):
    didChange(self, 'tokens',  ObservingContext(action='rollback'))
    didChange(self, 'constituents', ObservingContext(action='rollback'))
    didChange(self, 'dependencies', ObservingContext(action='rollback'))
  
  # ---- properties
  @property 
  def externalID(self):
    """ The ID of the span in the external text """
    return self._externalID

  @property 
  def spanInfo(self):
    """ Auxiliary information such as translation, speaker etc. """
    return getattr(self, '_spanInfo', {})

  @observable_property
  def headerLabel(self):
    spanInfo = self.spanInfo
    spantype = spanInfo.get("type", "Utterance")
    spanid   = spanInfo.get("id", 0) #self.index)
    subid    = spanInfo.get("subid", '')
    header = u"%s %s%s" % (spantype, spanid, subid)
    
    speaker = spanInfo.get("speakerCode", None)
    
    if speaker is None:
      return header
    else:
      return u"%s (Speaker %s)" % (header, speaker)
      
    
  @observable_property
  def translation(self):
    return self.spanInfo.get("translation", "(no translation)")  
    
  @translation.setter
  def translation(self, value):
    value = unicode(value)
    spanInfo = self.spanInfo
    spanInfo['translation'] = value
    self._spanInfo = spanInfo

  # ---- span objects
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
    return tuple(self._constituents)

  @observable_property
  def dependencies(self):
    return tuple(self._dependencies)
  
    
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
    self._constituents = []
    self._dependencies = []
    
  def canRemoveToken(self, token):
    guard(token in self._tokens, KeyError("Token %s not in the span" % token))
    if(len(self._tokens)==1):
      return False
      
    if len(tuple(r for r in self.dependencies if (r.controller is token) or (r.target is token)))>0:
      return False
      
    for constituent in self.constituents:
      if (token in constituent) and (len(constituent.tokens) == 1):
        return False
        
    return True
    
    
    
    
  def removeToken(self, token):
    """ Remove a token from span """
    guard(token in self._tokens, KeyError("Token %s not in the span" % token))
    guard(self.canRemoveToken(token), ValueError("Cannot safely delete token"))
    print(self.canRemoveToken(token))
    
    assert(len(self._tokens)>1)
    
    # if the token is part of a dependency, we can't delete it
    if len(tuple(r for r in self.dependencies if (r.controller is token) or (r.target is token)))>0:
      raise RuntimeError("Cannot delete a token that is part of a dependency relation")
    
    # remove the token from all cosntituents
    for constituent in self.constituents:
      if token in constituent: 
        try:
          constituent.remove(token)
        except:
          raise RuntimeError("Cannot remove %s from %s" % (token, constituent))
    
    # remove the token
    token._span = None
    
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
    
    
  def removeConstituent(self, constituent):
    assert(constituent.span is self)
    if len(tuple(r for r in self.dependencies if (r.controller is constituent) or (r.target is constituent)))>0:
      raise ValueError("Cannot delete a constituent that is part of a dependency relation")      
    
    
    willChange(self, 'constituents', ObservingContext(action='remove', object=constituent))
    constituents = list(self._constituents)
    constituents.remove(constituent)
    self._constituents = constituents
    didChange(self, 'constituents', ObservingContext(action='remove', object=constituent))

  def removeDependency(self, dependency):
    assert(dependency.span is self)
    willChange(self, 'dependencies', ObservingContext(action='remove', object=dependency))
    dependencies = list(self._dependencies)
    dependencies.remove(dependency)
    self._dependencies = dependencies
    didChange(self, 'dependencies', ObservingContext(action='remove', object=dependency))
    
    
  def toXML(self):
    spanInfo = self.spanInfo
    spantype = spanInfo.get("type", "Utterance")
    speaker = spanInfo.get("speakerCode", "")
    translation = self.translation
    
    element = ET.Element("Span", type = spantype, speaker = speaker, translation = translation, label=str(spanInfo.get("id", 0)), index_in_document=str(self.index))

    return element
  

  
# ======================  Constituent =============
@Document.persistenceSchema.Persistent
class Constituent(object):
  """ 
    Describes a constituent (a collection of one or more tokens).
    
    Constituents can be discontinuous (but lets hope they are not).
    Constituents are automatically removed from the db if they don't contain 
    any tokens. Constituents can't span across spans (bah)  
  """
  # -- change notification
  def __beforeRollback__(self):
    willChange(self, 'tokens', ObservingContext(action='rollback'))
    
  def __afterRollback__(self):
    didChange(self, 'tokens',  ObservingContext(action='rollback'))
    
  # def __loaded__(self):
  #   print "Loaded %s" % self
  #   if not hasattr(self, 'refmark'):
  #     self.refmark = None
  
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
    
  def getDirectlyContainedTokens(self):
    constituents = set(self.span.constituents)
    
    all_tokens = set(self.tokens)
    
    final_tokens = set(self.tokens)
    
    
    for c in constituents:
      other_tokens = set(c.tokens)
      
      if all_tokens.issuperset(other_tokens) and not other_tokens.issuperset(all_tokens):
        final_tokens = final_tokens - other_tokens
    
    return list(final_tokens)
 
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
    self.refmark = None
   
  def add(self, token):
    """ Add a token to the constituent """  
    # can't add the same token twice
    if token in self: return
    
    # check span consistency
    guard((self.span is None) or (self.span is token.span), ValueError("Constituent cannot cross spans!"))
    
    
    # check if the constituent will become valid (non empty), 
    # which means that it needs to be added to the constituent list
    willBecomeNonEmpty = self.isEmpty
    
    if willBecomeNonEmpty:
      willChange(token.span, 'constituents', ObservingContext(action = 'add', object = self))
    
    # insert the token in sorted order
    willChange(self, 'tokens', ObservingContext(action = 'add', object = token))
    tokens = list(self._tokens)
    tokens.append(token)
    tokens.sort(key=lambda t: t.index)
    self._tokens = tokens
    didChange(self, 'tokens', ObservingContext(action = 'add', object = self))
    
    if willBecomeNonEmpty:
      constituents = list(token.span._constituents)
      constituents.append(self)
      token.span._constituents = constituents
      didChange(token.span, 'constituents', ObservingContext(action = 'add', object = self))
    
    return self
    
  def remove(self, token):
    """ Add a token from the constituent. """  
    # can't add the same token twice
    guard(token in self, KeyError("Token %s not part of the constituent %s" % (token, self)))
    assert(self.span is token.span)
        
    # check if the constituent will become invalid ( empty), 
    # which means that it needs to be removed from the constituent list
    if len(self._tokens) == 1:
      raise ValueError("Cannot remove the sole token of a constituent")      
        
        
    # remove the token
    willChange(self, 'tokens', ObservingContext(action = 'remove', object = token))
    tokens = list(self._tokens)
    tokens.remove(token)
    self._tokens = tokens
    didChange(self, 'tokens', ObservingContext(action = 'remove', object = token))
    
    return self   
    
  # ---- variables      
  @observable_property
  def mnemonic(self):
    return self.variables.getMnemonic(separator='\n')  
    
  @observable_property
  def variables(self):
    return VariablesAccessor(self)

  @variables.changing
  def variables(self, value):
    willChange(self, 'mnemonic', {})

  @variables.changed
  def variables(self, value):
    didChange(self, 'mnemonic', {})
  
  def toXML(self, item_ids):
    element = ET.Element("Constituent")
    if(self.refmark is not None):
      element.set("refmark", str(self.refmark.index))
    
    element.append(self.variables.toXML())
    refs = ET.SubElement(element, "Items")
    for token in self.tokens:
      if token in item_ids:
        # print("Token is %s, its id in the thing is %s" % (id(token), item_ids.get(token, -1)))
        ET.SubElement(refs, "ItemRef", type="token", refid=str(item_ids[token]))
      
    return element
  
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
    
    
    willChange(self.span, 'dependencies', ObservingContext(action = 'add', object = self))
    dependencies = list(self.span._dependencies)
    dependencies.append(self)
    self.span._dependencies = dependencies
    didChange(self.span, 'dependencies', ObservingContext(action = 'add', object = self))
        
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

  def toXML(self, item_ids):
    element = ET.Element("DependencyRelation")
    element.append(self.variables.toXML())
    
    controller_xml = ET.SubElement(element, "Controller")
    target_xml = ET.SubElement(element, "Target")
    
    if self.controller in item_ids:
      if isinstance(self.controller, Token):
        ET.SubElement(controller_xml, "ItemRef", type="token", refid=str(item_ids[self.controller]))
      else:
        ET.SubElement(controller_xml, "ItemRef", type="constituent", refid=str(item_ids[self.controller]))  
    
    if self.target in item_ids:  
      if isinstance(self.target, Token):
        ET.SubElement(target_xml, "ItemRef", type="token", refid=str(item_ids[self.target]))
      else:
        ET.SubElement(target_xml, "ItemRef", type="constituent", refid=str(item_ids[self.target]))  
   
    return element
  

  
# ======================  Variables =================  
class VariablesAccessor(object):
  def __init__(self, obj):
    self.obj = obj
    
    
  def get_value_without_checks(self, key):
    return getattr(self.obj, '_variables', {}).get(key, None)
    
  def __getitem__(self, key):
    """ Return value for the given key """  
    value = getattr(self.obj, '_variables', {}).get(key, None)
    if value not in self.getValidValuesForKey(key):
        value = None
    return value
    
  def __setitem__(self, key, value):
    """ Set the value for the given key """  
    if not (value is None or value in self.getValidValuesForKey(key)):
      raise ValueError("Invalid value %s %s" % (key, self.getValidValuesForKey(key)))
      
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
      
      if key == "PoS" and value == "Dummy":
        variables["Person"] = "3rd"
        variables["Head"] = "yes"
        # variables["Gender"] = "masculine"
        variables["Number"] = "singular"
      
    # set the new variables dictionary
    if len(variables) == 0: 
      del self.obj._variables
    else:
      self.obj._variables = variables
    didChange(self.obj, 'variables', context)
    
  def copyFrom(self, variables):
    willChange(self.obj, 'variables', {})
    if (isinstance(variables, dict)):
      self.obj._variables = dict(variables)
    else:
      self.obj._variables = dict(iter(variables))
    didChange(self.obj, 'variables', {})  
    
    
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
      
      
  def getMnemonicForKey(self, key, prefix=".", suffix=""):
    """ Get the short menmonic description for the given variable """
    keyvalue = (key, self[key])
    
    varlist = self.obj.__db__.document.variableDefinitionsLookup
    decl = varlist.get(keyvalue, None)
    
    if decl is None or decl.mnemonic == "": return ""
    
    return u"%s%s%s" % (prefix, decl.mnemonic, suffix)
    
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
       
  def toXML(self):
    element = ET.Element("Variables")
    for key, val in iter(self):
      if(val is not None):
        ET.SubElement(element, "Variable", Key=key, Value=val)
      
    return element

  
  
# ======================  Error handling =================
def guard(condition, exception):
  if not condition:
    raise exception
  
