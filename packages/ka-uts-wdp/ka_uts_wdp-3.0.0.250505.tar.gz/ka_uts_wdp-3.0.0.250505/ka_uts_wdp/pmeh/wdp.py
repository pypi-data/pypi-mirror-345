"""
This module provides task scheduling classes for the management of OmniTracker
SRR (NHRR) processing for Department UMH.
    SRR: Sustainability Risk Rating
    NHRR: Nachhaltigkeits Risiko Rating
"""
import os
import time

from ka_uts_log.log import Log
from ka_uts_uts.utils.pac import Pac
from ka_uts_dic.dic import Dic
from ka_uts_obj.pathnm import PathNm

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from typing import Any
TyArr = list[Any]
TyDic = dict[Any, Any]
TyStr = str
TyPath = str

TnPath = None | TyPath


class PmeHandler(PatternMatchingEventHandler):
    """
    WatchDog Event Handler for pattern matching of files paths
    """
    msg_evt: TyStr = "Watchdog received {E} - {P}"
    msg_exe: TyStr = "Watchdog executes script: {S}"

    def __init__(self, patterns, scripts):
        # Set the patterns for PatternMatchingEventHandler
        # self.kwargs = kwargs
        super().__init__(
                patterns=patterns,
                ignore_patterns=None,
                ignore_directories=True,
                case_sensitive=False)
        self.scripts = scripts

    def on_created(self, event):
        """
        process 'files paths are created' event
        """
        _path = event.src_path
        Log.debug(f"Watchdog received created event - {_path}")
        # result = subprocess.run(scripts, capture_output=True, text=True)
        for _script in self.scripts:
            Log.debug(f"Watchdog executes script: {_script}")
            os.system(_script)

    def on_modified(self, event):
        _path = event.src_path
        Log.debug(f"Watchdog received mdified event - {_path}")
        # result = subprocess.run(scripts, capture_output=True, text=True)
        for _script in self.scripts:
            Log.debug(f"Watchdog executes script: {_script}")
            Log.debug(f"Watchdog executes script: {_script}")
            os.system(_script)


class WdP:
    """
    General Task class
    """
    @staticmethod
    def pmeh(kwargs: TyDic) -> None:
        """
        WatchDog Task for pattern matching of files paths
        """
        _path = PathNm.sh_path('in_dir_wdp', kwargs)
        # _patterns = kwargs.get('in_patterns_wdp', [])
        # _scripts = kwargs.get('scripts_wdp', [])
        # if isinstance(_patterns, str):
        #     _patterns = [_patterns]
        # if isinstance(_scripts, str):
        #     _scripts = [_scripts]
        _patterns: TyArr = Dic.get_as_array(kwargs, 'in_patterns_wdp')
        _scripts_wdp: TyArr = Dic.get_as_array(kwargs, 'scripts_wdp')
        # _path_bin: TyPath = Com.sh_path_bin()

        _scripts = []
        for _script in _scripts_wdp:
            _arr: TyArr = _script.split(':', 1)
            Log.debug(f"_script = {_script}")
            Log.debug(f"_arr = {_arr}")
            if len(_arr) == 2:
                _package = _arr[0]
                _script_new = _arr[1]
                _path_bin: TyPath = Pac.sh_path_by_package(_package, 'bin')
                Log.debug(f"_path_bin = {_path_bin}")
                _script = os.path.join(_path_bin, _script_new)
            _scripts.append(_script)

        Log.debug(f"_path = {_path}")
        Log.debug(f"_patterns = {_patterns}")
        Log.debug(f"_scripts = {_scripts}")

        _pmehandler = PmeHandler(_patterns, _scripts)
        _observer = Observer()
        _observer.schedule(_pmehandler, path=_path, recursive=False)
        _observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            _observer.stop()
        _observer.join()
