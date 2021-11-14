class COGReader:
    def __init__(self, url: str):
        self._url = url

    @property
    def url(self):
        return self._url
