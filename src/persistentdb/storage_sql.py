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



from observing import WeakKey
from collections import namedtuple
import sys, os
import atexit

  
import msgpack, struct#, sqlite3
from pysqlite2 import dbapi2 as sqlite3

ExtType = msgpack.ExtType

# each oid consists of the class id + instance id (both uint32_t)
int_packer = struct.Struct('!L')

# make the map size big enough for 256MB database. We won't use anythign bigger!
MAP_SIZE = 256*1024*1024

# the object cache record
ObjCacheEntry = namedtuple('ObjCacheEntry', 'oid,data')

db_schema = """
-- the globals table contains important stuff 
create table globals(
  version text not null, 
  refcounts blob,
  classnames blob
);
insert into globals values('1.0', NULL, NULL);

-- this table contains the root items
create table root(
  key blob primary key, 
  value blob
);


-- this table contains the object data
create table objects(
  oid integer primary key,
  class integer,
  data blob,
  unique(oid, class)
);
""" 

db_init_connection_script = """
pragma locking_mode = EXCLUSIVE;
pragma journal_mode = WAL;
pragma temp_store  = MEMORY;
PRAGMA synchronous = FULL;
VACUUM;"""

class SQLStorageEngine(object):   
  def __init__(self, path): 
    # print os.path.join(sys.path[0], path)
    # print path
       
    self.__path = path
    
    # open the connection
    self.__connection = sqlite3.connect(path)
    self.__connection.executescript(db_init_connection_script)
    self.__cursor = self.__connection.cursor()
    
    # check if the database is empty, if yes, execute the schema
    try:
      version = self.__connection.execute('select version from globals').fetchone()[0]
      if version != '1.0': 
        raise ValueError('Version mismatch!')
    except sqlite3.OperationalError:
      self.__connection.executescript(db_schema)
      self.__connection.execute('PRAGMA wal_checkpoint(RESTART);')
    
    
    # read the class names and the instance id
    try:
      self.__classnames = msgpack.unpackb(self.__connection.execute('select classnames from globals').next()[0])
      for n in self.__classnames:
        self.makeInstanceForClass(n)
    except TypeError:
      self.__classnames = []
        
         
    # the object cache, consisting of ObjCacheEntry items
    self.__obj_cache = {}
    # oid -> weakref
    self.__oid_to_wref = {}
      
    # collect list - objects with rc of 0
    self.__to_collect = set()
    
    # ensure the database is closed when the process crashes or exits
    # without propertly calling the close() method
    def destruct(ref):
      if ref() is not None:
        ref().close()
        
    atexit.register(destruct, WeakKey(self))
    
  def __setup_db(self):
    connection = self.__connection
    
    connection.executescript("""
      pragma locking_mode = EXCLUSIVE;
      pragma journal_mode = WAL;
      pragma temp_store  = MEMORY;
      pragma synchronous = FULL;
      VACUUM;""")
    
    
  def close(self):
    # is it already closed?
    if self.__connection is None: return
    
    
    # make sure the wal file is reset
    #self.__connection.execute('pragma wal_checkpoint(RESTART);')
    # close the connection
    self.__connection.close()
    # remove the wal file
    # try: os.remove(self.__path + '-wal')
    # except: pass
    
    self.__connection = None
    
  def __del__(self):
    self.close()  
    
  def debug(self): 
    for line in self.__connection.iterdump():    
      print line
     
    
  # removes a collected item from the cache  
  def __remove_wref(self, wref):
    # remove the wref from the object cache
    try:
      del self.__oid_to_wref[self.__obj_cache.pop(wref).oid]
    except: pass
    
  def getRootItem(self, key):
    # make sure key msg-encoded encoded!
    key = buffer(msgpack.packb(key))
    
    # get the data from the root table
    value = self.__cursor.execute('select value from root where key = ?', (key,)).fetchone()
    
    # if there is no such key, we simply return None
    if value is None:
      return None
      
    # the msgpack extension type decoder
    # 1 is the code for the object
    def ext_hook(code, data):
      if code == 1: return self.__getObjectForOID(int_packer.unpack(data)[0])
      else: raise ValueError("Unknown extended type: %s" % code)
    
    return msgpack.unpackb(value[0], ext_hook=ext_hook)
    
  def objectsByClass(self, cls):
    # get the class id
    try:
      class_i = self.__classnames.index(cls.__name__)
    except ValueError:
      return tuple() # no such data, duh
    
    # stored items. we use this instead of iteration for a number of reasons    
    oids = list(self.__cursor.execute('select oid from objects where class = ?', (class_i, )))
    objects = [self.__getObjectForOID(oid[0]) for oid in oids]
                        
    return objects           
      
    
    
  def __getObjectForOID(self, oid):    
    # if the object is in cache, return that
    wref = self.__oid_to_wref.get(oid, None)
    if wref is not None:
      return wref()
    
    # we will need to create the instance

    # get the of for the instance
    classname = self.__classnames[self.__cursor.execute('select class from objects where oid = ?', (oid, )).fetchone()[0]]
      
    # otherwise, we need a new instance
        
    # make the innstance and add it to the cache to prevent recursion
    obj = self.makeInstanceForClass(classname)
    wref = WeakKey(obj, self.__remove_wref)
    
    self.__obj_cache[wref] = ObjCacheEntry(oid, None)
    self.__oid_to_wref[oid] = wref
    
    
    # we are done here! the object will use lazy loading
    return obj    
    
  def getPersistentDataForObject(self, obj): 
    cache_entry = self.__obj_cache.get(obj, None)
    if cache_entry is not None:
      oid, data = cache_entry
      if data is None:
        # the msgpack extension type decoder
        # 1 is the code for the object
        def ext_hook(code, data):
          if code == 1: 

            return self.__getObjectForOID(int_packer.unpack(data)[0])
          else: raise ValueError("Unknown extended type: %s" % code)
      
        packed_data = self.__cursor.execute('select data from objects where oid = ?', (oid,)).fetchone()[0]
                
        data = msgpack.unpackb(packed_data, encoding = 'utf-8', ext_hook=ext_hook)  


        

        
        def decode(code, oid):
          if code == 1: 
            oid = int_packer.unpack(oid)[0]
          return oid
          

          
        
          
        self.__obj_cache[obj] = ObjCacheEntry(oid, data)
          
      return data
    else:
      return None
  
  def getRefcountsForObjects(self, objects):
    # retrieve the refcount table
    refcount_table = self.__cursor.execute('select refcounts from globals').fetchone()[0]
    if refcount_table is None:
      refcount_table = {}
    else:
      refcount_table = msgpack.unpackb(refcount_table)
    
    # we will store the counts here
    counts = []
    
    for obj in objects:
      cache_entry = self.__obj_cache.get(obj, None)
      if cache_entry is None:
        counts.append(0)
      else:
        counts.append(refcount_table.get(cache_entry.oid, 1))
      
    return counts  
    
  
  # do the garbage collection on objects with refcounter of zero    
  # we need a write transaction to do this, as we will change the database!  
  def __collect(self, cursor,  refcount_table):
    # local reference to the non-collected objects with refcount of 0
    to_collect = self.__to_collect
    
    # this msgpack decoder function will decrement the refcount of each object it encounteres
    # we use it to decrease the dependency on contained objects
    def decode_and_decrease_refcount(code, oid):
      if code == 1: 
        refcount = refcount_table.pop(oid, 1)
        # case 1 - refcount == 1, then we release the object
        if refcount == 1:
          # we must notify the collector that this object is being released
          to_collect.add(oid)
        else:
          # decrease it by one
          refcount -= 1
          if refcount > 1: # we need to write this back
            refcount_table[oid] = refcount
          
      else: 
        raise ValueError("Unknown extended type: %s" % code)


    while len(to_collect)>0:
      # get the next id to be collected
      oid = to_collect.pop()
      
      data = cursor.execute('select data from objects where oid = ?', (oid,)).fetchone()
      cursor.execute('delete from objects where oid = ?', (oid,))
      
      # and make sure the refcount of its dependences is decreased
      if data is not None:
        msgpack.unpackb(data[0], ext_hook = decode_and_decrease_refcount)
        
      
      # remove the item from cache 
      # the reference to the object might still live, but it will be basically treated as a newly created (dangling) object
      wref = self.__oid_to_wref.pop(oid, None)
      if wref is not None:
        del self.__obj_cache[wref]
        
        

  # this is where the magic happens
  def commitChanges(self, objects, root_items): 
    # this will record all new objects in case we need to invalidate the cache on abort
    new_objects = []   
    committed_objects = set()
    
    cursor = self.__cursor     
    
    # --- commit is starting!
    # we do it in a try-except block so we can rollback the cache and the db state if somethign go wrong
    try:
      # 1 read in the refcount table
      refcount_table = cursor.execute('select refcounts from globals').fetchone()[0]
      if refcount_table is None:
        refcount_table = {}
      else:
        refcount_table = msgpack.unpackb(refcount_table)
        
        
      # this msgpack decoder function will decrement the refcount of each object it encounteres
      # we use it to decrease the dependency on contained objects
      def decode_and_decrease_refcount(code, oid):
        if code == 1: 
          oid = int_packer.unpack(oid)[0]
          refcount = refcount_table.pop(oid, 1)
          # case 1 - refcount == 1, then we release the object
          if refcount == 1:
            # we must notify the collector that this object is being released
            self.__to_collect.add(oid)

          else:
            # decrease it by one
            refcount -= 1
            if refcount > 1: # we need to write this back
              refcount_table[oid] = refcount
            # make sure its not collected!
            #self.__to_collect.discard(oid)
          
        else: 
          raise ValueError("Unknown extended type: %s" % code)

      
      # this msgpack encoder function will create/encode the object data and increase the refcount
      def encode_and_increase_refcount(obj):

        
        cache_entry = self.__obj_cache.get(obj, None)
        if cache_entry is None:
          # we need to create a new object
          
          # 1. get the class_i
          try:
            classname = obj.__class__.__name__
            classname_i = self.__classnames.index(classname)
          except ValueError:
            if not self.isClassAccepted(obj.__class__):
              raise ValueError('Class %s is not persistent and cannot be encoded!' % obj.__class__)
            
            classname_i = len(self.__classnames)
            self.__classnames.append(classname)
        
          # get the object data
          # its either in the commit record
          # or its a dangling object, in which case we must consult the database
          data = objects.get(obj, None)
          if data is None:
            data = self.getDataForPersistenceCandidate(obj)
          data = dict(data)  
          # ok, this is inelegant, but for now it will suffice
          # we add the object twice to the table - because we need to know the oid
          cursor.execute('insert into objects values(null, ?, null)', (classname_i,))
          oid = cursor.lastrowid
           
            
          # add it to the cache
          # we add it to the cache first to deal with circular dependencies
          wref = WeakKey(obj, self.__remove_wref)
        
          self.__obj_cache[wref] = ObjCacheEntry(oid, data)
          self.__oid_to_wref[oid] = wref
        
          # pack the data and put it into the database   
          packed_data = buffer(msgpack.packb(data, default = encode_and_increase_refcount))
          
          cursor.execute('update objects set data = ? where oid = ?', (packed_data, oid))
          
          committed_objects.add(obj)
        
          # and mark it as a new object - we need it to rollback the cache
          new_objects.append((oid, wref))
        else:
          oid = cache_entry.oid
        
          # increase the refcounter
          refcount_table[oid] = refcount_table.get(oid, 1) + 1
          self.__to_collect.discard(oid)

        return tuple.__new__(ExtType, (1, int_packer.pack(oid)))
        
        
      # 2. process the object changes
      n = 0
      for obj, data in objects.iteritems():
        if obj in committed_objects: 
          continue
          
        # ok, the idea is - if the object is not yet persistent, we don't update it
        # because if its not persistent, its refcount is 0
        cache_entry = self.__obj_cache.get(obj, None)
        if cache_entry is None: 
          continue
        

        oid = cache_entry[0]
        
        # the data has changed - decrement the refcounts of all dependent objects
        old = cursor.execute('select data from objects where oid = ?', (oid,)).fetchone()
        if old is not None:
          msgpack.unpackb(old[0], ext_hook = decode_and_decrease_refcount)
        
        # set the new data and cache entry
         # print 'SQL COMMITS', obj, data
        self.__obj_cache[obj] = ObjCacheEntry(oid, dict(data))
        #print 'CACHE ENTRY IS', self.__obj_cache[obj]
        data = buffer(msgpack.packb(data, default = encode_and_increase_refcount))
        
        def decode(code, oid):
          if code == 1: 
            oid = int_packer.unpack(oid)[0]
          return oid
        
        
        cursor.execute('update objects set data = ? where oid = ?', (data, oid))
        committed_objects.add(obj)
        
        
        n += 1
        
      # 3 - process the root item changes 
      # the idea here is simple - we decrease the refcount of all items in the old value
      # and increase the refcount f all items in the new value
      for key, value in root_items.iteritems():
        # pack the key
        key = buffer(msgpack.packb(key))
        
        
        # make sure the old data is released
        old = cursor.execute('select value from root where key = ?', (key,)).fetchone()
        if old is not None:
          msgpack.unpackb(old[0], ext_hook = decode_and_decrease_refcount)
          cursor.execute('delete from root where key = ?', (key,))    

        # make sure the new data is retained

        
        if value is not None:
          value = buffer(msgpack.packb(value, default = encode_and_increase_refcount))
          cursor.execute('insert into root values(?, ?)', (key, value))
        
          

        
      # step 3 - collect the garbage
      self.__collect(cursor, refcount_table)      
      
      # sync the refcount table
      if len(refcount_table)>0:
        cursor.execute('update globals set refcounts = ?', (buffer(msgpack.packb(refcount_table)), ))
      else:
        cursor.execute('update globals set refcounts = null')

      
      # and the classnames!
      cursor.execute('update globals set classnames = ?', (buffer(msgpack.packb(self.__classnames)), ))

      # commit the transaction!
      self.__connection.commit()
      self.__connection.execute('pragma wal_checkpoint(truncate);')
    except:
      self.__connection.rollback()
      
      # restore the cache
      for oid, wref in new_objects:
        del self.__obj_cache[wref]
        del self.__oid_to_wref[oid]
        

      self.debug()
      raise
      
      
    
    
  
  
    
  
    
    
