class Event():
    # is_active = models.BooleanField(default=True)

    def __init__(self, name, is_active=True):
        self.name = name
        self.is_active = is_active

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'is_active': self.is_active,
        }


class ManuscriptUser:
    def __init__(self, username: str,  id: int, first_name: str = '', last_name: str = '', email=None, password: str = '123'):
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


class Team:
    def __init__(self, name, event, is_active=True,  id=None, image='',):
        self.id = id
        self.name = name
        self.image = image
        self.event = event
        self.is_active = is_active

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'image': self.image,
            'event': self.event,
            'is_active': self.is_active,
        }

    def get_members(self):
        return self.members


class Participant:
    def __init__(self, user, team, role, status, id=None):
        self.id = id
        self.user = user
        self.team = team
        self.role = role
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.to_dict(),
            'team': self.team.to_dict(),
            'role': self.role,
            'status': self.status,
        }
