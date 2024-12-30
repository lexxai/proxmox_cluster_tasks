class API:
    def __init__(self, backend):
        self.backend = backend
        self._cluster = None

    @property
    def cluster(self):
        if self._cluster is None:
            self._cluster = API_Cluster(self.backend)
        return self._cluster


class API_Cluster:
    def __init__(self, backend):
        self.backend = backend
        self._ha = None

    @property
    def ha(self):
        if self._ha is None:
            self._ha = API_ClusterHa(self.backend)
        return self._ha


class API_ClusterHa:
    def __init__(self, backend):
        self.backend = backend
        self._groups = None

    @property
    def groups(self):
        if self._groups is None:
            self._groups = API_ClusterHaGroups(self.backend.ha_groups)
        return self._groups


class API_ClusterHaGroups:
    def __init__(self, backend):
        self.backend = backend
        self.name = None

    def __call__(self, name):
        self.name = name
        return self

    def get(self): ...

    def create(self): ...

    async def aget(self): ...

    async def acreate(self): ...
