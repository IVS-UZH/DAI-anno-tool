##############################################################
# layout.py
#
# Provides constraint-based mechanism for laying out the user interface
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
from GUI import Task as PyGUI_Task


##############################################################
# Interpolation routines commonly used for interpolation
#  
# Interpolable values provide the method interpolateTo

# class StaticClassMeta(type):
#     def __getattribute__(cls, name):
#         return object.__getattribute__(cls, '__dict__')[name]
        
def interpolate_values(t, A, B):
    try:
        return A.__interpolate__(B, t)
    except:
        return A*(1-t) + B*t
        

class Interpolators(object):
#    __metaclass__ = StaticClassMeta
    
    # A is starting value, B is end value, t is interpolation variable (0-1)
    linear = staticmethod(interpolate_values)
    
    @staticmethod        
    def inCubic(t, A, B):
        return interpolate_values(math.pow(t, 3), A, B)

    @staticmethod                
    def outCubic(t, A, B):
        return interpolate_values(math.pow(t-1, 3)+1, A, B)
     
    @staticmethod           
    def inoutCubic(t, A, B):
        t = t*2
        if t <1:
            return interpolate_values(math.pow(t, 3)/2.0, A, B)
        else:
            t = t-2
            return interpolate_values(1+ math.pow(t, 3), A, B)
            
    @staticmethod        
    def bounce(t, A, B):        
        if t < 1 / 2.75:
            return interpolate_values(7.5625 * t * t, A, B)
        elif t < 2 / 2.75:
            t = t - (1.5 / 2.75)
            return interpolate_values(7.5625 * t * t + 0.75, A, B)
        elif t < 2.5 / 2.75:
            t = t - (2.25 / 2.75)
            return interpolate_values(7.5625 * t * t + 0.9375, A, B)
        else:
            t = t - (2.625 / 2.75)
            return interpolate_values(7.5625 * t * t + 0.984375, A, B)


##############################################################
# The Animation class is essentialy a tasklet which is called by a round-robin sheduler 
#  

class DeadAnimation(object):
    def run_step(self): pass
    
    @property
    def dead(self): return True
    
    def finish(self): pass
    
class Animation(object):
    __animation_queue = []
    __animation_task = None
    __task_running__ = False
    
    def __init__(self):
        Animation.__animation_queue.append(self)
        if Animation.__animation_task is None:
            Animation.__animation_task = PyGUI_Task(Animation.__animation_sheduler, 0.025, repeat = True, start = True)
            Animation.__task_running__ = True
        elif not Animation.__task_running__:
            Animation.__animation_task.start()
            Animation.__task_running__ = True
        
        self.callback = None

    @classmethod
    def running_animations(cls):
        return iter(Animation.__animation_queue)    
    
    @classmethod
    def __animation_sheduler(cls):
        dead_animations = []

        for animation in Animation.__animation_queue:
            animation.run_step()
            if animation.dead:
                dead_animations.append(animation)
                
        # delete all dead animations        
        for a in dead_animations:
            Animation.__animation_queue.remove(a)
    
        # if there are no animations left, stop the task so that we don't waste the CPU time
        # TODO: setup multiple tasks with different granularity so that we can track the stuff
        if len(Animation.__animation_queue) == 0:
            Animation.__animation_task.stop() 
            Animation.__task_running__ = False
            
    #---- override these
    @property
    def dead(self): return False
    
    
    def finish(self):
      callback = self.callback  
      self.__class__ = DeadAnimation
      if callback is not None:
        callback(self)
        
    def run_step(self): pass
        
     
def animation(fun):
    class A(Animation):
        def __init__(self, *args, **kwargs):
            super(A, self).__init__()
            self.__iterator = fun(*args, **kwargs)
        
        def run_step(self):
            try:
                self.__iterator.next()
            except StopIteration:
                self.finish()
    
    A.__name__ = fun.__name__
    return A
        
        
##############################################################
# The DelayedInvoke class calls a method after a certain time has expired
#  
class delayedInvoke(Animation):
    def __init__(self, delay, fun, *args, **kwargs):
        super(delayedInvoke, self).__init__()
        self.fun = fun
        self.delay = delay
        self.args = args
        self.kwargs = kwargs
        self.starttime = time.time()
        
    def run_step(self):
        t = time.time()
        if t - self.starttime >= self.delay:
            self.fun(*self.args, **self.kwargs)
            self.finish()
                    
        
##############################################################
# The AttributeAnimation class handles interpolation of a particular attribute
#  
        
class AttributeAnimation(Animation):
    def __init__(self, obj, attrname,  attrvalue, duration=1.0, interpolator = Interpolators.linear, repeat=False, swap_on_repeat = False, reset_value = False):
        super(AttributeAnimation, self).__init__()
        self.__wrobj = weakref.ref(obj)
        self.attrname = attrname
        self.A = getattr(obj, attrname)
        self.B = attrvalue
        self.interpolator = interpolator
        self.duration = duration
        if repeat is False:
            self.repeat = 1
        elif repeat is True:
            self.repeat = 1000000
        else:
            self.repeat = repeat
            
        self.swap_on_repeat = swap_on_repeat
        if reset_value:
            self.final_value = self.A
        else:
            self.final_value = self.B
        self.starttime = time.time()

    @property
    def obj(self): return self.__wrobj()
        

    def finish(self):
        if self.obj is not None:
            setattr(self.obj, self.attrname, self.final_value)
            
        super(AttributeAnimation, self).finish()
        
    def run_step(self):
        obj = self.obj
        
        if obj is None: # object has been released
            self.finish()
            return
        
        # get the interpolator value, don't forget to clip it
        t = min((time.time() - self.starttime)/self.duration, 1.0)

        
        # set the interpolated value
        setattr(obj, self.attrname, self.interpolator(t, self.A, self.B))

        # we are at the end
        if t == 1.0:
            # are we done repeating?
            self.repeat = self.repeat - 1
            
            if self.repeat == 0: self.finish()
            
            if self.swap_on_repeat:
                self.A, self.B = self.B, self.A
            
            self.starttime = time.time()
            
            
##############################################################
# The Animator is syntactic sugar for starting/stopping animations on attributes
#  
class Animator(object):
    def __init__(self, obj, interpolator = Interpolators.linear, duration = 1.0, repeat = False, swap_on_repeat = True, reset_value = False, callback = None):
        object.__setattr__(self, 'obj', obj)
        object.__setattr__(self, 'interpolator', interpolator)
        object.__setattr__(self, 'duration', duration)
        object.__setattr__(self, 'repeat', repeat)
        object.__setattr__(self, 'swap_on_repeat', swap_on_repeat)
        object.__setattr__(self, 'reset_value', reset_value)
        object.__setattr__(self, 'callback', callback)
        object.__setattr__(self, 'animations', [])
        
                
    def __setattr__(self, attr, val):
        if not hasattr(self.obj, attr):
            raise AttributeError('%s.%s' % (self.obj, attr))
        # transform the value if nessesary
        descriptor = getattr(self.obj.__class__, attr, None)
        if hasattr(descriptor, 'transformValue'):
          val = descriptor.transformValue(val)
        
        animation = AttributeAnimation(self.obj, attr, val, duration = self.duration, interpolator = self.interpolator, repeat=self.repeat, swap_on_repeat=self.swap_on_repeat, reset_value=self.reset_value)
        animation.callback = self.__animation_finished
        self.animations.append(animation)
        
    @property
    def finished(self):
        for animation in self.animations:
          if not animation.dead:
            return False
        else:
          return True
        
        
        
    def __animation_finished(self, animation):
        # ensure that all animations are dead
        if not self.finished:
          return
          
        if self.callback is not None:
          self.callback(self)
        
    def finish(self, *attributes):
        attributes = set(attributes)
        for animation in self.animations():
            try:
                if len(attributes) != 0:
                    if animation.attrname not in attributes: continue    
                animation.finish()
            except: pass
            
    @classmethod
    def finishAll(cls):
        for animation in Animation.running_animations():
            try:
                animation.finish()
            except: pass
            
            
# what about grouping animations in a context?
# like this:
#
# animationgroup = AnimationGroup()
# with animationgroup:
#    Animation(...)
#    Animation(...)
#    Animation(...)
#    Animation(...)
#
# these animations only start when the animation group is sheduled
#
#
# Ok, so lets like rewrite the animator a bit
# Now we need to shedule animations

def sheduler():
  print 'yes!'
        
task = PyGUI_Task(sheduler, 1, repeat = True, start = True)        
        
            
            
__all__ = ['Animator', 'delayedInvoke', 'animation', 'Interpolators']