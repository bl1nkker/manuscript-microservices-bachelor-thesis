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


class Team:
    def __init__(self, name, leader, event, is_active=True, members=[], id=None):
        self.id = id
        self.name = name
        self.leader = leader
        self.event = event
        self.members = members
        self.is_active = is_active
