import abc
from typing import Union, List
import app.models as models
import domain.fake_models as fake_models


class AbstractNotificationRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, **kwargs):
        ''' 
        Возвращает [Notification], если user с таким username существует

                Args:
                        kwargs: [dict] - словарь с параметрами для поиска

                Returns:
                        [Notification] - студент, которому принадлежит пользователь
                        [None] - если студент не найден
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def list(self, **kwargs):
        ''' 
        Возвращает [Notification], если user с таким username существует

                Args:
                        kwargs: [dict] - словарь с параметрами для поиска

                Returns:
                        [Notification] - студент, которому принадлежит пользователь
                        [None] - если студент не найден
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def create(self, **kwargs):
        '''
        Создает [Notification] и возвращает его

                Args:
                        **kwargs: Параметры для создания [Notification]
                Returns:
                        [Notification] - созданный студент
        '''
        raise NotImplementedError


class NotificationRepository(AbstractNotificationRepository):

    def get(self, **kwargs) -> Union[models.Notification, None]:
        return models.Notification.objects.filter(**kwargs).first()

    def list(self, **kwargs):
        return models.Notification.objects.filter(**kwargs)

    def create(self, **kwargs) -> models.Notification:
        return models.Notification.objects.create(**kwargs)


class FakeNotificationRepository(AbstractNotificationRepository):

    def __init__(self):
        self._id = 1
        self._notifications = []

    def get(self, **kwargs) -> Union[fake_models.Notification, None]:
        return next((notification for notification in self._notifications if all([
            getattr(notification, key) == value for key, value in kwargs.items()
        ])), None)

    def list(self, include_deactivated=False, **kwargs, ) -> List[fake_models.Notification]:
        return [team for team in self._notifications if all(getattr(team, key) == value for key, value in kwargs.items())]

    def create(self, **kwargs) -> fake_models.Notification:
        notification = fake_models.Notification(
            id=self._id,
            **kwargs
        )
        self._notifications.append(notification)
        self._id += 1
        return notification
