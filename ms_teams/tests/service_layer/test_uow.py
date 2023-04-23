import shutil
from django.test import TransactionTestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile

import service_layer.unit_of_work as uow
import app.models as models


TEST_DIR = 'test_data'


def create_user(username='test_user', password='test_password'):
    user = models.User.objects.create(username=username)
    return models.ManuscriptUser.objects.create(user=user)


def create_event(name='test_event'):
    return models.Event.objects.create(name=name)


@override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
class TestDjangoORMUnitOfWork(TransactionTestCase):
    def setUp(self) -> None:
        self.uow = uow.DjangoORMUnitOfWork()
        self.user = create_user()
        self.event = create_event()
        return super().setUp()

    def tearDown(self) -> None:
        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            pass

    def test_team_repository_create_should_create_team(self):
        with self.uow:
            image = SimpleUploadedFile(
                "test_image.jpg", b"file_content", content_type="image/jpeg")
            team = self.uow.team.create(
                name='test_team',
                image=image,
                leader=self.user,
                event=self.event,
            )
            self.assertEqual(models.Team.objects.count(), 1)
            self.assertEqual(team.name, 'test_team')
            self.assertEqual(team.leader, self.user)
            self.assertEqual(team.event, self.event)
            self.assertEqual(team.is_active, True)
            self.assertEqual(team.members.count(), 0)

    def test_team_repository_edit_should_edit_team(self):
        with self.uow:
            image = SimpleUploadedFile(
                "test_image.jpg", b"file_content", content_type="image/jpeg")
            team = self.uow.team.create(
                name='test_team',
                image=image,
                leader=self.user,
                event=self.event,
            )
            updated_team = self.uow.team.edit(
                id=team.id,
                name='updated_test_team',
            )
            self.assertEqual(models.Team.objects.count(), 1)
            self.assertEqual(updated_team.name, 'updated_test_team')

            another_leader = create_user(username='another_leader')
            updated_team = self.uow.team.edit(
                id=team.id,
                leader=another_leader
            )
            self.assertEqual(models.Team.objects.count(), 1)
            self.assertEqual(updated_team.leader, another_leader)
            new_member = create_user(username='new_member')
            updated_team = self.uow.team.edit(
                id=team.id,
                members=[new_member]
            )
            self.assertEqual(models.Team.objects.count(), 1)
            self.assertEqual(updated_team.members.count(), 1)
            self.assertEqual(updated_team.members.first(), new_member)

            updated_team = self.uow.team.edit(
                id=team.id,
                members=[]
            )
            self.assertEqual(models.Team.objects.count(), 1)
            self.assertEqual(updated_team.members.count(), 0)

    def test_team_repository_deactivate_should_deactivate_team(self):
        with self.uow:
            image = SimpleUploadedFile(
                "test_image.jpg", b"file_content", content_type="image/jpeg")
            team = self.uow.team.create(
                name='test_team',
                image=image,
                leader=self.user,
                event=self.event,
            )
            deactivated_team = self.uow.team.deactivate(id=team.id)
            self.assertEqual(models.Team.objects.count(), 1)
            self.assertEqual(deactivated_team.is_active, False)

    def test_team_repository_list_should_list_all_active_teams(self):

        with self.uow:
            for _ in range(3):
                self.uow.team.create(
                    name='test_team', leader=self.user, event=self.event,)
            for _ in range(7):
                self.uow.team.create(
                    name='test_team', leader=self.user, event=self.event, is_active=False)
            result = self.uow.team.list()
            self.assertEqual(len(result), 3)

    def test_team_repository_list_should_filter_teams_when_props_passed(self):
        with self.uow:
            for _ in range(3):
                self.uow.team.create(
                    name='test_team', leader=self.user, event=self.event,)
            another_event = create_event(name='another_event')
            for _ in range(7):
                self.uow.team.create(
                    name='test_team', leader=self.user, event=another_event, is_active=False)
            result = self.uow.team.list(event=self.event)
            self.assertEqual(len(result), 3)

    def test_team_repository_get_should_get_team(self):
        with self.uow:
            team = self.uow.team.create(
                name='test_team', leader=self.user, event=self.event, is_active=True)
            team = self.uow.team.get(id=team.id)
            self.assertEqual(team.name, 'test_team')
