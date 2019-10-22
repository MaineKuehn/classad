from typing import Any

from classad._classad import ClassAd


class Expression:
    def evaluate(self, my: ClassAd, target: ClassAd) -> Any:
        return NotImplemented
