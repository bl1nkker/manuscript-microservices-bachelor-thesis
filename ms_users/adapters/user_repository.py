import abc
from typing import Union, List

import app.models as models
import domain.fake_models as fake_models
import django.contrib.auth as django_auth


class AbstractUserRepository(abc.ABC):
    ''' 
    Репозиторий, отвечающий за управление [User].
    '''
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
    def authenticate(self, request, username, password):
        '''
        Аутентифицирует пользователя

                Args:
                        request: [HttpRequest] - запрос
                        username: [str] - username пользователя
                        password: [str] - password пользователя

                Returns:
                        [User] - аутентифицированный пользователь
                        [None] - если пользователь не найден
        '''


class ManuscriptUserRepository(AbstractUserRepository):

    def get(self, **kwargs) -> Union[models.ManuscriptUser, None]:
        if 'id' in kwargs:
            return models.ManuscriptUser.objects.filter(**kwargs).first()
        user = models.User.objects.filter(**kwargs).first()
        return models.ManuscriptUser.objects.filter(user=user).first()

    def create(self, **kwargs):
        user = models.User.objects.create(**kwargs)
        if 'password' in kwargs:
            user.set_password(kwargs['password'])
            user.save()
        return models.ManuscriptUser.objects.create(user=user)

    def authenticate(self, request, username, password):
        return django_auth.authenticate(request=request, username=username, password=password)


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

    def authenticate(self, request, username, password):
        return next((user for user in self._users if all([
            user.username == username,
            user.password == password
        ])), None)
