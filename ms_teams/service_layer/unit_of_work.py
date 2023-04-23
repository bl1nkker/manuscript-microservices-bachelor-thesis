# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
import abc

import adapters as repository


class AbstractUnitOfWork(abc.ABC):
    event: repository.AbstractEventRepository
    user: repository.AbstractUserRepository
    team: repository.AbstractTeamRepository

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
        self.event = repository.EventRepository()
        self.user = repository.ManuscriptUserRepository()
        self.team = repository.TeamRepository()
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)

    def commit(self):
        pass

    def rollback(self):
        pass


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.event = repository.FakeEventRepository()
        self.user = repository.FakeManuscriptUserRepository()
        self.team = repository.FakeTeamRepository()

    def commit(self):
        self.committed = True

    def rollback(self):
        pass
