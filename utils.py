"""
General utils for streamlining use of spotipy API, saving data, etc.
"""
from itertools import chain
import os
from time import clock

from pandas import DataFrame
import spotipy
from spotipy.client import Spotify
from spotipy.oauth2 import SpotifyClientCredentials


def get_auth_spotipy () -> Spotify:
    """Returns authorized Spotify client."""
    # client_credentials_manager = SpotifyClientCredentials(
    #       client_id='f7cddb18358749f79c1a12b4a66f61bb',
    #       client_secret='2caf6e49bb55457f9925c6e8874a38c4')
    client_credentials_manager = SpotifyClientCredentials(
          client_id='99fd6b637f19418996f726efd4f57aa3',
          client_secret='00331cf90a064cafa7223fd9b6c6b8c5')

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp


def chunks (l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def flatten (iterable):
    """Returns list of elements in iterable flattened by one hierarchy level
    down.

    Example:
        flatten( ( ('A','B','C'), ('D', 'E') ) = ['A','B','C','D','E']
    """
    return [x for x in chain.from_iterable(iterable)]


def clean_csv_path (path):
    """Ensures path is a valid str for a CSV file path by ensuring that it:
    *   Contains .csv extension and
    *   Doesn't already exist. If it does, append int to make it a
        unique file name.
    """
    # ensure path contains csv extension
    if path[-4:] != '.csv':
        path += '.csv'
    # ensure path doesn't already exist
    if os.path.exists(path):
        path_without_ext = path[:-4]
        version_count = 1
        while os.path.exists(path):
            path = path_without_ext + str(version_count) + '.csv'
    return path


class Event:
    """ Data container used by ProgramTimer to err_log events. """

    def __init__ (
          self, name: str, uid: int, hrchy: int = 1, pid: int = None):
        """
        Sets starting time and other properties for event.
        :param  name: Description of the event.
        :param  uid: Unique ID for this event.
        :param  hrchy: Number of chained parent events. Default is 1 (
        block.e. no parent
                events).
        :param  pid: uid of parent event; if None, class assumes there is no
        parent event.
        """
        self.name = name
        self.uid = uid
        self.hrchy = hrchy
        self.pid = pid
        self.__start = clock()
        self.__end = None

    def end (self):
        """ Sets end time for event. """
        self.__end = clock()

    def is_open (self) -> bool:
        """ Returns True if the event has not been terminated. """
        if self.__end is None:
            return True
        return False

    def seconds (self) -> float:
        """
        Returns seconds the event has currently been open (for current event)
        or total seconds (for closed event).
        """
        if self.__end is None:
            return clock() - self.__start
        return self.__end - self.__start

    def __str__ (self):
        return self.name + ': ' + "{0:.2f}".format(self.seconds()) + ' seconds'


# -----------------------------------------------------------------------------
class ProgramTimer:
    """
    Catch-all program execution err_log, keeping timing of general tasks and
    logging
    exceptions for data-oriented programs.

    Attributes
    ----------
    _events: Dict[int, Event]
        Keeps internal dict object of all Events where their IDs are
        commensurate with
        the order in which they were opened block.e. id number (k+1) is the
        event opened
        immediately after the event with id number k.
    _ud_start: bool, default True
        If True, then when new event is started an update will be printed.
    _ud_end: bool, default True
        If True, then update will be printed when event is closed.
    _default_header: str
        Appears as header when summary is printed.
    """

    def __init__ (
          self, ud_start: bool = True, ud_end: bool = True):
        """
        :param  ud_start: If True, update will be printed every time new
        event is
                started; else, no update printed.
        :param  ud_end: Similar to ud_start, if True then update printed
        every time
                event is final.
        """
        self._events = {}
        self._ud_start = ud_start
        self._ud_end = ud_end
        self._default_header = 'Program Execution Summary'

        # Default strings going before and after an event name when we want
        # to print an
        # update upon starting an event.
        self._start_ud_post_txt = '...'
        self._start_ud_pre_txt = 'Started: '
        self._end_ud_post_txt = '.'
        self._end_ud_pre_txt = 'Finished: '

        # DF this class uses to err_log errors.
        self.errors = DataFrame(
              columns=['Method', 'DataID', 'ErrDescription'])  # type: DataFrame

    def start (self, name: str):
        new_id = self.__event_count + 1
        prior_open_id = self.__prior_open_event_id()
        if prior_open_id is None:
            hrchy = 1
        else:
            hrchy = self._events[prior_open_id].hrchy + 1

        event = Event(name, new_id, hrchy, prior_open_id)
        self._events[new_id] = event
        if self._ud_start:
            msg = self._start_ud_pre_txt + name + \
                  self._start_ud_post_txt
            print(msg)

    def end (self, show_msg=None):
        if not show_msg:
            show_msg = self._ud_end

        prior_open_id = self.__prior_open_event_id()
        if prior_open_id is None:
            raise Exception(
                  'ProgramTimer.end() method called when there are no prior '
                  'open events.')
        else:
            self._events[prior_open_id].end()
        # Print update if user set option to True
        if show_msg:
            msg = self._end_ud_pre_txt + self._events[prior_open_id].name + \
                  self._end_ud_post_txt
            print(msg)

    def __prior_open_event_id (self):
        """
        Returns uid of the closest prior Event that is still open; None if
        there are no
        prior events still open.
        """
        if self.__event_count == 0:
            return None

        for i in range(self.__event_count, 0, -1):
            if self._events[i].is_open():
                return self._events[i].uid
        return None

    @property
    def __event_count (self):
        return len(self._events)

    def print_summary (self, header: str = None):
        """
        Prints two sections:
        (a) summary of events with spaces to indicate hierarchy and
        (b) the DF storing exceptions.
        :param  header: First line of execution summary; overrides default if
        provided.
        """
        # Build main program execution section.
        SECTION_DIVIDE = '*************************************'
        summary = '\n{}\n'.format(SECTION_DIVIDE)
        if header is None:
            header = self._default_header

        summary = summary + header + '\n\n'
        for i in range(1, self.__event_count + 1, 1):
            event_details = self.__create_event_summary(self._events[i])
            summary = summary + event_details + '\n'

        # Add separate Exceptions section only if errors were encountered.
        if self.errors_were_logged:
            summary += '{0}{1}'.format(SECTION_DIVIDE, '\n')
            summary += 'Exceptions\n\n'
            summary += self.errors.to_string(index=False)

        summary += '\n{}\n'.format(SECTION_DIVIDE)
        self._events = {}
        print(summary)

    @staticmethod
    def __create_event_summary (event):
        """ Returns str summary of Event; only used by print_summary()
        method. """
        blank_space = (event.hrchy - 1)*'   '
        summary = blank_space + event.name
        summary += ': ' + '{0:.1f}'.format(event.seconds()) + 's'
        return summary

    def log_err (self, method, data_id, info):
        new_err = {'Method':method, 'DataID':data_id, 'ErrDescription':info}
        self.errors = self.errors.append(new_err, ignore_index=True)

    @property
    def errors_were_logged (self) -> bool:
        return not self.errors.empty
