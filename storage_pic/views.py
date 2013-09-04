from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.response import TemplateResponse
from storage_pic.models import Painting, Painting_liker
from django.contrib.auth.models import User
from django.utils import timezone
import time, random
from django.contrib.auth.decorators import login_required


def upload(request):
    if request.method == 'POST':
    	b = save_pic(request.FILES['picture'],request)
    return HttpResponseRedirect(reverse('accounts.views.userhome'))

def save_pic(pic_file,request,path=''):
	filename = str( time.time() )+ str(random.random()) + pic_file._get_name()
	import os 
	if 'SERVER_SOFTWARE' in os.environ:
		import sae.const
		access_key = sae.const.ACCESS_KEY
		secret_key = sae.const.SECRET_KEY
		appname = sae.const.APP_NAME
		domain_name = "picturestorage"

		import sae.storage
		s = sae.storage.Client()
		ob = sae.storage.Object(pic_file.read())
		url = s.put(domain_name,filename,ob)
		request.user.painting_set.create(key_name=filename,pic_url=url,like=0,create_date=timezone.now(),describe=request.POST['describe'])
		#a = '{"url":"'+url+'","title":"'+filename+'","state":"SUCCESS"}'
		return url
	else:
		fd = open('/Users/nosongyang/develop/%s' % (pic_file.name),'wb')
		for chunk in pic_file.chunks():
			fd.write(chunk)
		fd.close()
		a  ='{"url":"/media/'+filename+'","title":"'+filename +'","state":"SUCCESS"}'
		return a

@login_required()
def like(request,painting_id):
	painting = get_object_or_404(Painting, pk=painting_id)
	try:
		liker = painting.painting_liker_set.get(liker_id=request.user.id)
	except:
		painting.like +=1
		painting.save()
		painting.painting_liker_set.create(liker_id=request.user.id,liker_name=request.user.username)
	return HttpResponseRedirect(reverse('accounts.views.someone_painting', args=(painting.user.username,)))

def show(request):
	plist = Painting.objects.all().order_by('-create_date')[:12]
	last_painting_list = []
	for x in range(0,12,4):
		last_painting_list.append(plist[x:x+4])
	return render_to_response('show.html',{'last_painting_list':last_painting_list},context_instance=RequestContext(request))



