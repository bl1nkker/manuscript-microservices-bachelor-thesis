# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
import abc

import adapters as repository


class AbstractUnitOfWork(abc.ABC):
    user: repository.AbstractUserRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class DjangoORMUnitOfWork(AbstractUnitOfWork):

    def __enter__(self):
        self.user = repository.ManuscriptUserRepository()
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)

    def commit(self):
        pass

    def rollback(self):
        pass


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.user = repository.FakeManuscriptUserRepository()

    def commit(self):
        self.committed = True

    def rollback(self):
        pass
