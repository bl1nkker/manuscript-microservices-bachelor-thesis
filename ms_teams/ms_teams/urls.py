from django.contrib import admin
from django.urls import path
import app.views as views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('teams/', views.teams, name='teams'),
    path('teams/<int:team_id>', views.team, name='teams'),
    path('teams/<int:team_id>/kick/<int:member_id>', views.kick, name='kick'),
    path('teams/<int:team_id>/participants',
         views.team_participants, name='team_participants'),
    path('teams/<int:team_id>/participants/<int:participant_id>',
         views.team_participant, name='team_participant'),
]
