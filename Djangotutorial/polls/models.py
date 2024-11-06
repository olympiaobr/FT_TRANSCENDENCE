import datetime

from django.db import models
from django.utils import timezone

# Create your models here.

class Question(models.Model):
    question_text = models.CharField(max_length = 256)
    publication_date = models.DateTimeField("Publication date")
    def __str__(self):
        return self.question_text
    def was_published_recently(self):
        return self.publication_date >= timezone.now() - datetime.timedelta(days=1)

class Answer(models.Model):
    questions = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length = 256)
    votes = models.IntegerField(default = 0)
    def __str__(self):
        return self.answer_text