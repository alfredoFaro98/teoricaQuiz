from django.db import models

class Subject(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6') # Hex color for UI

    def __str__(self):
        return self.name

class Lecture(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="lectures", null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    page_number = models.IntegerField(null=True, blank=True, help_text="Slide/Page number reference")
    nature = models.CharField(max_length=20, choices=[('Teorica', 'Teorica'), ('Pratica', 'Pratica')], default='Teorica')

    # statistiche aggregate
    times_answered = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)
    times_wrong = models.IntegerField(default=0)

    def __str__(self):
        return self.text[:80]


class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{'[OK]' if self.is_correct else '[X]'} {self.text[:60]}"
