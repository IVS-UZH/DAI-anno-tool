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


import threading, weakref, observing, collections, itertools
from observing import ObservingContext
import logging

class Invalid(object):      
  """ 
    A proxy class for managed objects that became invalid
  """
  def __getattribute__(self, attr):
    if attr == '__valid__':
      return False
    else:
      raise AttributeError('Invalid object')
      
""" A special value meaning that the key does not exist """
class NoValueType(object):
  def __repr__(self):
    return "NoValue"

NoValue = NoValueType()

class Transaction(object):
  """
    The transaction interface. Do not create instances of this class, each db will do it for you instead. 
    
    A transaction only covers the subsets of data which has been changed under it. The user can use multiple
    transactions at the same time to modify different subsets of the database
  """
  
  
  # ----- must be implemented by subclasses
  def commit(self): pass

  def abort(self): pass
  
  def setattr(self, obj, attr, value):
    """ the low-level API of changing persistent objects """
    
  def delattr(self, obj, attr):
    """ the low-level API of changing persistent objects """

  def new(self, cls, *args, **kwargs):
    """ the low-level API of changing persistent objects """
      
  @property
  def modifiedInstances(self): pass
  
  @property
  def newInstances(self): pass
  
  # ----- current transaction support
  __threadlocal = threading.local()
  __threadlocal.current = None
  
  @staticmethod
  def getCurrent():
    current = Transaction.__threadlocal.current
    if current is None:
      raise ValueError('No current transaction!')
    return current
    
  def __enter__(self):
    assert Transaction.__threadlocal.current is None
    
    Transaction.__threadlocal.current = self
    
  def __exit__(self, etype, evalue, traceback):
    assert Transaction.__threadlocal.current is self
    
    Transaction.__threadlocal.current = None
    
    # if there is an unhandled exception, we must rollback!
    if evalue is not None:
      self.abort()
  
class PersistenceSchema(object):
  def __init__(self):
    self.__registered_classes = registered_classes = {} 
    
    # define the metaclass for all the persistent stuff
    def obj__new__(cls, *args, **kwargs):
      return Transaction.getCurrent().new(cls, *args, **kwargs)
  
    def obj__setattr__(self, attr, value):
      Transaction.getCurrent().setattr(self, attr, value)
    
    def obj__delattr__(self, attr):
      Transaction.getCurrent().delattr(self, attr)
    
    class Persistent(type):
      def __new__(metacls, *args):
        if len(args) == 1 and isinstance(args[0], type):
          return Persistent(args[0].__name__, (args[0], ), {})
          
        name, bases, dct = args
        dct['__new__'] = obj__new__
        dct['__setattr__'] = obj__setattr__
        dct['__delattr__'] = obj__delattr__
        
        cls = type(name, bases, dct)
        
        registered_classes[name] = cls
        
        #cls.__observers__ = {}
        
        return cls
        
    self.Persistent = Persistent
    
    
  @property
  def classes(self):
    try:
      return self.__classes_accessor
    except AttributeError:
      registered_classes = self.__registered_classes
      
      class accessor(object):
        def __iter__(_): return registered_classes.iterkeys()
        
        def __getitem__(_, name): return registered_classes[name]
        
        __getattr__ = __getitem__
        
        def iteritems(_): return registered_classes.iteritems()
        
        def __repr__(_): return '[%s]' % ','.join(map(repr, registered_classes.itervalues()))
    
      self.__classes_accessor = accessor = accessor()
      
      return accessor
      

_empty_observing_list = collections.namedtuple('_', 'before,after')((), ())      
  
class DB(object): 
  """
    The engine-independent database interface
  """   
  def __init__(self, path, engine, schema = None):
    # the non-comitted root cache (used to implement root modification)
    self.__rootcache = {}
        
    # the persistent data wrapper classes
    self.__wrapper_classes = {}
    
    # schema class indirection 
    self.__schema_class_to_db_class = {}
    
    # lazy load class implementation
    self.__lazyload_classes = {}
    
    # observer storage
    # the observers are set up as a weak dictionery of objects
    # to dictionaries of keys to observer lists
    # we store the observers outside the instance to simplify the managed storage
    # as __dict__ is directly mirrored to the db
    self.__obj_observers = obj_observers = {}
    
    def remove_wref(wref):
      del obj_observers[wref]
    
    # if a schema is provided, we copy the class implementations from there
    if schema is not None:
      specials = frozenset(['__valid__', '__dict__'])
      
      for cls_name, cls in schema.classes.iteritems():
        class db_cls(cls):
          __db__ = self
          __module__ = cls.__module__
          
          __valid__ = True
                    
          __changingF = getattr(cls, '__changing__', None)
          __changedF = getattr(cls, '__changed__', None)
          
          # implement the observing data model
          def __key_is_observable__(_, key):
            return key in _.__dict__ or key in specials

          def __get_observers_for_key__(_, key):
            observer_dict = obj_observers.get(_, None)
            if observer_dict is None:
              wref = observing.WeakKey(_, remove_wref)
              obj_observers[wref] = observer_dict = dict()
              
            return observer_dict.setdefault(key, observing.BeforeAfterObservers())
            
          @property
          def __observable_keys__(_):
            return itertools.chain(_.__dict__.iterkeys(), specials)
              
          def __changing__(_, context):
            # execute the changing hook
            if _.__changingF is not None: _.__changingF(context)
            # get the observer table
            observer_dict = obj_observers.get(_, None)
            if observer_dict is None:
              return
            # notify the observers for the key
            for o in observer_dict.get(context.get('key', None), _empty_observing_list).before:
              o(_, context) 
            # notify the global observers
            for o in observer_dict.get('__dict__', _empty_observing_list).before:  
              o(_, context) 
              
          def __changed__(_, context):
            # execute the changed hook
            if _.__changedF is not None: _.__changedF(context)
            # get the observer table
            observer_dict = obj_observers.get(_, None)
            if observer_dict is None:
              return
            # notify the observers for the key
            for o in observer_dict.get(context.get('key', None), _empty_observing_list).after:
              o(_, context) 
            # notify the global observers
            for o in observer_dict.get('__dict__', _empty_observing_list).after:  
              o(_, context) 
              
          
        db_cls.__name__ = cls.__name__      
        
        self.__wrapper_classes[cls_name] = db_cls   
        self.__schema_class_to_db_class[cls] = db_cls
        
    # currently active transactions
    self.__active_transactions = set()

    # init the storage
    self.__storage = self.__buildEngineClass(engine)(path)
    
    # build the transaction class
    self.__transaction_class = self.__buildTransactionClass()
    
  @property
  def activeTransaction(self):
    try:
      return iter(self.__active_transactions).next()
    except:
      return None
    
  def close(self):
    self.__storage.close()
    
  def __makeObjectInvalid(self, obj):
    logging.debug("Object %s with id 0x%x became invalid", obj, id(obj))
    
    # clean up the observer table and retrieve the __valid__ observers
    observer_dict = self.__obj_observers.pop(obj, {})
    observers = observer_dict.get('__valid__', _empty_observing_list)
    
    context = ObservingContext(key = '__valid__', new = False, old = True)
    
    # change the lass to Invalid
    for o in observers.before:
      o(obj, context)  
    object.__setattr__(obj, '__class__', Invalid)
    for o in observers.after:
      o(obj, context)  
    
    
        
  def __buildEngineClass(self, base):
    wrapper_classes = self.__wrapper_classes
    active_transactions = self.__active_transactions
    lazyload_classes = self.__lazyload_classes
    db = self
    
    class Engine(base):
      def isClassAccepted(self, cls):
        return cls in wrapper_classes.values()
      
      def makeInstanceForClass(self, classname):
        cls = wrapper_classes.get(classname, None)
        if cls is None:
          # its a class that comes from the storage, we don't have a definition for it!
          # cls = type(classname, (PersistentObject,), {'__db__': db})
          # wrapper_classes[classname] = cls
          raise TypeError('Unknown persistent class %s!', classname)
        
        # get the lazy load version
        lazy_load_cls = lazyload_classes.get(cls, None)
        if lazy_load_cls is None:
          class _Lazy(cls):
            def __getattribute__(_, attr):
              # set the __dict__ to the decoded data
              data = self.getPersistentDataForObject(_)
              
              object.__setattr__(_, '__dict__', dict(data))
              object.__setattr__(_, '__class__', cls)
              
              # inform the object that it has been loaded
              # loaded = getattr(_, '__loaded__', None)
              # if loaded is not None:
              #   loaded()
              # else:
              #   print u"loaded %s with %s" % (cls, loaded)
              
              return getattr(_, attr)
        
            def __repr__(_):
              return _.__getattribute__('__repr__')()
              
            def __setattr__(_, attr, value):
              return _.__getattribute__('__setattr__')(attr, value)
          
          _Lazy.__name__ = 'Lazy+' + cls.__name__
                
          lazy_load_cls = lazyload_classes[cls] = _Lazy
        
        
        #
        return object.__new__(lazy_load_cls)
        #return object.__new__(cls)

        
      def getDataForPersistenceCandidate(_, obj):
        # ok, this is a special function
        # its called when we try to commit an object which is unknown
        # we use this to treat 'dangling' objects - one's 
        try:
          # we allow dangling objects if they are currently not being changed by one of the active transactions
          for txn in active_transactions:
            if txn.isModifyingObject(obj):
              raise Exception()
          return obj.__dict__
        except:
          raise ValueError('The object %s is not a persistent object of the current database and cannot be committed!' % object.__repr__(obj))
    
      
    return Engine      
  
  def __buildTransactionClass(self): 
    # db state needed by the transactions
    active_transactions = self.__active_transactions
    storage = self.__storage
    db_schema_class_to_db_class = self.__schema_class_to_db_class
    db = self
    rootcache = self.__rootcache
    make_invalid = self.__makeObjectInvalid
    
    class db_Transaction(Transaction):
      __db__ = self
      active = True
      
      
      def __init__(self):
        if(len(active_transactions)>0):
          raise RuntimeError("Nested transactions are not allowed")
        
        self.__changes = {}
        self.__changed_rootattrs = set()
        self.__initialstate = {}
        self.__rollbackinprogress = False
        # mark the transaction as active
        active_transactions.add(self) 
        
      def isModifyingObject(self, obj):
        return obj in self.__changes
        
      @property
      def changedObjects(self):
        return self.__changes.iterkeys()
      
      def commit(self): 
        logging.info("Committing transaction 0x%x", id(self))
        try:
          # get the changed root items
          root_item_changes = {name:rootcache[name] for name in self.__changed_rootattrs}
          
          # compute the to be commited states for the objects
          objects = {}
          for obj, attributes in self.__changes.iteritems():
            d = storage.getPersistentDataForObject(obj) 
            if d is None:
              d = obj.__dict__
            else:
              # make a copy of the persistent data, substituting the changes
              d = dict(d)
              __dict__ = obj.__dict__
              for attr in attributes:
                if attr in __dict__:
                  d[attr] = __dict__[attr]
                else:
                  del d[attr]
                  
            # add it to the changelist        
            objects[obj] = d
            logging.debug("Commit %s with data %s", obj, d)
                                        
          # commit the changes
          storage.commitChanges(objects, root_item_changes)
          
          # invalidate the objects that went out of scope
          # python docs seem to suggest that keys will be iterated in the same order
          # if no changes happen to the dictionary, but let's be on the safe side here
          objects_to_check  = tuple(objects.iterkeys())
          invalid_objects = [obj for obj, refcount in itertools.izip(objects_to_check, storage.getRefcountsForObjects(objects_to_check)) if refcount == 0]
          
          for obj in invalid_objects:
            make_invalid(obj)  
          
          # weird GC issue? clear manually
          objects.clear()
          root_item_changes.clear()
          
          # don't forget to clean the root cache!
          for key in self.__changed_rootattrs:
            rootcache.pop(key)
            
          # and make sure the transaction is not active anymore
          active_transactions.discard(self)           
          del self.__changes
          del self.__changed_rootattrs
          del self.__initialstate
          self.__class__ = Invalid
        except Exception as e:
          logging.exception("Exception while committing transaction 0x%x", id(self))
          self.abort()
          raise
          
        logging.info("Finished committing transaction 0x%x", id(self))
        

      def abort(self):         
        self.__rollbackinprogress = True
        
        self.__enter__()
        
        logging.info("Rolling back transaction %x", id(self))
        
        
        for obj, attributes in self.__changes.iteritems():
          d = storage.getPersistentDataForObject(obj) 

          #if d is None: d = {}
          logging.debug("Rolling back %s with data %s to original data 0x%s", obj, obj.__dict__, d)
          
          if d is not None:
            # restore all changed attributes from the persistent data
            if hasattr(obj, '__beforeRollback__'): obj.__beforeRollback__()
            for attr in attributes:
              if attr in d:
                value = d[attr]
                context = ObservingContext(key = attr, new = value, old = obj.__dict__.get(attr, NoValue))
                obj.__changing__(context)
                obj.__dict__[attr] = d[attr]
                obj.__changed__(context)
              else:
                context = ObservingContext(key =  attr, new = NoValue, old = obj.__dict__[attr])
                obj.__changing__(context)
                del obj.__dict__[attr]
                obj.__changed__(context)
            if hasattr(obj, '__afterRollback__'): obj.__afterRollback__()
          else:
            make_invalid(obj)
              
        
        self.__exit__(None, None, None)
            
        # don't forget to clean the root cache!
        for key in self.__changed_rootattrs:
          rootcache.pop(key)
           
        # and make sure the transaction is not active anymore  
        active_transactions.discard(self) 
        del self.__changes
        del self.__changed_rootattrs
        
        self.__rollbackinprogress = False
        
        
        self.__class__ = Invalid
        
        logging.info("Finished rolling back transaction 0x%x", id(self))
        
        
        
      def set_root_item(self, name, value):
        if self.__rollbackinprogress: return
        
        # check if we can shedule the root value modification or if another transation already does it
        if name in self.__changed_rootattrs or name not in rootcache:
          rootcache[name] = value
          self.__changed_rootattrs.add(name)
          
      def del_root_item(self, name):
        if self.__rollbackinprogress: return
        
        # check if we can shedule the root value modification or if another transation already does it
        if name in self.__changed_rootattrs or name not in rootcache:
          rootcache[name] = None
          self.__changed_rootattrs.add(name)
            
  
      def setattr(self, obj, attr, value):
        if self.__rollbackinprogress: return
        
        # if attr is a descriptor, delegate the changes to it
        desc = getattr(obj.__class__, attr, None)
        if desc is not None and hasattr(desc, '__set__'):
          desc.__set__(obj, value)
          return
        
        
        # TODO: make sure that we cannot reference objects which are not in store because it means that they are defined
        #   by another transaction!
        #print 'attempting to change', attr, 'of', object.__repr__(obj)
        
        
        # 1. get the list of changed attributes for the given object
        changed_attributes_for_object = self.__changes.get(obj, [])
        
        # 2. if this transaction did not already change, we must do some additioal testing 
        if attr not in changed_attributes_for_object:
          # was it modified by another transaction? this would be an error
          if len(active_transactions)>1:
            for txn in active_transactions:
              if txn is not self:
                if attr in txn.__changes.get(obj, []):
                  raise ValueError('The attribute %s has been modified in another transaction!' % attr)
          # mark it as modified
          changed_attributes_for_object.append(attr)
          self.__changes[obj] = changed_attributes_for_object
          
        # 3. change the attribute and notify the observers. Yes, its that simple
        context = ObservingContext(key = attr, new = value, old = obj.__dict__.get(attr, NoValue))

         # print "Changing %s with context %s" % (obj, context)

        obj.__changing__(context)  
        obj.__dict__[attr] = value    
        obj.__changed__(context)  
                  
        
        
      def delattr(self, obj, attr):
        if self.__rollbackinprogress: return
        
        # TODO: make sure that we cannot reference objects which are not in store because it means that they are defined
        #   by another transaction!
        
        # 1. get the list of changed attributes for the given object
        changed_attributes_for_object = self.__changes.get(obj, [])
        
        # 2. if this transaction did not already change, we must do some additioal testing 
        if attr not in changed_attributes_for_object:
          # was it modified by another transaction? this would be an error
          if len(active_transactions)>1:
            for txn in active_transactions:
              if txn is not self:
                if attr in txn.__changes.get(obj, []):
                  raise ValueError('The attribute %s has been modified in another transaction!' % attr)
          # mark it as modified
          changed_attributes_for_object.append(attr)
          self.__changes[obj] = changed_attributes_for_object
          
        # 3. delet the attribute. Yes, its that simple
        context = ObservingContext(key = attr, new = NoValue, old = obj.__dict__[attr])

        obj.__changing__(context)  
        del obj.__dict__[attr]
        obj.__changed__(context)  
        

      def new(self, cls, *args, **kwargs):
        # try to fix the class
        cls = db_schema_class_to_db_class.get(cls, cls)
        # check that its a correct class
        assert cls.__db__ is db
        
        # create the object
        obj = object.__new__(cls)        
        #obj.__init__(*args, **kwargs)
        
        # and add it to the transaction change log
        self.__changes[obj] = []
        
        return obj
        
      def debug(self):
        print self.__changes, self.__changed_rootattrs, active_transactions
        
        
      
    return db_Transaction
    

  # ------- schema and objects  
  @property
  def classes(self):
    """ registered persistent classes """
    try:
      return self.__classes_accessor
    except AttributeError:
      registered_classes = self.__wrapper_classes
      
      class accessor(object):
        def __iter__(_): return registered_classes.iterkeys()
        
        def __getitem__(_, name): return registered_classes[name]
        
        __getattr__ = __getitem__
        
        def __repr__(_): return '[%s]' % ','.join(map(repr, registered_classes.itervalues()))
        
    
      self.__classes_accessor = accessor = accessor()
      
      return accessor
    
    
  def objectsByClass(self, *classes):
    classes = [self.__schema_class_to_db_class.get(cls, cls) for cls in classes]
    
    objects = set()
    
    for cls in classes:
      # query the active transactactions
      for txn in self.__active_transactions:
        for obj in txn.changedObjects:
          if isinstance(obj, cls):
            objects.add(obj)
      
      # query the database
      for obj in self.__storage.objectsByClass(cls):
        objects.add(obj)
        
    return objects
    
  def objectsByCondition(self, filter, *classes):
    pass
    
    
  def getRefcountsForObjects(self, objects):
    if len(objects) == 0:
      return {}
      
    return dict(zip(objects, self.__storage.getRefcountsForObjects(objects)))  
    
  def objectPersistencyStatus(self, obj):
    """ return True if the current object is stored within the db """
    return self.__storage.objectPersistencyStatus(obj)
              
        
  # ------- transaction management
  def transaction(self):
    """ create a new transaction """
    return self.__transaction_class()
    
  
  # ------- root items
  @property
  def root(self):
    try:
      return self.__root_accessor
    except AttributeError:
      storage = self.__storage
      rootcache = self.__rootcache
      
      class accessor(object):
        def __getitem__(_, key): 
          try:
             return rootcache[key]
          except KeyError:
            return storage.getRootItem(key)
        
        __getattr__ = __getitem__
        
        def __setitem__(_, key, value): 
          Transaction.getCurrent().set_root_item(key, value)
        
        __setattr__ = __setitem__
        
        def __delitem__(_, key): 
          Transaction.getCurrent().del_root_item(key)
        
        __delattr__ = __delitem__
        
                
    
      self.__root_accessor = accessor = accessor()  
      
      return accessor
      
  def debug(self):
    self.__storage.debug()

    
# class PersistentObject(object):
#   """
#     Changes to the persistent object are simply communicated to the current transaction
#     
#     It is also possible to use the appropriate methods if the transaction to change the object
#   """
#   def __new__(cls, *args, **kwargs):
#     return Transaction.getCurrent().new(cls, *args, **kwargs)
#   
#   def __setattr__(self, attr, value):
#     Transaction.getCurrent().setattr(self, attr, value)
#     
#   def __delattr__(self, attr):
#     Transaction.getCurrent().delattr(self, attr)
# 
#     
#     
#     
#     
#     
#   
#