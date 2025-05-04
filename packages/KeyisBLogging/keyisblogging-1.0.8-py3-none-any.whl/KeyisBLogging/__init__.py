"""
logging
*******

*created by KeyisB*

-==============================-




Copyright (C) 2024 KeyisB. All rights reserved.

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to use the Software exclusively for
projects related to the MMB or GW systems, including personal,
educational, and commercial purposes, subject to the following
conditions:

1. Copying, modification, merging, publishing, distribution,
sublicensing, and/or selling copies of the Software are
strictly prohibited.
2. The licensee may use the Software only in its original,
unmodified form.
3. All copies or substantial portions of the Software must
remain unaltered and include this copyright notice and these terms of use.
4. Use of the Software for projects not related to GW or
MMB systems is strictly prohibited.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR
A PARTICULAR PURPOSE, AND NON-INFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM, OUT OF, OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

__GW_VERSION__ = "0.0.0.0.4"
__version__ = "1.0.6"

from typing import Callable, List, Any, Dict
import inspect
import traceback
import colorama
from colorama import Fore

colorama.init(autoreset=True)

class __Log:
    INFO = 'info'
    FATAL = 'fatal'
    ERROR = 'error'
    DEBUG = 'debug'
    OK = 'ok'

    def __init__(self) -> None:

        self.__log_listener: List[Callable] = []

        self.__config: Dict[str, Any] = {
            'logConfig': '[{level}][{File}] -> {msg}',
            'print': True,
            'files': {
                'on': [],
                'off': []
            }
        }

        self._colors = {
            'info':Fore.CYAN,
            'fatal':Fore.RED,
            'error':Fore.RED,
            'debug':Fore.YELLOW,
            'ok':Fore.GREEN
        }


    

    def info(self, msg: Any, *args, **kwargs):
        """
        Добавляет информационный лог.
        """
        self._log(self.INFO, msg, *args, **kwargs)
    def fatal(self, msg: Any, *args, **kwargs):
        """
        Добавляет фатальный лог.
        """
        self._log(self.FATAL, msg, *args, **kwargs)
    def error(self, msg: Any, *args, **kwargs):
        """
        Добавляет лог ошибки.
        """
        traceback_ = traceback.format_exc()
        self._log(self.ERROR, msg, traceback_,  *args, **kwargs)
    def debug(self, msg: Any, *args, **kwargs):
        """
        Добавляет отладочный лог.
        """
        self._log(self.DEBUG, msg, *args, **kwargs)
    def ok(self, msg: Any, *args, **kwargs):
        """
        Добавляет лог ok.
        """
        self._log(self.OK, msg, *args, **kwargs)
    def _log(self, level: Any, msg: str, *args, **kwargs):
        """
        Основная функция для добавления логов.
        """
        logVars = {
            'level': level,
            'msg': msg
        }
        __config = self.__config

        if kwargs.get('fullExecutiblePath', None):
            __config['logConfig'] = '[{level}][{fullExecutiblePath}] -> {msg}'


        if '{File}' in __config['logConfig']:
            frame = inspect.currentframe()
            stack = inspect.getouterframes(frame)

            # Используем стандартный способ получения имени файла и функции
            caller = stack[2]
            file_name = caller.filename
            #file_name_short = file_name.split('\\')[-1]
            function_name = caller.function
            #class_name = caller.frame.f_locals['self'].__class__.__name__ if 'self' in caller.frame.f_locals else None
            line_number = caller.lineno

            logVars['File'] = f'File "{file_name}", line {line_number}, in {function_name}'

            if self.__config['files']['off']:
                if file_name in self.__config['files']['off']:
                    return
            
            if self.__config['files']['on']:
                if file_name not in self.__config['files']['on']:
                    return
        

        if '{fullExecutiblePath}' in __config['logConfig']:
            frame = inspect.currentframe()
            stack = inspect.getouterframes(frame)
            q = [f'\n     File "{s.filename}", line {s.lineno}, in {s.function}' for s in stack]
            q2 = []
            for i in q:
                if '"<frozen importlib._bootstrap>"' not in i and "<frozen importlib._bootstrap_external>" not in i:
                    q2.append(i)

            q2.reverse()

            q2 = q2[:-2]
            full_call_path = " -> ".join(q2)

            logVars['fullExecutiblePath'] = f'Full Call Path: {full_call_path}\n     Error:'




        
            

        log = __config['logConfig'].format(**logVars)
        if __config['print']:
            print(self._colors.get(level, '') + log, end=kwargs.get('end', '\n'))

        for listener in self.__log_listener:
            try:
                listener(log)
            except Exception as e:
                print(f'Ошибка при вызове слушателя логов: {e}')
    
    def setPrinting(self, state: bool = True) -> None:
        """
        Устанавливает режим печати логов.
        """
        self.__config['print'] = state
    def addLogListener(self, listener: Callable) -> None:
        """
        Устанавливает слушателя логов.
        """
        self.__log_listener.append(listener)
    def removeLogListener(self, listener: Callable) -> None:
        if listener in self.__log_listener:
            self.__log_listener.remove(listener)
        else:
            logging.error(f'Слушатель логов -> [{listener}] не найден')

    def setLogFormat(self, config: str) -> None:
        """
        Устанавливает конфигурацию логов.

        [{level}][{File}] -> {msg}

        [{level}][{fullExecutiblePath}] -> {msg}

        """
        self.__config['logConfig'] = config


    def addFilterFile(self, file: str, off: bool = True) -> None:
        """
        Добавляет файл в список игнорируемых файлов для логов.
        """
        if off:
            if file not in self.__config['files']['off']:
                self.__config['files']['off'].append(file)
        else:
            if file not in self.__config['files']['on']:
                self.__config['files']['on'].append(file)

logging = __Log()
logging.setPrinting(True)
logging.setLogFormat('[{level}][{File}] -> {msg}')
#logging.setLogFormat('[{level}][{fullExecutiblePath}] -> {msg}')

