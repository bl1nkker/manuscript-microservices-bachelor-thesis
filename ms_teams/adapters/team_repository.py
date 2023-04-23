import abc
from typing import Union, List

import app.models as models
import domain.fake_models as fake_models


class AbstractTeamRepository(abc.ABC):
    ''' 
    Репозиторий, отвечающий за управление [Team].
    '''
    @abc.abstractmethod
    def create(self, **kwargs):
        '''
        Создает [Team] и возвращает его

                Args:
                        **kwargs: Параметры для создания [Team]
                Returns:
                        [Student] - созданный студент
        '''

    @abc.abstractmethod
    def get(self, **kwargs):
        ''' 
        Возвращает [Team], если event существует

                Args:
                        kwargs: [dict] - словарь с параметрами для поиска

                Returns:
                        [Team] - найденный event
                        [None] - если event не найден
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def edit(self, id, **kwargs):
        ''' 
        Редактирует [Team]

                Args:
                        id: [int] - id event который нужно отредактировать
                        **kwargs: [dict] - словарь с параметрами для редактирования
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def list(self, include_deactivated=False, **kwargs):
        ''' 
        Возвращает список [Team]

                Args:
                        kwargs: [dict] - словарь с параметрами для поиска

                Returns:
                        [List[Team]] - список найденных event
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def deactivate(self, id):
        ''' 
        Удаляет [Team]

                Args:
                        id: [int] - id event который нужно удалить
        '''
        raise NotImplementedError


class TeamRepository(AbstractTeamRepository):

    def get(self, **kwargs) -> Union[models.Team, None]:
        return models.Team.objects.filter(**kwargs).first()

    def create(self, **kwargs) -> models.Team:
        return models.Team.objects.create(**kwargs)

    def edit(self, id, **kwargs) -> models.Team:
        team = models.Team.objects.get(id=id)
        for key, value in kwargs.items():
            if key == 'members':
                team.members.set(value)
                continue
            setattr(team, key, value)
        team.save()
        return team

    def list(self, include_deactivated=False, **kwargs, ) -> List[models.Team]:
        return models.Team.objects.filter(**kwargs, is_active=True) if not include_deactivated else models.Team.objects.filter(**kwargs)

    def deactivate(self, id) -> models.Team:
        team = models.Team.objects.get(id=id)
        team.is_active = False
        team.save()
        return models.Team.objects.get(id=id)


class FakeTeamRepository(AbstractTeamRepository):

    def __init__(self) -> None:
        self._teams = []
        self._id = 0

    def get(self, **kwargs) -> Union[fake_models.Team, None]:
        return super().get(**kwargs)

    def create(self, **kwargs):
        return super().create(**kwargs)

    def edit(self, id, **kwargs):
        return super().edit(id, **kwargs)

    def list(self, include_deactivated=False, **kwargs, ) -> List[fake_models.Team]:
        return super().list(include_deactivated, **kwargs)

    def deactivate(self, id):
        return super().deactivate(id)
