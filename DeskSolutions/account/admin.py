from django.contrib import admin
from .models import Organization, User, Department, Profile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserModelForm, CustomDepartmentForm, ProfileFormSet
from django.contrib.auth.models import Group, Permission
from django.utils.crypto import get_random_string
from django.core.mail import send_mail


class ProfileInline(admin.TabularInline):
    model = Profile
    formset = ProfileFormSet
    # fieldsets = (
    #     (None, {'fields': ('is_manager', 'department')}),
    # )
    # add_fieldsets = (
    #     ('Personal Information', {
    #         'fields': ('organization_email', 'organization_name', 'department', 'is_staff', 'is_active', 'groups',)}
    #      ),
    # )

    def get_formset(self, request, obj=None, **kwargs):
        if obj:
            kwargs['exclude'] = ('is_manager',)
        return super().get_formset(request, obj, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return False


# class ProfileAdmin(admin.ModelAdmin):
#     list_display = ('is_manager',)
#     fieldsets = (
#         (None, {'fields': ('is_manager', 'department',)}),
#     )


class UserAdmin(BaseUserAdmin):
    add_form = UserModelForm
    model = User
    inlines = [
        ProfileInline,
    ]

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            # we are on change page if the below condition is TRUE
            if obj is None or not obj.is_admin:
                yield inline.get_formset(request, obj), inline

    list_display = ('email',
                    'is_admin',)
    list_filter = ('is_superuser', 'is_staff',)
    ordering = ('email',)
    filter_horizontal = ()

    fieldsets = (
        ("Information", {'fields': ('email', 'phone', 'address', 'groups')}),
        ('Permissions', {'fields': ('is_staff',
                                    'is_active',)}),
    )

    # def get_user(self, obj):
    #     return obj.get_user()

    # def get_fieldsets(self, request, obj=None):
    #     fs = [
    #         ("see",  {'fields': ['address', ]}),
    #         ('Map', {'fields': [],  # required by django admin
    #                  'description':obj.get_user(),
    #                  }),
    #     ]
    #     print(obj.get_user())
    #     return fs

    # def get_fieldsets(self, request, obj=None):
    #     fields = super().get_fields(request, obj)
    #     if obj:
    #         fields_to_remove = []
    #         if request.user.is_superuser:
    #             fields_to_remove = ['is_admin', ]
    #             for field in fields_to_remove:
    #                 fields.remove(field)
    #         return fields

    # def get_fieldsets(self, request, obj=None):
    #     if not request.user.is_admin:
    #         # print("yesss")
    #         print(request.user.password)
    #         fs = [(None, {'fields': ('email', 'title', 'phone', 'description', 'url', 'password', 'is_staff',
    #                                  'is_active', 'is_manager', 'groups',)})]
    #         exclude = ('password2',)
    #         return fs
    #     else:
    #         fs = [(None, {'fields': ('email', 'title', 'phone',
    #                                  'description', 'password')})]

    # return fs

    # def get_fieldsets(self, request, obj=None):
    #     fs = super().get_fieldsets(request, obj)
    #     # fs now contains [(None, {'fields': fields})], do with it whatever you want
    #     fs[0][1]['fields': ('email'), ]
    #     return fs
    # else:
    # return ("Information", {'fields': ('email', 'title', 'phone',
    #    'description', 'password')})

    # /////// yhqn aik function bna k dekho, jo groups field ko replace kr k custom group dy

    add_fieldsets = (
        ('Personal Information', {
            # To create a section with name 'Personal Information' with mentioned fields
            'description': "added_by",
            # To make char fields and text fields of a specific size
            'classes': ('wide',),
            'fields': ('email', 'phone', 'address', 'is_staff',
                       'is_active', 'groups',)}
         ),
    )

    readonly_fields = ('is_staff', 'is_active')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # elif request.user.is_admin:
        #     return qs
        print(qs)
        print(request.user)
        return qs.filter(organization_id=request.user.organization)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return False
        return True

# 9/11/2020, rat 9.16 pe isko comment kia tha meny, ku k mjy lgta tha k iski koi zrurt ni
    def save_model(self, request, obj, form, change):
        user = request.user
        obj = form.save(commit=False)
        password = get_random_string(length=7)
        # qs = Organization.objects.
        print("user object is here",user)
        print("objecst calss is here",obj)
        print("Here is my new generated password", password)
        if obj and not change:
            print("in here")
            #print("Here is my emmail ", use)
            obj.organization = user.organization
            obj.password = password
            obj.is_admin = False

        obj.save()

        #send password from email
        send_mail('This is your passwrd', password, 'solutionsdesktop19@gmail.com', [obj], fail_silently=False)
        return obj


class DepartmentAdmin(admin.ModelAdmin):

    form = CustomDepartmentForm
    list_display = ('department_name', 'user')
    list_filter = ('department_name',)
    ordering = ('department_name',)
    filter_horizontal = ()
    fieldsets = (
        (None, {'fields': ('department_name',)}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return False
        return True

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return False
        return True

    def save_model(self, request, obj, form, change):
        # if obj.organization:
        #     obj.organization = request.user
        #     obj.save()

        user = request.user
        # if user
        obj = form.save(commit=False)
        if not change or not obj.user:
            obj.user = user
        # instance.modified_by = user
        obj.save()
        # form.save_m2m()
        return obj

    def get_form(self, request, obj=None, **kwargs):
        DepartmentForm = super().get_form(request, obj, **kwargs)

        class DepartmentFormWithRequest(DepartmentForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return DepartmentForm(*args, **kwargs)
        return DepartmentFormWithRequest


admin.site.register(User, UserAdmin)
admin.site.register(Organization)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Profile)
