from rest_framework import serializers

from polls.models import *


class PollDatesValidation:
    def validate(self, data):
        if data['date_end'] <= data['date_start']:
            raise serializers.ValidationError(
                {'date_end': 'Дата окончания опроса не может быть раньше или совпадать с датой начала'}
            )
        return data


class PollCreateSerializer(PollDatesValidation, serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = '__all__'


class PollRetrieveSerializer(PollDatesValidation, serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = '__all__'
        read_only_fields = ['date_start']


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        exclude = ['question', 'is_manual']


class QuestionCreateSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = '__all__'

    def create(self, validated_data):
        if 'answers' in validated_data:
            answers_data = validated_data.pop('answers')
            question = Question.objects.create(**validated_data)
            for answer_data in answers_data:
                Answer.objects.create(question=question, **answer_data)
        else:
            question = Question.objects.create(**validated_data)
        return question

    def validate(self, data):
        question_type = data['type']
        answers = data.get('answers', [])
        if question_type != Question.MANUAL_ANSWER and not answers:
            raise serializers.ValidationError({'answers': 'Не указано ни одного ответа'})
        return data


class QuestionRetrieveSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True, source='preset_answers')

    class Meta:
        model = Question
        fields = '__all__'

    def validate_type(self, value):
        if value != Question.MANUAL_ANSWER and self.instance.answers.count() == 0:
            raise serializers.ValidationError('Не указано ни одного ответа')
        return value


class DetailedPollSerializer(serializers.ModelSerializer):
    questions = QuestionRetrieveSerializer(many=True)

    class Meta:
        model = Poll
        fields = '__all__'


class ResultSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False)
    question_id = serializers.IntegerField()
    answer_id = serializers.IntegerField(required=False)
    answer = serializers.CharField(required=False)

    def create(self, validated_data):
        try:
            has_answer_id = validated_data.get('answer_id', None) is not None
            has_answer = validated_data.get('answer', None) is not None

            if user_id := validated_data.get('user_id', False):
                user = User.objects.get(id=user_id)
            else:
                user = None
            question = Question.objects.get(id=validated_data['question_id'])

            answer = None
            if answer_id := validated_data.get('answer_id', False):
                answer = Answer.objects.get(id=answer_id, question=question)

            if user is not None:
                if question.type != Question.MULTIPLE_CHOICE and question.answers.filter(results__user=user).exists():
                    raise QuestionWasAnswered
                elif user.results.filter(
                        answer__question=question,
                        answer=answer
                ).exists():
                    raise QuestionWasAnswered
            if has_answer_id and question.type == Question.MANUAL_ANSWER:
                raise ManualAnswerRequired
            if has_answer and question.type != Question.MANUAL_ANSWER:
                raise ExistingAnswerRequired
            if question.poll.is_inactive:
                raise InactivePoll

            if answer is None:
                answer = Answer.objects.create(
                    question=question,
                    text=validated_data['answer'],
                    is_manual=True,
                )

        except User.DoesNotExist:
            raise serializers.ValidationError({'user_id': 'Пользователь с таким ID не найден'})
        except QuestionWasAnswered:
            raise serializers.ValidationError('Пользователь уже ответил на этот вопрос')
        except ManualAnswerRequired:
            raise serializers.ValidationError({'answer': 'Поле не указано'})
        except ExistingAnswerRequired:
            raise serializers.ValidationError({'answer_id': 'Поле не указано'})
        except InactivePoll:
            raise serializers.ValidationError('Опрос неактивен')
        except Question.DoesNotExist:
            raise serializers.ValidationError({'question_id': 'Вопрос с таким ID не найден'})
        except Answer.DoesNotExist:
            raise serializers.ValidationError({'answer_id': 'Ответ с таким ID не найден'})
        return Result.objects.create(user=user, answer=answer)

    def validate(self, data):
        has_answer_id = data.get('answer_id', None) is not None
        has_answer = data.get('answer', None) is not None
        if (has_answer_id and has_answer) or (not has_answer_id and not has_answer):
            raise serializers.ValidationError('Нужно указать answer_id либо answer')
        return data

    def update(self, instance, validated_data):
        raise NotImplementedError


class AnsweredQuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True, source='preset_answers')
    selected_answers = serializers.SerializerMethodField('get_selected_answers')

    class Meta:
        model = Question
        fields = '__all__'

    def get_selected_answers(self, question):
        selected_answers = Answer.objects.filter(results__user=self.context['user'], question=question)
        serializer = AnswerSerializer(instance=selected_answers, many=True)
        return serializer.data


class AnsweredPollSerializer(serializers.ModelSerializer):
    questions = AnsweredQuestionSerializer(many=True)

    class Meta:
        model = Poll
        fields = '__all__'
