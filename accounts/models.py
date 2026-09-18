from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")
    bio = models.TextField(max_length=300, blank=True, default="")
    avatar = models.ImageField(upload_to="avatars/",blank=True,null=True)
    birthdate = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip()
    
    @property
    def age(self):
        if not self.birthdate:
            return None
        
        today = date.today()
        years = today.year - self.birthdate.year
        
        if (today.month, today.year) < (self.birthdate.month, self.birthdate.year):
            years = years - 1

        return years
