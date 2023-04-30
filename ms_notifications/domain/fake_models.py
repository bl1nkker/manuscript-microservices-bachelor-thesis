class Notification:
    def __init__(self, id, user, message, status, ):
        self.id = id
        self.user = user
        self.message = message
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            "user": self.user.to_dict(),
            "message": self.message,
            "status": self.status,
        }


class ManuscriptUser:
    def __init__(self, username: str, password: str, id: int, first_name: str = '', last_name: str = '', email=None):
        self.id = id
        self.username = username
        self.email = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name
        }
