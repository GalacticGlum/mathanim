import bisect
from abc import ABC, abstractmethod

class SequenceItem(ABC):
    '''
    The base class for any item that can be added to a :class:`Sequence`.
    
    '''

    @abstractmethod
    def get_value(self, time):
        '''
        Gets the value of the sequence item at the specified time.

        :param time:
            The time, in seconds, relative to the start of the sequence item.
        :returns:
            The value of the sequence item at the specified time.

        '''

        pass

class Sequence(SequenceItem):
    '''
    A sequence is a chain of actions (and/or other sequences), executed one after the other, used to build animations.

    '''

    def __init__(self, *sequence_items):
        '''
        Initializes an instance of :class:`Sequence`.

        :param *sequence_items:
            An optional list of nested sequence items.

        '''

        # Time intervals is an list containing the end time of each sequence item.
        self._time_intervals = [0]
        self.items = []
        self.add(*sequence_items)
            
    def get_value(self, time):
        '''
        Gets the value of the sequence at the specified time.

        :param time:
            The time relative to the start of the sequence, in seconds.
        :returns:
            The value of the sequence after the specified time.
            If the time exceeds the duration of the sequence, None is returned.

        '''

        if time > self.duration: return None
        item_index = max(bisect.bisect_left(self._time_intervals, time) - 1, 0)
        return self.items[item_index].get_value(time - self._time_intervals[item_index])

    @property
    def duration(self):
        '''
        Gets the total duration of the sequence.

        '''

        return sum(item.duration for item in self.items)

    def add(self, *sequence_items):
        '''
        Adds a list of sequence items to this sequence.

        '''

        for item in sequence_items:
            self.items.append(item)
            self._time_intervals.append(self._time_intervals[-1] + item.duration)

        return self

def chain(*sequence_items):
    '''
    Chains a list of sequence items together so that they occur sequentially.

    :note:
        An action may also be passed into method and the chaining will still work.
        This is because an action is considered a sequence.

    :param *sequence_items:
        The sequence items to chain.
    :returns:
        A sequence consisting of the items in the order of the input.

    '''

    return Sequence(*sequence_items)

def accumulate(*sequence_items):
    '''
    Returns a new sequence whose output is the sum of all the individual sequence items.

    :note:
        The duration of the accumulated sequence is the maximum duration of all the inputs.

    :param *sequence_items:
        The sequence items to accumulate.
    :returns:
        A sequence consisting of the sum of the input items.
    '''

    from mathanim.actions import Procedure

    def _accumulate_func(time, items):
        values = [item.get_value(time) for item in items]
        return sum(v for v in values if v is not None)       

    result_duration = max(item.duration for item in sequence_items)
    return Sequence(Procedure(result_duration, _accumulate_func, sequence_items))
    