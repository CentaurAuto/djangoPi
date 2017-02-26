from django import forms
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone
from .models import UserActivity
from django.conf import settings

ACTIVITY_TIME_DELTA = getattr(settings,"ACTIVITY_TIME_DELTA",timedelta(minutes=1))

User = get_user_model()

class LoginForm(forms.Form):
	username = forms.CharField()
	password = forms.CharField(widget=forms.PasswordInput)

	def clean(self,*args,**kwargs):
		cleaned_data=super(LoginForm,self).clean(*args,**kwargs)
		username = cleaned_data['username']
		qs = User.objects.filter(username__iexact=username)
		password = cleaned_data['password']

		if not qs.exists() or qs.count() !=1:
			raise forms.ValidationError("This username/passowrd is incorrect")
		else:
			user_obj = qs.first()
			if not user_obj.check_password(password):
				raise forms.ValidationError("This username/passowrd is incorrect")
		return cleaned_data


class UserActivityForm(forms.Form):
	username = forms.CharField(widget=forms.HiddenInput)
	password = forms.CharField(label="verify password",widget=forms.PasswordInput)

	def clean(self,*args,**kwargs):
		cleaned_data=super(UserActivityForm,self).clean(*args,**kwargs)
		username = cleaned_data['username']
		qs = User.objects.filter(username__iexact=username)
		password = cleaned_data['password']

		if not qs.exists() or qs.count() !=1:
			raise forms.ValidationError("This passowrd is incorrect")
		else:
			user_obj = qs.first()
			current = UserActivity.objects.current(user_obj)
			if current:
				actual_obj_time = current.timestamp
				the_delta = ACTIVITY_TIME_DELTA
				diff = the_delta + actual_obj_time
				now = timezone.now()
				if diff > now:
					raise forms.ValidationError("You must wait {time} before this action".format(time=the_delta))
			if not user_obj.check_password(password):
				raise forms.ValidationError("This passowrd is incorrect")
		return cleaned_data

'''
	def clean_username(self,*args,**kwargs):
		username = self.cleaned_data['username']
		qs = User.objects.filter(username__iexact=username)
		if not qs.exists or qs.count() > 1:
			raise forms.ValidationError("This username/passowrd is incorrect")

		return username


	def clean_password(self,*args,**kwargs):
		username = self.cleaned_data['username']
		qs = User.objects.filter(username__iexact=username)
		password = self.cleaned_data['password']
		if qs.exists or qs.count() == 1:
			user_obj = qs.first()
			if not user_obj.check_password(password):
				raise forms.ValidationError("This username/passowrd is incorrect")
			return password
		else:
			raise forms.ValidationError("This username/passowrd is incorrect")
'''