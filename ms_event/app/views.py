import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import app.models as models
# Create your views here.


def create_event(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        body['author'] = models.ManuscriptUser.objects.get(id=body['author'])
        event = models.Event.objects.create(**body)
        # Send redis message
        return JsonResponse(data={'id': event.id}, status=201)
    return HttpResponse(status=403)
