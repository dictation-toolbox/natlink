#
# This file was part of Dragonfly.
# (c) Copyright 2007, 2008 by Christo Butcher
# Licensed under the LGPL.
#
# It is now improved and augmented for the Natlink project
# by Quintijn Hoogenboom for wider use 15/7/2019.
# See also unittestClipboard.py in Unimacro/unimacro_test

"""
This file implements an interface to the Windows system clipboard.
"""

import copy
import types
import time
import win32clipboard
import win32con

#===========================================================================

class Clipboard:

    #-----------------------------------------------------------------------

    format_text      = win32con.CF_TEXT
    format_oemtext   = win32con.CF_OEMTEXT
    format_unicode   = win32con.CF_UNICODETEXT
    format_locale    = win32con.CF_LOCALE
    format_hdrop     = win32con.CF_HDROP
    format_names = {
                    format_text:     "text",
                    format_oemtext:  "oemtext",
                    format_unicode:  "unicode",
                    format_locale:   "locale",
                    format_hdrop:    "hdrop",
                   }

    @classmethod
    def get_system_text(cls):
        """get text from the clipboard
        
        from natlinkclipboard import Clipboard
        
        simply call: text = Clipboard.get_system_text()
        
        as alias also Get_text can be used, so: text = Clipboard.Get_text()
        """
        if not OpenClipboardCautious():
            print('Clipboard, get_system_text: could not open clipboard')
            return
        try:
            for format in cls.format_unicode, cls.format_text, cls.format_oemtext:
                try:
                    content = win32clipboard.GetClipboardData(format)
                    if content: break
                except:
                    continue
            else:
                print('Clipboard, get_system_text, no content found')
                content = ""
            if content:
                content = content.replace('\0', '')
                if content.find('\r\n') >= 0:
                    content = content.replace('\r\n', '\n')
            return content
        finally:
            win32clipboard.CloseClipboard()

    Get_text = get_system_text

    @classmethod
    def set_system_text(cls, content):
        """set text to the clipboard
        
        First the clipboard is emptied. 
        
        This method fails when not in elevated mode.
        
        As alias, you can also call: Clipboard.Set_text("abacadabra")
        """
        print('set to clipboard: %s'% content)
        # content = str(content)
        if not OpenClipboardCautious():
            print('Clipboard, set_system_text: could not open clipboard')
            return
        clipNum = win32clipboard.GetClipboardSequenceNumber()
        # print 'clipboard number: %s'% clipNum
        try:
            win32clipboard.EmptyClipboard()
            if type(content) == bytes:
                format = cls.format_text
            elif type(content) == str:
                format = cls.format_unicode
            
            win32clipboard.SetClipboardData(format, content)
        except:
            print('Clipboard, cannot set text to clipboard: %s'% content)
        finally:
            clipNum2 = win32clipboard.GetClipboardSequenceNumber()
            if clipNum2 == clipNum:
                print('Clipboard, did not increment clipboard number: %s'% clipNum)
            win32clipboard.CloseClipboard()
    Set_text = set_system_text

    @classmethod
    def Get_clipboard_formats(cls):
        """returns a list of format types of current clipboard
        
        This is mainly meant for debugging purposes.
        """
        if not OpenClipboardCautious():
            print('get_clipboard_formats, could not open clipboard')
            return
        try:
            # 
            formats = _get_clipboard_formats_open_clipboard()
            return formats
        finally:
            win32clipboard.CloseClipboard()

    @classmethod
    def get_system_folderinfo(cls, waiting_time=0.05):
        """returns a tuple of file/folder info of selected files or folders
        
        As alias use Get_folderinfo, Get_hdrop or get_system_hdrop
        
        win32con.CF_HDROP is the parameter for calling this type of clipboard data
        
        """
        if not OpenClipboardCautious(waiting_time=waiting_time):
            print('Clipboard, get_system_folderinfo, could not open clipboard')
            return
        try:
            for i in range(3):
                try:
                    folderinfo = win32clipboard.GetClipboardData(cls.format_hdrop)
                    break
                except:
                    time.sleep(0.1)                    
                    continue
                else:
                    print('%s folderinfo: %s'% (i, repr(folderinfo)))
                    if folderinfo:
                        print('got it!')
                        return folderinfo
            else:
                print('Clipboard, get_system_folderinfo: no folder info found.')
                return
            return folderinfo
        finally:
            win32clipboard.CloseClipboard()
    
    get_system_hdrop = get_system_folderinfo
    Get_folderinfo = get_system_folderinfo
    Get_hdrop = get_system_folderinfo

    #-----------------------------------------------------------------------
    def __init__(self, contents=None, text=None, from_system=False, save_clear=False, debug=None):
        """initialisation of clipboard instance.
        
        save_clear can be set to True, current clipboard contents is saved and cleared
               saved contents are kept in self._backup and will be retrieved
               when instance is destroyed.
        from_system: obsolete option
        contents: can be set as initial contents of the clipboard (not tested, 2019)
        text: can be set as initial text contents of the clipboard (not tested, 2019)
        debug: default off, 1: important messages are printed, > 1 more messages are printed
        
        """
        self._contents = {}
        self._backup = None
        self.debug = debug or 0
        if not OpenClipboardCautious():
            if self.debug: print('Warning Clipboard: at initialisation could not open the clipboard')
            return
        self.current_sequence_number = win32clipboard.GetClipboardSequenceNumber()
        if self.debug > 1: print('current_sequence_number: %s'% self.current_sequence_number)

        # If requested, retrieve current system clipboard contents.
        if from_system:
            self.copy_from_system(save_clear=save_clear)
        elif save_clear:
            self.copy_from_system(save_clear=save_clear)

        # Process given contents for this Clipboard instance.
        if contents:
            try:
                self._contents = dict(contents)
            except Exception as e:
                raise TypeError("Clipboard: Invalid contents: %s (%r)" % (e, contents))

        # Handle special case of text content.
        if not text is None:
            self._contents[self.format_unicode] = str(text)

    def __del__(self):
        """restore clipboard if self._backup contains data
        
        This is so if save_clear is True when the instance was created,
        and when the clipboard held data at that moment.
        
        Note: need elevated mode for setting the clipboard...
        """
        if self._backup:
            self.restore()

    def __str__(self):
        arguments = []
        skip = []
        if not self._contents:
            arguments = ["(empty)"]
        else:
            text = self.get_text()
            if text:
                if len(text) > 20:
                    shorter = text[:10] + ' // ' + text[-10:]
                    arguments.append(repr(shorter))
                else:
                    arguments.append(repr(text))
                    
                skip.append(self.format_text)
                skip.append(self.format_unicode)
                skip.append(self.format_oemtext)
            else:
                arguments.append("(no_text)")
            for format in sorted(self._contents.keys()):
                if format in skip:
                    continue
                if format in self.format_names:
                    arguments.append(self.format_names[format])
                else:
                    arguments.append(repr(format))
        arguments = ", ".join(str(a) for a in arguments)
        return "%s(%s)" % (self.__class__.__name__, arguments)

    def copy_from_system(self, formats=None, save_clear=False, waiting_interval=None, waiting_iterations=None):
        """Copy the Windows system clipboard contents into this instance.

            Arguments:
             - *formats* (iterable, default: None) -- if not None, only the
               given content formats will be retrieved.  If None, all
               available formats will be retrieved.
             - *save_clear* (boolean, default: False) -- if true, the Windows
               system clipboard will be saved in self._backup, and
               cleared after its contents have been retrieved.
               Will be restored from self._backup when the instance is destroyed.
               If false contents are retrieved in self._contents
        """
        if waiting_interval or waiting_iterations:
            waiting_interval = waiting_interval or 0.025
            waiting_iterations = waiting_iterations or 10
            result = self._wait_for_clipboard_change(waiting_interval, waiting_iterations)
            if result is None:
                print("no clipboard change")
                return
            if result:
                if result > waiting_iterations*0.7 or self.debug:
                    print(f'did have to wait {result} steps of {waiting_iterations} with interval of {waiting_interval:.3f} seconds.')
        if not OpenClipboardCautious():
            if self.debug: print('Clipboard copy_from_system, could not open clipboard')
            return

        try:                
        # Determine which formats to retrieve.
            contents = self._get_clipboard_data_from_system(formats=formats)

            # Retrieve Windows system clipboard content.
            if save_clear:
                if contents:
                    self._backup = copy.copy(contents)
                    if self.debug > 1: print('Clipboard, set backup to: %s'% repr(self._backup))
                else:
                    self._backup = None
                self._contents = None
                win32clipboard.EmptyClipboard()
            else:
                if contents:
                    self._contents = copy.copy(contents)
                else:
                    self._contents = None
            return contents
        finally:    
            # Clear the system clipboard, if requested, and close it.
            self.current_sequence_number = win32clipboard.GetClipboardSequenceNumber()
            win32clipboard.CloseClipboard()
            pass

    def _get_clipboard_data_from_system(self, formats=None):
        """once the clipboard is opened, just get the clipboard data
        
        meant as internal functions, called from copy_from_system
        return the contents as a dict, see for example method get_text
        also leave the contents in self._contents
        """
        contents = {}
        self._contents = {}
        if not formats:
            formats = _get_clipboard_formats_open_clipboard()
        elif isinstance(formats, int):
            formats = (formats,)

        # Verify that the given formats are valid.
        if not formats:
            if self.debug > 1: print('_get_clipboard_data_from_system, no formats available, empty clipboard...')
            return contents

        if formats:
            for format in formats:
                # if not format in self.format_names.keys():
                #     # print 'not getting clipboard for format: %s'% format
                #     continue
                try:
                    content = win32clipboard.GetClipboardData(format)
                    contents[format] = content
                except:
                    pass  # unknown formats, which cannot be handled
                    # # print("_get_clipboard_data_from_system, format %s (%s) not available"% (format, self.format_names[format]))
                    # actual_formats = _get_clipboard_formats_open_clipboard()
                    # if actual_formats:
                    #     print('_get_clipboard_data_from_system, formats asked for not available: %s, available are: %s'% (formats, actual_formats))
                    # else:
                    #     print('_get_clipboard_data_from_system, clipboard empty')
                    # return {}
            self._contents = contents
            return contents

    def copy_to_system(self, data=None, clear=True):
        """Copy the contents of this instance to the Windows clipboard

            Arguments:
            - data: text or dict of clipboard items (format, content) pairs
             - *clear* (boolean, default: True) -- if true, the Windows
               system clipboard will be cleared before this instance's
               contents are transferred.

        """
        if not OpenClipboardCautious():
            print('copy_to_system, could not open clipboard')
            return
        try:
            # Clear the system clipboard, if requested.
            if clear:
                try:
                    win32clipboard.EmptyClipboard()
                except:
                    if self.debug > 1: print('Clipboard, cannot EmptyClipboard, need more rights, can also not restore backup of clipboard')
    
            # Transfer content to Windows system clipboard.
            data = data or self._contents
            if data is None:
                return
            elif isinstance(data, str):
                self.get_text(data)
            elif type(data) == dict:
                for format, content in list(data.items()):
                    win32clipboard.SetClipboardData(format, content)
            else:
                
                if self.debug: print("Clipboard, copy_to_system, invalid type of data: %s"% type(data))
                if self.debug > 1: print("data: %s\n========"% repr(data))
                return 
        finally:
            self.current_sequence_number = win32clipboard.GetClipboardSequenceNumber()
            win32clipboard.CloseClipboard()

    def Set_text_and_paste(t):
        """a one shot function to past text back into the application
        """
        if type(t) == str and t:
            self.copy_to_system(data=t)
            pass
        #### to be finished


    def restore(self):
        """restore the _backup to the system clipboard
        """
        if self._backup:
            self.copy_to_system(self._backup, clear=True)
        else:
            if self.debug: print('Clipboard restore, nothing to restore')
            
    def clear_clipboard(self):
        """Empty the clipboard and clear the internal clipboard data
        
        assume the clipboard is open
        
        this will be done at init phase with save_clear == True
        """
        if self.debug > 1:
            print("clear_clipboard, before start, sequence number: %s"% self.current_sequence_number)

        if not OpenClipboardCautious():
            print('copy_to_system, could not open clipboard')
            return
        try:        
            win32clipboard.EmptyClipboard()
            self._contents = None
        except:
            print("clipboard, clear_clipboard, could not clear the clipboard")
        finally:
            self.current_sequence_number = win32clipboard.GetClipboardSequenceNumber()
            if self.debug > 1:
                print("clear_clipboard, new sequence number: %s"% self.current_sequence_number)
            win32clipboard.CloseClipboard()
    
    def has_format(self, format):
        """Determine whether this instance has content for the given format

            Arguments:
             - *format* (int) -- the clipboard format to look for.
        """
        return (format in self._contents)

    def get_format(self, format):
        """Retrieved this instance's content for the given *format*.

            Arguments:
             - *format* (int) -- the clipboard format to retrieve.

            If the given *format* is not available, a *ValueError*
            is raised.
        """
        try:
            return self._contents[format]
        except KeyError:
            raise ValueError("Clipboard format not available: %r"
                             % format)

    def set_format(self, format, content):
        self._contents[format] = content

    def has_text(self, waiting_interval=None, waiting_iterations=None):
        """ Determine whether this instance has text content. """
        
        if self.contents:
            return (self.format_unicode in self._contents
                    or self.format_text in self._contents)
        else:
            return False

    def get_text(self, waiting_interval=None, waiting_iterations=None, replaceNullChar=True):
        """get the text (mostly unicode) contents of the clipboard
        
        This method first does a copy from system.
        
        If no text content available, return ""
        """
        contents = self.copy_from_system(formats = [self.format_unicode, self.format_text], waiting_interval=waiting_interval, waiting_iterations=waiting_iterations)
        text = ""
        if contents:
            if self.format_unicode in contents:
                text = contents[self.format_unicode]
                if text.find('\r\n') >= 0:
                    text = text.replace('\r\n', '\n')
                if text.find('\0') >= 0:
                    if replaceNullChar:
                        text = text.replace('\0', '')
            elif self.format_text in contents:
                text = contents[self.format_text]
            else:
                print("get contents, but no expected format: %s"% contents.keys())
                text = ""
        if text.find('\r\n') >= 0:
            text = text.replace('\r\n', '\n')
        return text

    def set_text(self, content):
        self._contents[self.format_unicode] = str(content)

    text    = property(
                       lambda self:    self.get_text(),
                       lambda self, d: self.set_text(d)
                      )

    def get_folderinfo(self, waiting_interval=None, waiting_iterations=None):
        """Retrieve this instance's folderinfo (also hdrop)
        
        do a copy_from_system automatically
           
        This should be a tuple of valid paths. The paths are not checked.

        If no valid info, return None
        """
        self.copy_from_system(waiting_interval=waiting_interval, waiting_iterations=waiting_iterations)
        if self.format_hdrop in self._contents:
            result = self._contents[self.format_hdrop]
            if type(result) == tuple:
                return result

    def save_sequence_number(self):
        """get the Clipboard Sequence Number and store in instance
        
        It is set in self.current_sequence_number, no return
        """
        self.current_sequence_number = win32clipboard.GetClipboardSequenceNumber()
        
    def _wait_for_clipboard_change(self, waiting_time, waiting_iterations):
        """wait a few steps until the clipboard is not changed.
        
        The previous Clipboard Sequence Number should be in
        the instance variable self.current_sequence_number
        
        This value is set when opening the clipboard, or in this internal function.
        
        When in doubt, call _set_sequence_number, before doing a copy!
        
        return True if changed
        """
        try:
            w_time = float(waiting_time)
        except ValueError:
            w_time = 0.001
        if w_time > 0.55:
            print('Clipboard, _wait_for_clipboard_change, waiting time too long, set to 0.1'% w_time)
            w_time = 0.001
        try:
            n_wait = int(waiting_iterations)
        except ValueError:
            n_wait = 4
        if n_wait <= 0:
            n_wait = 4
            
        for i in range(n_wait):
            new_sequence_number = win32clipboard.GetClipboardSequenceNumber()
            if new_sequence_number > self.current_sequence_number:
                self.current_sequence_number = new_sequence_number
                if i:
                    if self.debug: print('---Clipboard changed after %s steps of %.4fs (%.4f)'% (i, w_time, i*w_time))
                else:
                    if self.debug > 1: print('_wait_for_clipboard_change, clipboard changed immediately')
                # time.sleep(w_time)
                return i
            time.sleep(w_time)
        # no result:
        time_waited = n_wait*w_time
        if self.debug: print('Clipboard, no change in clipboard in %.4f seconds'% time_waited)


    
    get_hdrop = get_folderinfo

def _get_clipboard_formats_open_clipboard():
    """return clipboard formats available, when clipboard is open
    
    """
    formats = []
    f = win32clipboard.EnumClipboardFormats(0)
    while f:
        formats.append(f)
        f = win32clipboard.EnumClipboardFormats(f)
    return formats

def OpenClipboardCautious(nToTry=4, waiting_time=0.1):
    """sometimes, wait a little before you can open the clipboard...
    """
    for i in range(nToTry):
        try:
            win32clipboard.OpenClipboard()
        except:
            time.sleep(waiting_time)
            continue
        else:
            # wait = (i+2)*waiting_time
            if i:
                print('had to wait, and extra wait %s OpenClipboardCautious: %s seconds'% (i, wait))
            time.sleep(waiting_time)
            return True
    
