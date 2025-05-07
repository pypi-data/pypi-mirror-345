class Include():
    __slots__ = [ "__sql", "__name", "__match", "__source" ]

    def __init__(self, sql: str, name: str, match: str, source: str):
        self.__sql = sql
        self.__name = name
        self.__match = match
        self.__source = source

    @property
    def sql(self) -> str:
        return self.__sql

    @property
    def name(self) -> str:
        return self.__name

    @property
    def match(self) -> str:
        return self.__match

    @property
    def source(self) -> str: # pragma: no cover
        return self.__source
