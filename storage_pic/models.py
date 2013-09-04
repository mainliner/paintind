from django.db import models
from django.contrib.auth.models import User


class Painting(models.Model):
	user = models.ForeignKey(User)
	key_name = models.CharField(max_length=200)
	pic_url = models.CharField(max_length=500)
	describe = models.CharField(max_length=500)
	like = models.IntegerField()
	create_date = models.DateTimeField('date published')
	def __unicode__(self):
		return self.key_name

class Painting_liker(models.Model):
	panting = models.ForeignKey(Painting)
	liker_id = models.IntegerField()
	liker_name = models.CharField(max_length=30)