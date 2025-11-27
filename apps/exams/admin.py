from django.contrib import admin

from apps.exams.models import Exam


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "price", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "code"]
