import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class InactivePoll(Exception):
    pass


class ManualAnswerRequired(Exception):
    pass


class ExistingAnswerRequired(Exception):
    pass


class QuestionWasAnswered(Exception):
    pass


class Poll(models.Model):
    name = models.CharField(max_length=100)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    description = models.TextField(default='', blank=True)

    @property
    def is_inactive(self):
        return not self.date_start < timezone.now() < self.date_end


class Question(models.Model):
    MANUAL_ANSWER = 1
    SINGLE_CHOICE = 2
    MULTIPLE_CHOICE = 3

    QUESTION_TYPE_CHOICES = (
        (MANUAL_ANSWER, 'Ответ текстом'),
        (SINGLE_CHOICE, 'Единственный выбор'),
        (MULTIPLE_CHOICE, 'Множественный выбор'),
    )

    poll = models.ForeignKey(Poll, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    type = models.IntegerField(choices=QUESTION_TYPE_CHOICES)

    @property
    def preset_answers(self):
        return self.answers.filter(is_manual=False)


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.TextField()
    is_manual = models.BooleanField(default=False)


class Result(models.Model):
    user = models.ForeignKey(User, related_name='results', null=True, blank=True, on_delete=models.SET_NULL)
    answer = models.ForeignKey(Answer, related_name='results', on_delete=models.CASCADE)
