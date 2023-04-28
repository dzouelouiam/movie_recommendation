from django.forms import ModelForm
from .models import Room

class RoomForm(ModelForm):
    class Meta:
        model = Room
        #include all the fields ( name, topic, description , body ...) in class Room ( models.py)
        fields = '__all__' 