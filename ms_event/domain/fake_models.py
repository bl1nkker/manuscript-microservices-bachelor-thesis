class Event():
    # is_active = models.BooleanField(default=True)

    def __init__(self, name, image, location, location_url, description, full_description, start_date, end_date, author, tags, is_active=True):
        self.name = name
        self.image = image
        self.location = location
        self.location_url = location_url
        self.description = description
        self.full_description = full_description
        self.start_date = start_date
        self.end_date = end_date
        self.author = author
        self.tags = tags
        self.is_active = is_active

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'image': self.get_image_url(),
            'location': self.location,
            'location_url': self.location_url,
            'description': self.description,
            'full_description': self.full_description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'author': self.author.to_dict(),
            'tags': self.tags,
            'is_active': self.is_active,
        }

    def get_image_url(self):
        return self.image


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
