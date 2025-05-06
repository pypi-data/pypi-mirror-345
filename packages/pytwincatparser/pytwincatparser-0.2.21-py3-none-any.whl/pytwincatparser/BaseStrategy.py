from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from .TwincatDataclasses import TcObjects


class BaseStrategy(ABC): # extract to seperate file


    @abstractmethod
    def check_strategy(self, path:Path) -> bool:
        raise NotImplementedError()
    
    @abstractmethod
    def load_objects(self, path:Path) -> List[TcObjects]:
        raise NotImplementedError()
    