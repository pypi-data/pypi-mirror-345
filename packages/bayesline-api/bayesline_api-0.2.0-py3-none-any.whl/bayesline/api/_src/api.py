import abc

from bayesline.api._src.equity.api import AsyncBayeslineEquityApi, BayeslineEquityApi
from bayesline.api._src.permissions import AsyncUserPermissionsApi, UserPermissionsApi


class BayeslineApi(abc.ABC):

    @property
    @abc.abstractmethod
    def equity(self) -> BayeslineEquityApi: ...

    @property
    @abc.abstractmethod
    def permissions(self) -> UserPermissionsApi: ...


class AsyncBayeslineApi(abc.ABC):

    @property
    @abc.abstractmethod
    def equity(self) -> AsyncBayeslineEquityApi: ...

    @property
    @abc.abstractmethod
    def permissions(self) -> AsyncUserPermissionsApi: ...
