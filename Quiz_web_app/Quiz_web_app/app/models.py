from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model( username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username
    
class Quiz(models.Model):
    title = models.CharField(max_length=120, unique=True)
    description = models.CharField(max_length=300)
    number_of_questions = models.PositiveSmallIntegerField()

    def create_example_1(self):
        quiz = Quiz.objects.create(
            title='My Quiz7',
            description='This is a sample quiz 7 for testing purposes',
            number_of_questions=2
        )
        quiz.save()

        question1 = Question.objects.create(
            quiz=quiz,
            text='What is the capital of France?'
        )
        question1.save()

        question2 = Question.objects.create(
            quiz=quiz,
            text='What is the largest planet in our solar system?'
        )
        question2.save()

        # Add distractors for the first question
        distractor1 = Distractor.objects.create(
            question=question1,
            text='Berlin'
        )
        distractor1.save()

        distractor2 = Distractor.objects.create(
            question=question1,
            text='London'
        )
        distractor2.save()

        # Add the correct answer for the first question
        correct_answer1 = Answer.objects.create(
            question=question1,
            text='Paris'
        )
        correct_answer1.save()

        # Add distractors for the second question
        distractor3 = Distractor.objects.create(
            question=question2,
            text='Mars'
        )
        distractor3.save()

        distractor4 = Distractor.objects.create(
            question=question2,
            text='Venus'
        )
        distractor4.save()

        # Add the correct answer for the second question
        correct_answer2 = Answer.objects.create(
            question=question2,
            text='Jupiter'
        )
        correct_answer2.save()

    def create_example_2(self):
        quiz = Quiz.objects.create(
            title='My Quiz8',
            description='This is a sample quiz 8 for testing purposes',
            number_of_questions=2
        )
        quiz.save()

        question1 = Question.objects.create(
            quiz=quiz,
            text='What is the capital of France?'
        )
        question1.save()

        question2 = Question.objects.create(
            quiz=quiz,
            text='What is the largest planet in our solar system?'
        )
        question2.save()

        # Add distractors for the first question
        distractor1 = Distractor.objects.create(
            question=question1,
            text='Berlin'
        )
        distractor1.save()

        distractor2 = Distractor.objects.create(
            question=question1,
            text='London'
        )
        distractor2.save()

        # Add the correct answer for the first question
        correct_answer1 = Answer.objects.create(
            question=question1,
            text='Paris'
        )
        correct_answer1.save()

        # Add distractors for the second question
        distractor3 = Distractor.objects.create(
            question=question2,
            text='Mars'
        )
        distractor3.save()

        distractor4 = Distractor.objects.create(
            question=question2,
            text='Venus'
        )
        distractor4.save()

        # Add the correct answer for the second question
        correct_answer2 = Answer.objects.create(
            question=question2,
            text='Jupiter'
        )
        correct_answer2.save()
        

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)

    def __str__(self):
        return self.text

class Distractor(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=100)

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=100)

    def __str__(self):
        return self.text


