from django.shortcuts import render

# Create your views here.
from django.views import View
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout,get_user_model
from django.http import HttpResponseRedirect
from .models import UserActivity
from .forms import LoginForm, UserActivityForm

class ActivityView(View):
	def get(self,request, *args, ** kwargs):
		if not request.user.is_authenticated():
			return HttpResponseRedirect("/login/")

		if request.session.get("username"):
			username_auth = request.user.username
			username_ses = request.session.get("username")

		if username_ses == username_auth:
			username = username_auth
			context={}
			form = UserActivityForm(initial={"username":username})
			context["form"]=form
			if request.user.is_authenticated():
				obj = UserActivity.objects.current(request.user)
				context["object"]=obj
		else:
			logout(request)
			return HttpResponseRedirect("/login/")
		return render(request,"timeclock/activity-view.html",context)

	def post(self,request,*args,**kwargs):
		form = UserActivityForm(request.POST)
		obj = UserActivity.objects.current(request.user)
		context={
		"form":form,
		"object":obj
		}
		if form.is_valid():
			toggle = UserActivity.objects.toggle(request.user)
			return HttpResponseRedirect("/")
			context['object']=toggle
		return render(request,"timeclock/activity-view.html",context)



class UserLoginView(View):
	def get(self,request, *args, ** kwargs):
		
		form = LoginForm()
		context={
		"form":form
		}

		return render(request,"timeclock/login-view.html",context)

	def post(self,request,*args,**kwargs):
			
		form = LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data.get("username")
			password = form.cleaned_data.get("password")
			user = authenticate(username=username,password=password)
			if user is not None:
				login(request,user)
				request.session['username'] = username
				return HttpResponseRedirect("/")
			else:
				return HttpResponseRedirect("/")

		context={
		"form":form
		}

		return render(request,"timeclock/login-view.html",context)


User = get_user_model()

class UserActivityView(View):
	def get(self,request,*args,**kwargs):
		users = User.objects.all()
		
		checked_in_list=[]
		checked_out_list=[]
		no_activity_unknown_users=[]
		for u in users:
			act = u.useractivity_set.all().today().recent()
			if act.exists():
				current_user_activity_object = act.first()
				if current_user_activity_object == 'checkin':
					checked_in_list.append(current_user_activity_object.id)
				else:
					checked_out_list.append(current_user_activity_object.id)
			else:
				no_activity_unknown_users.append(u)


		checked_in_users = UserActivity.objects.filter(id__in=checked_in_list)
		checked_out_users = UserActivity.objects.filter(id__in=checked_out_list)
		context={
		"checked_in_users":checked_in_users,
		"checked_out_users":checked_out_users,
		"inactive_users":no_activity_unknown_users

		}
		return render(request,"timeclock/users-activity-view.html",context)




class UserLogoutView(View):
	def get(self,request,*args,**kwargs):
		logout(request)
		return HttpResponseRedirect("/")


def activity_view(request,*args,**kwargs):
	if request.method=='POST':
		new_act=UserActivity.objects.create(user=request.user,activity='checkin')
	return render(request,"timeclock/activity-view.html",{})