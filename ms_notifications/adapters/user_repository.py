import abc
from typing import Union, List

import app.models as models
import domain.fake_models as fake_models
import django.contrib.auth as django_auth


class AbstractUserRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, **kwargs):
        ''' 
        Возвращает [User], если user с таким username существует

                Args:
                        kwargs: [dict] - словарь с параметрами для поиска

                Returns:
                        [User] - студент, которому принадлежит пользователь
                        [None] - если студент не найден
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def create(self, **kwargs):
        '''
        Создает [User] и возвращает его

                Args:
                        id: [int] - id пользователя
                        username: [str] - username пользователя
                        password: [str] - password пользователя (по умолчанию 'dsadsadas')

                Returns:
                        [Student] - созданный студент
        '''


class ManuscriptUserRepository(AbstractUserRepository):

    def get(self, **kwargs) -> Union[models.ManuscriptUser, None]:
        if 'id' in kwargs:
            return models.ManuscriptUser.objects.filter(**kwargs).first()
        user = models.User.objects.filter(**kwargs).first()
        return models.ManuscriptUser.objects.filter(user=user).first()

    def create(self, **kwargs):
        user = models.User.objects.create(**kwargs)
        return models.ManuscriptUser.objects.create(user=user)


class FakeManuscriptUserRepository(AbstractUserRepository):

    def __init__(self):
        self._id = 1
        self._users = []

    def get(self, **kwargs) -> Union[fake_models.ManuscriptUser, None]:
        return next((user for user in self._users if all([
            getattr(user, key) == value for key, value in kwargs.items()
        ])), None)

    def create(self, **kwargs) -> fake_models.ManuscriptUser:
        user = fake_models.ManuscriptUser(
            id=self._id,
            **kwargs
        )
        self._users.append(user)
        self._id += 1
        return user
