from django.db import models
import os 
# Create your models here.


class UserModel(models.Model):
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    otp = models.IntegerField(null=True)
   


    def __str__(self):
        return self.username
    
    class Meta:
        db_table = "UserModel"  # Optional, but can be used to specify the table name

class UserProfile(models.Model):
    user_id = models.IntegerField(null=True)
    phone = models.IntegerField()
    address = models.CharField(max_length=255)
    image = models.FileField(upload_to=os.path.join('static/assets/' 'UserProfiles'))
    bio = models.TextField()
    def __str__(self):
        return self.user.username
    class Meta:
        db_table = "UserProfile"  # Optional, but can be used to specify the table name
    




from django.db import models
from tinyec import registry
from .models import UserModel

curve = registry.get_curve('brainpoolP256r1')


class EncryptedImage(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    encrypted_data = models.BinaryField()
    encrypted_key = models.BinaryField()
    iv = models.BinaryField()
    c1 = models.TextField()  # Serialized ECC point
    width = models.IntegerField()
    height = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def image_size(self):
        return (self.width, self.height)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "EncryptedImageModel"  # Optional, but can be used to specify



class RequestFileModel(models.Model):
    file_id = models.ForeignKey(EncryptedImage, on_delete=models.CASCADE)
    requester =  models.EmailField()
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, default='Pending')
    otp = models.IntegerField(null=True)

    def __str__(self):
        return self.requester
    class Meta:
        db_table = "RequestFileModel"  # Optional, but can be used to specify the