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



import threading, weakref, observing

class Invalid(object):        
    def __getattribute__(self, attr):
        if attr == 'active':
            return False
        else:
            raise AttributeError('Invalid object')

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
        
        
        
    # def registerClass(self, cls):
    #     cls = type(cls.__name__, (PersistentObject, cls), {'__module__': cls.__module__})
    #     
    #     #self.__changing__()
    #     self.__registered_classes[cls.__name__] = cls
    #     #self.__changed__()
    #     
    #     return cls
        
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
            
    # def opendb(self, path, engine, **kwargs):
    #     return DB(path, self, engine, **kwargs)
        
    
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
        
        # the observers are set up as a weak dictionery of objects
        # to dictionaries of keys to observer lists
        # the None keys sets up the default observer
        self.__obj_observers = {}
        
        # if a schema is provided, we copy the class implementations from there
        if schema is not None:
            observers = self.__obj_observers
            
            def get_observer_dict_for_obj(_):
                # get the observers dictionary
                # create one if it does no exist
                obj_observers = observers.get(_, None)
                if obj_observers is None:
                    wref = observing.WeakKey(_, remove_wref)
                    observers[wref] = obj_observers = dict()
                    
                return obj_observers
            
            for cls_name, cls in schema.classes.iteritems():
                remove_wref = self.__remove_object
                
                class db_cls(cls):
                    __db__ = self
                    __module__ = cls.__module__
                    
                    __changingF = getattr(cls, '__changing__', None)
                    __changedF = getattr(cls, '__changed__', None)
                    
                    def __observers_for_key__(_, key):
                        # return the observer list for the key
                        # or create a default observer list
                        # yes, its inefficient, who cares
                        return get_observer_dict_for_obj(_).setdefault(key, observing.BeforeAfterObservers())
                            
                    def __observers__(_):
                        # return the observer list for the object (key=None)
                        # or create a default observer list
                        # yes, its inefficient, who cares
                        return get_observer_dict_for_obj(_).setdefault(None, observing.BeforeAfterObservers())
                        
                    def __changing__(_, context = None):
                        # execute the changing hook
                        if _.__changingF is not None: _.__changingF(context)
                        # get the observers
                        obj_observers = observers.get(_, None)
                        # guard agains empty observers
                        if obj_observers is None: 
                            return
                        # run the object observer (if any)
                        olist = obj_observers.get(None, None)    
                        if olist is not None:
                            for o in olist.before:
                                o(_, context = context)
                        # run the key observer (if any)
                        key = context.get('attr', None)
                        if key is None:
                            return
                        olist = obj_observers.get(key, None)    
                        if olist is not None:
                            for o in olist.before:
                                o(_, context = context)
                            
                    def __changed__(_, context = None):
                        if _.__changedF is not None: _.__changedF(context)
                        # get the observers
                        obj_observers = observers.get(_, None)
                        # guard agains empty observers
                        if obj_observers is None: 
                            return
                        # run the object observer (if any)
                        olist = obj_observers.get(None, None)    
                        if olist is not None:
                            for o in olist.after:
                                o(_, context = context)
                        # run the key observer (if any)
                        key = context.get('attr', None)
                        if key is None:
                            return
                        olist = obj_observers.get(key, None)    
                        if olist is not None:
                            for o in olist.after:
                                o(_, context = context)
                                
                db_cls.__name__ = cls.__name__        
                
                self.__wrapper_classes[cls_name] = db_cls     
                self.__schema_class_to_db_class[cls] = db_cls
                
        # currently active transactions
        self.__active_transactions = set()

        # init the storage
        self.__storage = self.__buildEngineClass(engine)(path)
        
        # build the transaction class
        self.__transaction_class = self.__buildTransactionClass()
        
    def __remove_object(self, wref):
        del self.__obj_observers[wref]
        
    def close(self):
        self.__storage.close()
        
    def __del__(self):
        self.close()    
        
                
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
                            loaded = getattr(_, '__loaded__', None)
                            if loaded is not None:
                                loaded()
                            
                            return getattr(_, attr)
                
                        def __repr__(_):
                            return _.__getattribute__('__repr__')()
                            
                        def __setattr__(_, attr, value):
                            return _.__getattribute__('__setattr__')(attr, value)
                    
                    _Lazy.__name__ = 'Lazy+' + cls.__name__
                              
                    lazy_load_cls = lazyload_classes[cls] = _Lazy
                
                
                
                return object.__new__(lazy_load_cls)

                
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
        
        class db_Transaction(Transaction):
            __db__ = self
            active = True
            
            
            def __init__(self):
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
                      #  print '---COMMIT', obj, d
                            
                            
                    # commit the changes
                    storage.commitChanges(objects, root_item_changes)
                    
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
                    print 'encountered', e, 'rolling bock'
                    self.abort()
                    raise

            def abort(self): 
                self.__rollbackinprogress = True
                
                self.__enter__()
                #print Transaction.getCurrent()
                
                print '<<<ROLLBACK'
                
                for obj, attributes in self.__changes.iteritems():
                    d = storage.getPersistentDataForObject(obj) 
                    #if d is None: d = {}
                    
                    # print '---rolling back', obj, 'original', d, 'now', obj.__dict__
                    # try:
                    #     print 'token list id', id(d['tokens']), id(obj.__dict__['tokens'])
                    #     print 'data id', id(d), id(obj.__dict__)
                    #     
                    # except: pass
                    
                    if d is not None:
                        # restore all changed attributes from the persistent data
                        for attr in attributes:
                            if attr in d:
                                value = d[attr]
                                context = ObservingContext(attr = attr, new = value)
                                if hasattr(obj, attr): context['old'] = obj.__dict__[attr]
                                obj.__changing__(context = context)
                                obj.__dict__[attr] = d[attr]
                                obj.__changed__(context = context)
                            else:
                                context = {'attr' : attr, 'old': obj.__dict__[attr]}
                                obj.__changing__(context = context)
                                del obj.__dict__[attr]
                                obj.__changed__(context = context)
                    else:
                        context = {'attr' : '__dict__', 'old': dict(obj.__dict__)}
                        obj.__changed__(context = context)
                    
                   # print 'obj is now', obj.__dict__
                
                self.__exit__(None, None, None)
                        
                        
                # don't forget to clean the root cache!
                for key in self.__changed_rootattrs:
                    rootcache.pop(key)
                   
                # and make sure the transaction is not active anymore    
                active_transactions.discard(self) 
                del self.__changes
                del self.__changed_rootattrs
                
                self.__rollbackinprogress = False
                
                # print 'ROLLBACK END'
                # print 'active transactions', active_transactions
                
                
                self.__class__ = Invalid
                
                
                    
                
                    
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
                
                # TODO: make sure that we cannot reference objects which are not in store because it means that they are defined
                #       by another transaction!
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
                context = observing.ObservingContext(attr = attr, new = value)
                if hasattr(obj, attr): context['old'] = obj.__dict__[attr]

                print "Changing %s with context %s" % (obj, context)

                obj.__changing__(context = context)    
                obj.__dict__[attr] = value    
                obj.__changed__(context = context)    
                                    
                
                
                
            def delattr(self, obj, attr):
                if self.__rollbackinprogress: return
                
                # TODO: make sure that we cannot reference objects which are not in store because it means that they are defined
                #       by another transaction!
                
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
                context = ObservingContext(attr = attr, old = obj.__dict__[attr])

                obj.__changing__(context = context)    
                del obj.__dict__[attr]
                obj.__changed__(context = context)    
                

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
            # first, try all the stuff in the transactions
            for txn in self.__active_transactions:
                for obj in txn.changedObjects:
                    if isinstance(obj, cls):
                        objects.add(obj)
            
            #print 'looking for class cls'
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
#     """
#         Changes to the persistent object are simply communicated to the current transaction
#         
#         It is also possible to use the appropriate methods if the transaction to change the object
#     """
#     def __new__(cls, *args, **kwargs):
#         return Transaction.getCurrent().new(cls, *args, **kwargs)
#     
#     def __setattr__(self, attr, value):
#         Transaction.getCurrent().setattr(self, attr, value)
#         
#     def __delattr__(self, attr):
#         Transaction.getCurrent().delattr(self, attr)
# 
#         
#         
#         
#         
#         
#     
#         