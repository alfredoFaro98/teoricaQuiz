from django.contrib import admin
from .models import Lecture, Question, AnswerOption

class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    min_num = 4
    max_num = 4
    extra = 0

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerOptionInline]
    list_display = ('text', 'lecture', 'times_answered', 'times_correct', 'times_wrong')
    list_filter = ('lecture',)

admin.site.register(Lecture)
admin.site.register(Question, QuestionAdmin)
admin.site.register(AnswerOption)
