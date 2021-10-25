from pprint import pformat

class OrchestraInstance:

    def __init__(self, obj=None):
        self.obj = obj  if obj is not None else {}

    def root(self):
        return self.obj

    def __str__(self):
        return pformat(self.obj)

    def metadata(self):
        return self.obj["fixr:metadata"]