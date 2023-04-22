from services import Result
import services.unit_of_work as uow
import core.exceptions as exceptions


def sign_in_user_service(uow: uow.AbstractUnitOfWork, request, username: str, password: str) -> Result:
    if uow.user.authenticate(request=request, username=username, password=password) is None:
        return Result(data=None, error=exceptions.AuthenticationException)
    m_user = uow.user.get(username=username)
    return Result(data={"access_token": m_user.generate_jwt_token()})


def sign_up_user_service(uow: uow.AbstractUnitOfWork, request, username: str, first_name: str, last_name: str, password: str, confirm_password: str) -> Result:
    if password != confirm_password:
        return Result(data=None, error=exceptions.InvalidUserDataException)
    if not username or not first_name or not last_name:
        return Result(data=None, error=exceptions.InvalidUserDataException)
    user = uow.user.create(
        username=username, first_name=first_name, last_name=last_name, password=password, email=username)
    return Result(data={"access_token": user.generate_jwt_token()})


def get_user_service(uow: uow.AbstractUnitOfWork, id: int = None) -> Result:
    user = uow.user.get(id=id)
    if user is None:
        return Result(data=None, error=exceptions.UserNotFoundException)
    return Result(data=user.to_dict(), error=None)


def get_me_service(uow: uow.AbstractUnitOfWork, user) -> Result:
    m_user = uow.user.get(username=user.username)
    return Result(data=m_user.to_dict(), error=None)
