from typing import Optional

from classad._classad import ClassAd
from classad._primitives import Undefined, Error


class Expression:
    def evaluate(self, my: ClassAd, target: ClassAd) -> \
            Optional[bool, Undefined, Error]:
        return NotImplemented
