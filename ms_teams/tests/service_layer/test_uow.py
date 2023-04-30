import shutil
from django.test import TransactionTestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile

import service_layer.unit_of_work as uow
import app.models as models
import core.constants as constants

TEST_DIR = 'test_data'


def create_user(username='test_user', password='test_password'):
    user = models.User.objects.create(username=username)
    return models.ManuscriptUser.objects.create(user=user)


def create_event(name='test_event'):
    return models.Event.objects.create(name=name)


@override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
class TestDjangoORMUnitOfWorkTeam(TransactionTestCase):
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
                event=self.event,
            )
            self.assertEqual(models.Team.objects.count(), 1)
            self.assertEqual(team.name, 'test_team')
            self.assertEqual(team.event, self.event)
            self.assertEqual(team.is_active, True)

    def test_team_repository_edit_should_edit_team(self):
        with self.uow:
            image = SimpleUploadedFile(
                "test_image.jpg", b"file_content", content_type="image/jpeg")
            team = self.uow.team.create(
                name='test_team',
                image=image,
                event=self.event,
            )
            updated_team = self.uow.team.edit(
                id=team.id,
                name='updated_test_team',
            )
            self.assertEqual(models.Team.objects.count(), 1)
            self.assertEqual(updated_team.name, 'updated_test_team')

    def test_team_repository_deactivate_should_deactivate_team(self):
        with self.uow:
            image = SimpleUploadedFile(
                "test_image.jpg", b"file_content", content_type="image/jpeg")
            team = self.uow.team.create(
                name='test_team',
                image=image,
                event=self.event,
            )
            deactivated_team = self.uow.team.deactivate(id=team.id)
            self.assertEqual(models.Team.objects.count(), 1)
            self.assertEqual(deactivated_team.is_active, False)

    def test_team_repository_list_should_list_all_active_teams(self):
        with self.uow:
            for _ in range(3):
                self.uow.team.create(
                    name='test_team', event=self.event,)
            for _ in range(7):
                self.uow.team.create(
                    name='test_team', event=self.event, is_active=False)
            result = self.uow.team.list()
            self.assertEqual(len(result), 3)

    def test_team_repository_list_should_filter_teams_when_props_passed(self):
        with self.uow:
            for _ in range(3):
                self.uow.team.create(
                    name='test_team', event=self.event,)
            another_event = create_event(name='another_event')
            for _ in range(7):
                self.uow.team.create(
                    name='test_team', event=another_event, is_active=False)
            result = self.uow.team.list(event=self.event)
            self.assertEqual(len(result), 3)

    def test_team_repository_get_should_get_team(self):
        with self.uow:
            team = self.uow.team.create(
                name='test_team', event=self.event, is_active=True)
            team = self.uow.team.get(id=team.id)
            self.assertEqual(team.name, 'test_team')

    def test_participant_repository_should_create_team_participant(self):
        with self.uow:
            image = SimpleUploadedFile(
                "test_image.jpg", b"file_content", content_type="image/jpeg")
            team = self.uow.team.create(
                name='test_team',
                image=image,
                event=self.event,
            )
            participant = self.uow.participant.create(
                user=self.user,
                team=team,
            )
            self.assertEqual(models.Participant.objects.count(), 1)
            self.assertEqual(participant.user, self.user)
            self.assertEqual(participant.team, team)
            self.assertEqual(participant.role, constants.MEMBER_ROLE)
            self.assertEqual(participant.status,
                             constants.PENDING_STATUS)

            participant = self.uow.participant.create(
                user=self.user,
                team=team,
                role=constants.LEADER_ROLE,
                status=constants.APPLIED_STATUS,
            )
            self.assertEqual(models.Participant.objects.count(), 2)
            self.assertEqual(participant.user, self.user)
            self.assertEqual(participant.team, team)
            self.assertEqual(participant.role, constants.LEADER_ROLE)
            self.assertEqual(participant.status,
                             constants.APPLIED_STATUS)

    def test_participant_repository_should_edit_team_participant(self):
        with self.uow:
            image = SimpleUploadedFile(
                "test_image.jpg", b"file_content", content_type="image/jpeg")
            team = self.uow.team.create(
                name='test_team',
                image=image,
                event=self.event,
            )
            participant = self.uow.participant.create(
                user=self.user,
                team=team,
            )
            participant = self.uow.participant.edit(
                id=participant.id,
                status=constants.KICKED_STATUS,
            )
            self.assertEqual(participant.status,
                             constants.KICKED_STATUS)

    def test_participant_repository_should_list_team_participants(self):
        with self.uow:
            image = SimpleUploadedFile(
                "test_image.jpg", b"file_content", content_type="image/jpeg")
            team = self.uow.team.create(
                name='test_team',
                image=image,
                event=self.event,
            )
            for _ in range(3):
                self.uow.participant.create(
                    user=self.user,
                    team=team,
                    status=constants.APPLIED_STATUS
                )
                self.uow.participant.create(
                    user=self.user,
                    team=team,
                    status=constants.KICKED_STATUS,
                )
            another_team = self.uow.team.create(
                name='another_test_team',
                image=image,
                event=self.event,
            )
            for _ in range(7):
                self.uow.participant.create(
                    user=self.user,
                    team=another_team,
                    status=constants.KICKED_STATUS,
                )
            result = self.uow.participant.list(team=team)
            self.assertEqual(len(result), 6)
            result = self.uow.participant.list(
                team=team, status=constants.APPLIED_STATUS)
            self.assertEqual(len(result), 3)

    def test_participant_repository_should_get_team_participant(self):
        with self.uow:
            image = SimpleUploadedFile(
                "test_image.jpg", b"file_content", content_type="image/jpeg")
            team = self.uow.team.create(
                name='test_team',
                image=image,
                event=self.event,
            )
            participant = self.uow.participant.create(
                user=self.user,
                team=team,
            )
            participant = self.uow.participant.get(id=participant.id)
            self.assertEqual(participant.user, self.user)
            self.assertEqual(participant.team, team)
            self.assertEqual(participant.role, constants.MEMBER_ROLE)
            self.assertEqual(participant.status,
                             constants.PENDING_STATUS)
