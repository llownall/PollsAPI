from rest_framework import generics, authentication, viewsets, views
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from polls.serializers import *


class PollViewSet(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]
    queryset = Poll.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return PollCreateSerializer
        return PollRetrieveSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]
    queryset = Question.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return QuestionCreateSerializer
        return QuestionRetrieveSerializer


class AnswerDetail(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def perform_destroy(self, instance):
        if instance.question.type != Question.MANUAL_ANSWER and instance.question.answers.count() == 1:
            raise ValidationError('Нельзя удалить последний ответ для вопроса с выбором ответа')
        instance.delete()


class ActivePollList(generics.ListAPIView):
    queryset = Poll.objects.filter(date_start__lt=timezone.now(), date_end__gt=timezone.now())
    serializer_class = DetailedPollSerializer


class AnswerQuestionView(views.APIView):
    def post(self, request, format=None):
        result = ResultSerializer(data=request.data)
        if result.is_valid():
            result.save()
            return Response({'message': 'Ответ принят'})
        return Response({'message': 'Ответ не принят'}, status=400)


class UserResultsList(generics.ListAPIView):
    serializer_class = AnsweredPollSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        try:
            user = User.objects.get(id=self.kwargs.get('user_id', None))
        except User.DoesNotExist:
            user = None
        context.update({'user': user})
        return context

    def get_queryset(self):
        user = User.objects.get(id=self.kwargs['user_id'])
        return Poll.objects.filter(questions__answers__results__user=user).distinct()
