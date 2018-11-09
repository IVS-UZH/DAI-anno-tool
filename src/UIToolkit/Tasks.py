##############################################################
# Tasks.py
#
# Synchronious round robin tasks
#
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


import time, weakref, math
from observing import observable_property, willChange, didChange, observers
from GUI import Task as PyGUI_Task


class lazystaticproperty(object):
  def __init__(self, finit):
    self.finit = finit
    
  def __get__(self, obj, cls):  
    if not hasattr(self, 'value'):
      self.value = self.finit(cls)
      
    return self.value


class TaskletBase(object):
  # state information
  @observable_property
  def running(self):
    return self in TaskletBase.__tasklets
    
  @observable_property 
  def completed(self):
    return isinstance(self, CompletedTasklet)
    
  def sheduleAfter(self, *tasklets):
    # save the list of tasklets we are waiting for
    self.__waiting_for = set(tasklets)
    
    # install observers
    for tasklet in tasklets:
      observers(tasklet, 'completed').after += self.__waiting_signal
    # mark this tasklet as waiting
    TaskletBase.__waiting_tasklets.add(self)    

    return self
    
  def __waiting_signal(self, tasklet, context):
    self.__waiting_for.discard(tasklet)
    if len(self.__waiting_for) == 0:
      self.shedule()
  
  def sheduleWith(self, tasklet):
    # save the list of tasklets we are waiting for
    self.__waiting_for = set((tasklet,))
    
    # install observers
    for tasklet in tasklets:
      observers(tasklet, 'running').after += self.__waiting_signal
    # mark this tasklet as waiting
    TaskletBase.__waiting_tasklets.add(self)    
    
    return self
    
    
      
  def shedule(self):
    """ Starts running the task """
    # do nothign if running
    if self.running:
      return
    
    willChange(self, 'running', {})
    # restart the task if its not running
    if len(TaskletBase.__tasklets) == 0:
      TaskletBase.__pygui_task.start() 
    TaskletBase.__tasklets.add(self)
    TaskletBase.__waiting_tasklets.discard(self)
    didChange(self, 'running', {})
  
    return self
  
  def complete(self):
    """ Complete the task. Subclasses should call this when their work is done """  
    # do nothing if already completed
    willChange(self, 'running', {})
    TaskletBase.__tasklets.discard(self)
    didChange(self, 'running', {})
        
    willChange(self, 'completed', {})
    didChange(self, 'completed', {})
    self.__class__ = CompletedTasklet
    
    return self
    
  # --- the step callback, subclasses will override this
  def _complete(self):
    pass
  
  def _step(self):
    pass
    
  # ---  sheduling logic
  __tasklets = set()
  __waiting_tasklets = set()
  
  @lazystaticproperty
  def __pygui_task(cls):
    return PyGUI_Task(TaskletBase.__sheduler, 0.025, repeat = True, start = False)
    
  @classmethod
  def __sheduler(cls):
    # step all active tasklets
    for tasklet in tuple(TaskletBase.__tasklets):
      tasklet._step()
        
    # if there are no tasks left, stop the task so that we don't waste the CPU time
    # TODO: setup multiple tasks with different granularity so that we can track the stuff
    if len(TaskletBase.__tasklets) == 0:
      TaskletBase.__pygui_task.stop() 
    
class CompletedTasklet(TaskletBase):
  def shedule(self):
    raise TypeError("Can't shedule already completed task")
        
  def complete(self):
    raise TypeError("Task already completed")  
    
  def _step(self):
    pass  

class Tasklet(TaskletBase):
  def __init__(self, callback, interval = 0):
    self.__lasttime = None
    self.__callback = callback
    self.__interval = interval

  def _step(self):
    # check if sufficient time has passed 
    t = time.time()
    if self.__lasttime is None or (t - self.__lasttime)>=self.__interval:
      # run the callback 
      self.__lasttime = t
      self.__callback(self)
    
class DelayedTask(TaskletBase):
  def __init__(self, callback, duration):
    self.__lasttime = None
    self.__callback = callback
    self.__interval = duration
  
  def _step(self):
    # first time we are called, just save the time
    if self.__lasttime is None:
      self.__lasttime = time.time()
    elif (time.time() - self.__lasttime)>=self.__interval:
      self.__callback(self)
      self.complete()    


__all__ = ('Tasklet', 'DelayedTask')    
    
    