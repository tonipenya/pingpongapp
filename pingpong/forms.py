# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _, ugettext as __
from ragendja.auth.models import UserTraits
from ragendja.forms import FormWithSets, FormSetField
from registration.forms import RegistrationForm, RegistrationFormUniqueEmail
from registration.models import RegistrationProfile
from pingpong.models import Player

from django import forms

class ContactForm(forms.Form):
  feedback = forms.CharField(widget=forms.Textarea(attrs={'name': 'feedback', 'class': 'contact_feedback fields required'}))
  name = forms.CharField(widget=forms.TextInput(attrs={'name': 'name', 'class': 'pads fields required'}))
  email = forms.EmailField(widget=forms.TextInput(attrs={'email': 'email', 'class': 'pads med fields required email'}))

def make_player_form(request):
  class PlayerForm(forms.ModelForm):
    name = forms.CharField(required=True, label='Name')

    class Meta:
      model = Player
      fields = ('name',)

    def save(self, commit=True):
      f = super(PlayerForm, self).save(commit=False)
      if not f.pk: f.owner = request.user
      if commit: f.save()
      return f

  return PlayerForm

class UserRegistrationForm(forms.ModelForm):
    username = forms.RegexField(regex=r'^\w+$', max_length=30,
        widget=forms.TextInput(attrs={'class': 'core_left pads med fields'}))
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'maxlength': '75', 'class': 'core_left pads med fields required email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False,
        attrs={'class': 'core_left pads fields required'}))
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False,
        attrs={'class': 'core_left pads fields required'}))

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        """
        user = User.get_by_key_name("key_"+self.cleaned_data['username'].lower())
        if user:
            raise forms.ValidationError(__(u'This username is already taken. Please choose another.'))
        return self.cleaned_data['username']

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(__(u'The passwords you entered do not match'))
        return self.cleaned_data
    
    def save(self, domain_override=""):
        """
        Create the new ``User`` and ``RegistrationProfile``, and
        returns the ``User``.
        
        This is essentially a light wrapper around
        ``RegistrationProfile.objects.create_inactive_user()``,
        feeding it the form data and a profile callback (see the
        documentation on ``create_inactive_user()`` for details) if
        supplied.
        
        """
        new_user = RegistrationProfile.objects.create_inactive_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            email=self.cleaned_data['email'],
            domain_override=domain_override)
        self.instance = new_user
        return super(UserRegistrationForm, self).save()

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        
        """
        email = self.cleaned_data['email'].lower()
        if User.all().filter('email =', email).filter(
                'is_active =', True).count(1):
            raise forms.ValidationError(__(u'This email address is already in use. Please supply a different email address.'))
        return email

    class Meta:
        model = User
        exclude = UserTraits.properties().keys()
