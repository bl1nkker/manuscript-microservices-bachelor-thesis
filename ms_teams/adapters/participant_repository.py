import abc
from typing import Union, List

import app.models as models
import domain.fake_models as fake_models


class AbstractParticipantRepository(abc.ABC):
    '''
    Репозиторий, отвечающий за управление [Participant].
    '''
    @abc.abstractmethod
    def create(self, **kwargs):
        '''
        Создает [Participant] и возвращает его

                Args:
                        **kwargs: Параметры для создания [Participant]
                Returns:
                        [Participant] - созданный студент
        '''

    @abc.abstractmethod
    def get(self, **kwargs):
        '''
        Возвращает [Participant], если event существует

                Args:
                        kwargs: [dict] - словарь с параметрами для поиска

                Returns:
                        [Participant] - найденный event
                        [None] - если event не найден
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def edit(self, id, **kwargs):
        '''
        Редактирует [Participant]

                Args:
                        id: [int] - id event который нужно отредактировать
                        **kwargs: [dict] - словарь с параметрами для редактирования
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def list(self, **kwargs):
        '''
        Возвращает список [Participant]

                Args:
                        kwargs: [dict] - словарь с параметрами для поиска

                Returns:
                        [List[Participant]] - список найденных event
        '''
        raise NotImplementedError


class ParticipantRepository(AbstractParticipantRepository):

    def get(self, **kwargs) -> Union[models.Participant, None]:
        return models.Participant.objects.filter(**kwargs).first()

    def create(self, **kwargs):
        return models.Participant.objects.create(**kwargs)

    def edit(self, id, **kwargs):
        event = models.Participant.objects.get(id=id)
        for key, value in kwargs.items():
            setattr(event, key, value)
        event.save()
        return event

    def list(self, **kwargs, ) -> List[models.Participant]:
        return models.Participant.objects.filter(**kwargs)


class FakeParticipantRepository(AbstractParticipantRepository):

    def __init__(self) -> None:
        self._participants = []
        self._id = 0

    def get(self, **kwargs) -> Union[fake_models.Participant, None]:
        participants = self._participants
        if 'user__username' in kwargs:
            participants = [
                participant for participant in participants if participant.user.username == kwargs['user__username']]
            kwargs.pop('user__username')
        return next((participant for participant in participants if all([
            getattr(participant, key) == value for key, value in kwargs.items()
        ])), None)

    def create(self, **kwargs):
        participant = fake_models.Participant(**kwargs)
        self._id += 1
        participant.id = self._id
        self._participants.append(participant)
        return participant

    def edit(self, id, **kwargs):
        participant = next(
            (participant for participant in self._participants if participant.id == id), None)
        for key, value in kwargs.items():
            setattr(participant, key, value)
        self._participants = [participant if participant.id ==
                              id else participant for participant in self._participants]
        return participant

    def list(self, **kwargs, ) -> List[fake_models.Participant]:
        return [participant for participant in self._participants if all([
            getattr(participant, key) == value for key, value in kwargs.items()
        ])]
