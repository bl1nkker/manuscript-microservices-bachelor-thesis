import abc
from typing import Union, List

import app.models as models
import domain.fake_models as fake_models
import django.contrib.auth as django_auth


class AbstractEventRepository(abc.ABC):
    ''' 
    Репозиторий, отвечающий за управление [Event].
    '''
    @abc.abstractmethod
    def create(self, **kwargs):
        '''
        Создает [Event] и возвращает его

                Args:
                        **kwargs: Параметры для создания [Event]
                Returns:
                        [Student] - созданный студент
        '''

    @abc.abstractmethod
    def get(self, **kwargs):
        ''' 
        Возвращает [Event], если event существует

                Args:
                        kwargs: [dict] - словарь с параметрами для поиска

                Returns:
                        [Event] - найденный event
                        [None] - если event не найден
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def edit(self, id, **kwargs):
        ''' 
        Редактирует [Event]

                Args:
                        id: [int] - id event который нужно отредактировать
                        **kwargs: [dict] - словарь с параметрами для редактирования
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def list(self, **kwargs):
        ''' 
        Возвращает список [Event]

                Args:
                        kwargs: [dict] - словарь с параметрами для поиска

                Returns:
                        [List[Event]] - список найденных event
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def deactivate(self, id):
        ''' 
        Удаляет [Event]

                Args:
                        id: [int] - id event который нужно удалить
        '''
        raise NotImplementedError


class EventRepository(AbstractEventRepository):

    def get(self, **kwargs) -> Union[models.Event, None]:
        return models.Event.objects.filter(**kwargs).first()

    def create(self, **kwargs):
        return models.Event.objects.create(**kwargs)

    def edit(self, id, **kwargs):
        event = models.Event.objects.get(id=id)
        for key, value in kwargs.items():
            setattr(event, key, value)
        event.save()
        return event

    def list(self, include_deactivated=False, **kwargs, ) -> List[models.Event]:
        if include_deactivated:
            return models.Event.objects.filter(**kwargs)
        return models.Event.objects.filter(**kwargs, is_active=True)

    def deactivate(self, id):
        event = models.Event.objects.get(id=id)
        event.is_active = False
        event.save()
