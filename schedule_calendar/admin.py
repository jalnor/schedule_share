from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from schedule_calendar.models import Event

#
# class CustomUserAdmin(UserAdmin):
#     list_display = ('username', 'email', 'first_name', 'last_name', 'address')
#
#     fieldsets = (
#         (None, {
#             'fields': ('username', 'password')
#         }),
#         ('Personal info', {
#             'fields': ('first_name', 'last_name', 'email')
#         }),
#         ('Permissions', {
#             'fields': (
#                 'is_active', 'is_staff', 'is_superuser',
#                 'groups', 'user_permissions'
#             )
#         }),
#         ('Important dates', {
#             'fields': ('last_login', 'date_joined')
#         }),
#         ('Additional info', {
#             'fields': ('is_student', 'is_teacher', 'mailing_address')
#         })
#     )
#
#     add_fieldsets = (
#         (None, {
#             'fields': ('username', 'password1', 'password2')
#         }),
#         ('Personal info', {
#             'fields': ('first_name', 'last_name', 'email')
#         }),
#         ('Permissions', {
#             'fields': (
#                 'is_active', 'is_staff', 'is_superuser',
#                 'groups', 'user_permissions'
#             )
#         }),
#         ('Important dates', {
#             'fields': ('last_login', 'date_joined')
#         }),
#         ('Additional info', {
#             'fields': ('is_student', 'is_teacher', 'mailing_address')
#         })
#     )


admin.site.register(Event)
# admin.site.register(CustomUser, CustomUserAdmin)
