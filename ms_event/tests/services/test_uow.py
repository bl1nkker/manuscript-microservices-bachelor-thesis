import app.models as models
import service_layer.unit_of_work as uow
from django.test import TransactionTestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
import shutil

TEST_DIR = 'test_data'


@override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
class TestDjangoORMUnitOfWork(TransactionTestCase):
    reset_sequences = True

    def setUp(self) -> None:
        self.uow = uow.DjangoORMUnitOfWork()
        user = models.User.objects.create(username='test_user')
        self.user = models.ManuscriptUser.objects.create(user=user)
        return super().setUp()

    def tearDown(self) -> None:

        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            pass

    # Create
    def test_event_repository_create_should_create_event(self):
        with self.uow:
            image = SimpleUploadedFile(
                "test_image.jpg", b"file_content", content_type="image/jpeg")
            data = {
                "name": "test_event",
                "image": image,
                "location": 'Almaty',
                "location_url": 'https://www.google.com',
                "description": 'Test description',
                "full_description": 'Test full description',
                "start_date": '2020-01-01',
                "end_date": '2020-01-02',
                "author": self.user,
                "tags": ['test_tag1', 'test_tag2'],
            }
            event = self.uow.event.create(**data)
            self.assertEqual(1, models.Event.objects.count())
            self.assertEqual(event.id, 1)
            self.assertEqual(event.name, 'test_event')
            self.assertEqual(
                event.image.url, '/uploads/images/events/test_image.jpg')
            self.assertEqual(event.location, 'Almaty')
            self.assertEqual(event.location_url, 'https://www.google.com')
            self.assertEqual(event.description, 'Test description')
            self.assertEqual(event.full_description, 'Test full description')
            self.assertEqual(event.start_date, '2020-01-01')
            self.assertEqual(event.end_date, '2020-01-02')
            self.assertEqual(event.author, self.user)
            self.assertEqual(event.tags, ['test_tag1', 'test_tag2'])

    # Edit

    def test_event_repository_edit_should_edit_event(self):
        with self.uow:
            image = SimpleUploadedFile(
                "test_image.jpg", b"file_content", content_type="image/jpeg")
            data = {
                "name": "test_event",
                "image": image,
                "location": 'Almaty',
                "location_url": 'https://www.google.com',
                "description": 'Test description',
                "full_description": 'Test full description',
                "start_date": '2020-01-01',
                "end_date": '2020-01-02',
                "author": self.user,
                "tags": ['test_tag1', 'test_tag2'],
            }
            event = self.uow.event.create(**data)
            self.assertEqual(1, models.Event.objects.count())

            image = SimpleUploadedFile(
                "test_image2.jpg", b"file_content", content_type="image/jpeg")
            data = {
                "name": "test_event updated",
                "image": image,
                "location": 'Qostanay',
                "location_url": 'https://www.habr.com',
                "description": 'Test description updated',
                "full_description": 'Test full description updated',
                "start_date": '2021-01-01',
                "end_date": '2021-01-02',
                "author": self.user,
                "tags": ['test_tag1', 'test_tag2', 'test_tag3'],
            }
            updated_event = self.uow.event.edit(id=event.id, **data)
            self.assertEqual(1, models.Event.objects.count())
            self.assertEqual(updated_event.id, 1)
            self.assertEqual(updated_event.name, 'test_event updated')
            self.assertEqual(
                updated_event.image.url, '/uploads/images/events/test_image2.jpg')
            self.assertEqual(updated_event.location, 'Qostanay')
            self.assertEqual(updated_event.location_url,
                             'https://www.habr.com')
            self.assertEqual(updated_event.description,
                             'Test description updated')
            self.assertEqual(updated_event.full_description,
                             'Test full description updated')
            self.assertEqual(updated_event.start_date, '2021-01-01')
            self.assertEqual(updated_event.end_date, '2021-01-02')
            self.assertEqual(updated_event.author, self.user)
            self.assertEqual(updated_event.tags, [
                             'test_tag1', 'test_tag2', 'test_tag3'])
    # List

    def test_event_repository_list_should_list_active_events(self):
        with self.uow:
            for i in range(10):
                city = 'Qostanay'
                image = SimpleUploadedFile(
                    f"test_image{i}.jpg", b"file_content", content_type="image/jpeg")
                data = {
                    "name": f"test_event{i}",
                    "image": image,
                    "location": city,
                    "location_url": 'https://www.google.com',
                    "description": 'Test description',
                    "full_description": 'Test full description',
                    "is_active": False,
                    "start_date": '2020-01-01',
                    "end_date": '2020-01-02',
                    "author": self.user,
                    "tags": ['test_tag1', 'test_tag2'],
                }
                self.uow.event.create(**data)
            for i in range(3):
                image = SimpleUploadedFile(
                    f"test_image{i}.jpg", b"file_content", content_type="image/jpeg")
                data = {
                    "name": f"test_event{i}",
                    "image": image,
                    "location": 'Almaty',
                    "location_url": 'https://www.google.com',
                    "description": 'Test description',
                    "full_description": 'Test full description',
                    "start_date": '2020-01-01',
                    "end_date": '2020-01-02',
                    "author": self.user,
                    "tags": ['test_tag1', 'test_tag2'],
                }
                self.uow.event.create(**data)
            events = self.uow.event.list()
            self.assertEqual(3, len(events))

            for i in range(3):
                city = 'Qostanay'
                image = SimpleUploadedFile(
                    f"test_image{i}.jpg", b"file_content", content_type="image/jpeg")
                data = {
                    "name": f"test_event{i}",
                    "image": image,
                    "location": city,
                    "location_url": 'https://www.google.com',
                    "description": 'Test description',
                    "full_description": 'Test full description',
                    "is_active": True,
                    "start_date": '2020-01-01',
                    "end_date": '2020-01-02',
                    "author": self.user,
                    "tags": ['test_tag1', 'test_tag2'],
                }
                self.uow.event.create(**data)
            qos_events = self.uow.event.list(location='Qostanay')
            self.assertEqual(3, len(qos_events))

            for i in range(3):
                city = 'Qostanay'
                image = SimpleUploadedFile(
                    f"test_image{i}.jpg", b"file_content", content_type="image/jpeg")
                data = {
                    "name": f"test_event{i}",
                    "image": image,
                    "location": city,
                    "location_url": 'https://www.google.com',
                    "description": 'Test description',
                    "full_description": 'Test full description',
                    "is_active": True,
                    "start_date": '2020-01-01',
                    "end_date": '2020-01-02',
                    "author": self.user,
                    "tags": ['test_tag4', 'test_tag3'],
                }
                self.uow.event.create(**data)
            tag_events = self.uow.event.list(tags__contains='test_tag3')
            self.assertEqual(3, len(tag_events))
    # Get

    def test_event_repository_get_should_get_event(self):
        with self.uow:
            for i in range(3):
                city = 'Qostanay'
                image = SimpleUploadedFile(
                    f"test_image{i}.jpg", b"file_content", content_type="image/jpeg")
                data = {
                    "name": f"test_event{i}",
                    "image": image,
                    "location": city,
                    "location_url": 'https://www.google.com',
                    "description": 'Test description',
                    "full_description": 'Test full description',
                    "start_date": '2020-01-01',
                    "end_date": '2020-01-02',
                    "author": self.user,
                    "tags": ['test_tag1', 'test_tag2'],
                }
                self.uow.event.create(**data)
            event = self.uow.event.get(id=1)
            self.assertEqual(event.id, 1)
            self.assertEqual(event.name, 'test_event0')
            event = self.uow.event.get(id=2)
            self.assertEqual(event.id, 2)
            self.assertEqual(event.name, 'test_event1')

    # Delete
    def test_event_repository_deactivate_should_deactivate_event(self):
        with self.uow:
            image = SimpleUploadedFile(
                "test_image.jpg", b"file_content", content_type="image/jpeg")
            data = {
                "name": "test_event",
                "image": image,
                "location": 'Almaty',
                "location_url": 'https://www.google.com',
                "description": 'Test description',
                "full_description": 'Test full description',
                "start_date": '2020-01-01',
                "end_date": '2020-01-02',
                "author": self.user,
                "tags": ['test_tag1', 'test_tag2'],
            }
            event = self.uow.event.create(**data)
            self.assertEqual(1, models.Event.objects.count())
            self.assertEqual(event.is_active, True)

            self.uow.event.deactivate(id=event.id)
            self.assertEqual(1, models.Event.objects.count())
            self.assertEqual(models.Event.objects.first().is_active, False)
