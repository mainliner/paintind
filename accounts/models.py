from django.db import models
from django.contrib.auth.models import User

class User_info(models.Model):
	user = models.ForeignKey(User)
	photo = models.CharField(max_length=500)
	fans_num = models.IntegerField()
	follower_num = models.IntegerField()
	describe = models.CharField(max_length=500)
	def __unicode__(self):
		return self.user
class Fans(models.Model):
	user = models.ForeignKey(User)
	fans = models.CharField(max_length=200)

class Follower(models.Model):
	user = models.ForeignKey(User)
	follower = models.CharField(max_length=200)