"""
Handling of more calls to the Natlink timer
Quintijn Hoogenboom, 25-4-2020

"""
#---------------------------------------------------------------------------
import copy
import time
import natlink
import sys
import traceback

natlinktimer = None


class GrammarTimer:
    """object which specifies how to call the natlinkTimer
    
    """
    def __init__(self, callback, interval, startNow=False, stopAtMicOff=False, maxIterations=None):
        curTime = self.starttime = round(time.time()*1000)
        self.callback = callback
        self.interval = interval
        self.nextTime = curTime + interval
        self.stopAtMicOff = stopAtMicOff
        self.startNow = startNow
        self.maxIterations = maxIterations
        pass

    def __str__(self):
        """make string with nextTime value relative to the starttime of the grammarTimer instance
        """
        result = f'grammartimer, interval: {self.interval}, nextTime (relative): {self.nextTime - self.starttime}'
        return result

    def __repr__(self):
        L = ['GrammarTimer instance:']
        for varname in 'interval', 'nextTime', 'stopAtMicOff', 'startNow', 'maxIterations':
            value = self.__dict__.get(varname, None)
            if not value is None:
                L.append(f'    {varname.ljust(13)}: {value}')
        return "\n".join(L)




class NatlinkTimer:  
    """
    This class utilises :meth:`natlink.setTimerCallback`, but multiplexes
    
    In this way, more grammars can use the single Natlink timer together.
    
    First written by Christo Butcher for Dragonfly, now enhanced by Quintijn Hoogenboom, May 2020
    
    """

    def __init__(self, minInterval=None):
        """initialize the natlink timer instance
        
        Should be called only once in a session
        
        The grammar callback functions are the keys of the self.callbacks dict,
        The corresponding values are GrammarTimer instances, which specify interval and possibly other parameters
        
        The minimum interval for the timer can be specified, is 50 by default.
        """
        self.callbacks = {}
        self.debug = None
        self.timerStartTime = self.getnow()
        self.minInterval = minInterval or 50
        self.tolerance = min(10, int(self.minInterval/4))
        
    def __del__(self):
        """stop the timer, when destroyed
        """
        self.stopTimer()
    
    def getnow(self):
        """get time in milliseconds
        """
        return round(time.time()*1000)

    
    def addCallback(self, callback, interval, debug=None):
        """add an interval 
        """
        self.debug = self.debug or debug
        now = self.getnow()

        if interval <= 0:
            self.removeCallback(callback)
            return
        if interval <= self.minInterval:
            if self.debug: print(f"addCallback {callback.__name}, set interval from {interval} to minInterval: {self.minInterval}")
        interval = round(interval)
        gt = GrammarTimer(callback, interval)
        self.callbacks[callback] = gt
        if self.debug: print("set new timer %s: %s (%s)"% (callback.__name__, interval, now))
        self.hittimer()
        return gt

    def removeCallback(self, callback, debug=None):
        """remove a callback function
        """
        self.debug = self.debug or debug
        if self.debug: print("remove timer for %s"% callback.__name__)

        try:
            del self.callbacks[callback]
        except KeyError:
            pass
        if not self.callbacks:
            if self.debug: print("last timer removed, setTimerCallback to 0")

            self.stopTimer()
            return
        
        self.hittimer()
        
    def hittimer(self):
        """move to a next callback point
        """
        now = self.getnow()
        nowRel = now - self.timerStartTime
        if self.debug: print("start hittimer at", nowRel)

        toBeRemoved = []
        # c = callbackFunc, g = grammarTimer
        decorated = [(g.interval, c, g) for (c, g)  in self.callbacks.items()]
        sortedList = sorted(decorated)
        
        
        for interval, callbackFunc, grammarTimer in sortedList:
            now = self.getnow()
            # for printing: 
            if self.debug: nowRel, nextTimeRel = now - self.timerStartTime, grammarTimer.nextTime - self.timerStartTime
            if grammarTimer.nextTime > (now + self.tolerance):
                if self.debug:
                    print(f'no need for {callbackFunc.__name__}, now: {nowRel}, nextTime: {nextTimeRel}')
                continue

            # now treat the callback, grammarTimer.nextTime > now - tolerance:
            hitTooLate = now - grammarTimer.nextTime
            
            if self.debug:
                print(f"do callback {callbackFunc.__name__} at {nowRel}, was expected at: {nextTimeRel}, interval: {interval}")

            ## now do the callback function:
            newInterval = None
            startCallback = now
            try:
                newInterval = callbackFunc()
            except:
                print(f"exception in callbackFunc ({callbackFunc}), remove from list")
                traceback.print_exc()
                toBeRemoved.append(callbackFunc)
                endCallback = None
            else:
                endCallback = self.getnow()
                
            if newInterval and newInterval >= 0:
                print(f"newInterval as result of {callbackFunc.__name__}: {newInterval}")
                grammarTimer.interval = interval = newInterval
            elif newInterval and newInterval <= 0:
                print(f"newInterval <= 0, as result of {callbackFunc.__name__}: {newInterval}, remove the callback function")
                toBeRemoved.append(callbackFunc)
                continue
            
            # if cbFunc ended correct, but took too much time, its interval should be doubled:
            if endCallback is None:
                pass
            else:
                spentInCallback = endCallback - startCallback
                if spentInCallback > interval:
                    if self.debug: print(f"spent too much time in {callbackFunc.__name__}, increase interval from {interval} to: {spentInCallback*2}")
                    grammarTimer.interval = interval = spentInCallback*2
                grammarTimer.nextTime += interval
                if self.debug:
                    nextTimeRelative = grammarTimer.nextTime - endCallback
                    print(f"new nextTime: {nextTimeRelative}, interval: {interval}, from gt instance: {grammarTimer.interval}")

        for gt in toBeRemoved:
            del self.callbacks[gt]
        
        if not self.callbacks:
            if self.debug: print("no callbackFunction any more, switch off the natlink timerCallback")
            self.stopTimer()
            return
        
        nownow = self.getnow()
        timeincallbacks = nownow - now
        if self.debug: print("time in callbacks: %s"% timeincallbacks)
        nextTime = min(gt.nextTime-nownow for gt in self.callbacks.values())
        if nextTime < self.minInterval:
            if self.debug: print(f"warning, nextTime too small: {nextTime}, set at minimum {self.minInterval}")
            nextTime = self.minInterval
        if self.debug: print("set nextTime to: %s"% nextTime)
        natlink.setTimerCallback(self.hittimer, nextTime)
        if self.debug:
            nownownow = self.getnow()
            timeinclosingphase = nownownow - nownow
            totaltime = nownownow - now
            print(f"time taken in closingphase: {timeinclosingphase}")
            print(f"total time spent hittimer: {totaltime}")
                    
    


    def stopTimer(self):
        """stop the natlink timer, by passing in None, 0
        """
        natlink.setTimerCallback(None, 0)
        


def setTimerCallback(callback, interval, debug=None):
    """This function sets a callback
    
    Interval in seconds, unless larger than 24
    callback: the function to be called
    """
    global natlinktimer
    if not natlinktimer:
        natlinktimer = NatlinkTimer()
    if not natlinktimer:
        raise Exception("NatlinkTimer cannot be started")
    
    if callback is None:
        raise Exception("stop the timer callback with natlinktimer.removeCallback(callback)")
    
    if interval:
        gt = natlinktimer.addCallback(callback, interval, debug=debug)
        return gt
    else:
        natlinktimer.removeCallback(callback, debug=debug)

def removeTimerCallback(callback, debug=None):
    """This function removes a callback from the callbacks dict
    
    callback: the function to be called
    """
    global natlinktimer
    if not natlinktimer:
        print("no timers active, cannot remove %s from natlinktimer"% callback)
        return
    
    if callback is None:
        raise Exception("please stop the timer callback with removeTimerCallback(callback)\n    or with setTimerCallback(callback, 0)")
    
    natlinktimer.removeCallback(callback, debug=debug)

def stopTimerCallback():
    """should be called at destroy of Natlink
    """
    global natlinktimer
    if natlinktimer:
        del natlinktimer

if __name__ == "__main__":
    to = GrammarTimer(interval=100, curTime=10340, t=123, u=None)
    pass