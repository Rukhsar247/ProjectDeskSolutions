from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponse, JsonResponse
from desksolutionsbase.forms import OrganizationForm, RegisterForm
from account.models import Organization, User
from .decorators import organization_absent
from django.core import serializers
import json

from DeskSolutions import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from account.models import User
import desksolutionsbase.models

def home(request):
    return render(request, "desksolutions/base.html")


def OrganizationRegister(request):
    context = {}
    if request.method == "POST" and request.is_ajax():
        print("request is POST")
        form = OrganizationForm(request.POST or None)
        # print(form)
        if form.is_valid():
            print("Organization Form is Valid")

            # org = form.save()
            # print(org)
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            url = form.cleaned_data['url']
            create_organization = Organization.objects.create(
                title=title, description=description, url=url)
            create_organization.save()
            # get_org = Organization.objects.filter(
            #     title=title)
            # print(get_org)

            # for g in get_org:
            #     print(g)
            # print(get_org)
            # ser_instance = serializers.serialize(
            # 'json', get_org)
            # print(ser_instance)
            # ser_instance = json.dumps(get_org, content_type='application/json')
            # print(ser_instance)
            request.session['organization'] = create_organization.id
            # print(ser_instance)
            print(request.session['organization'])
            # form.save()
            # return redirect("signup:signups", args=(request.session['organization'],))
            # return redirect('signups')
            # context['json'] = ser_instance
            # return JsonResponse(context)
        else:
            print("Organization Form is inValid")
            # context['register_form'] = form
            context['register_form'] = form.errors
            return JsonResponse(context)
    else:
        form = OrganizationForm()
        context['register_form'] = form

    return render(request, "desksolutionsbase/base.html", context)

@organization_absent
def signup(request):
    session_name = request.session.get('organization')
    print(session_name)
    if session_name is not None:
        get_organization = Organization.objects.get(id=session_name)
        print(get_organization)
        # get_org = get_object_or_404(Organization, title=url)
        print("in signup function")
        context = {}
        if request.method == "POST":
            user_form = RegisterForm(request.POST or None)
            if user_form.is_valid():
                print("form valid")
                user = user_form.save(commit=False)
                # email = user_form.cleaned_data.get('email')
                # first_name = user_form.cleaned_data.get('first_name')
                # last_name = user_form.cleaned_data.get('last_name')
                # phone = user_form.cleaned_data.get('phone')
                # address = user_form.cleaned_data.get('address')

                # user = User.objects.create_user(
                #     email=email)
                # profile = profile_form.save(commit=False)
                # org = request.session.get('organization')
                # for obj in serializers.deserialize("json", org):
                #     print(obj)
                # print(org)
                # print(user)
                # convert_to_obj = json.loads(org)
                # print(convert_to_obj)
                # print(org.id)
                user.organization = get_organization
                user.save()
                group, created = Group.objects.get_or_create(
                    name=settings.GROUP_ALLOCATE)
                print("I am in entering in group Entering code")
                ct = ContentType.objects.get_for_model(Organization)
                if created:
                    print("I am in IF Condition!!!")
                    permission = Permission.objects.filter(content_type=ct)

                    for perm in permission:
                        group.permissions.add(perm)
                    group.save()
                    user.groups.add(group)
                else:
                    print("I am in else condition!!!")

                    permission = Permission.objects.filter(content_type=ct)

                    print("Permission is ", permission)

                    for perm in permission:
                        group.permissions.add(perm)
                    group.save()

                    print("group is ", group)

                    user.groups.add(group)

                #    user.groups.add(group)
                # profile.organization = user
                # profile.save()
                del request.session['organization']
                # print(request.session['organization'])
            else:
                print("invalid form")
                context['user_form'] = user_form
        else:
            user_form = RegisterForm()
            context['user_form'] = user_form

        return render(request, 'desksolutionsbase/register.html', context)


#  Signals

class AddGroup(models.Model):
    user = models.ForeignKey(User, null=True, blank=True,
    on_delete=models.CASCADE)

    def __str__(self):
        return self.user

@receiver(post_save, sender=User)
def save_post(sender, instance, created, **kwargs):

   AddGroup.objects.create(user=instance)
   print("Successfully Add In The Group ")
post_save.connect(save_post, sender=User)
