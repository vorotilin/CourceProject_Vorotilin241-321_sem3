from rest_framework import serializers
from django.utils import timezone
from .models import Project, Event, User, Category, Skill, EventType


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'photo']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']


class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProjectSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    skills = SkillSerializer(many=True, read_only=True)
    skill_ids = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='skills'
    )
    skills_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'user', 'category', 'category_id', 'title', 'description',
            'cover_image', 'skills', 'skill_ids', 'skills_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
        extra_kwargs = {
            'title': {'required': True, 'max_length': 255},
            'description': {'required': False, 'allow_blank': True},
        }

    def get_skills_count(self, obj: Project) -> int:
        """
        Возвращает количество навыков проекта.
        Args:
            obj: Объект проекта
        """
        return obj.skills.count()

    def validate_title(self, value: str) -> str:
        """
        Проверяет минимальную длину названия проекта.
        Args:
            value: Название проекта
        """
        if len(value) < 3:
            raise serializers.ValidationError("Название проекта должно содержать минимум 3 символа.")
        return value

    def validate(self, data: dict) -> dict:
        user = self.context['request'].user
        title = data.get('title')

        if title:
            existing_projects = Project.objects.filter(user=user, title=title)
            if self.instance:
                existing_projects = existing_projects.exclude(pk=self.instance.pk)

            if existing_projects.exists():
                raise serializers.ValidationError({
                    'title': 'У вас уже есть проект с таким названием.'
                })

        return data


class EventSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event_type = EventTypeSerializer(read_only=True)
    event_type_id = serializers.PrimaryKeyRelatedField(
        queryset=EventType.objects.all(),
        source='event_type',
        write_only=True,
        required=False,
        allow_null=True
    )
    has_certificate = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'user', 'event_type', 'event_type_id', 'title',
            'event_date', 'result', 'certificate_image', 'has_certificate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
        extra_kwargs = {
            'title': {'required': True, 'max_length': 255},
            'result': {'required': False, 'allow_blank': True},
            'event_date': {'required': False, 'allow_null': True},
        }

    def get_has_certificate(self, obj: Event) -> bool:
        """
        Возвращает наличие сертификата у мероприятия.
        Args:
            obj: Объект мероприятия
        """
        return obj.has_certificate()

    def validate_title(self, value: str) -> str:
        """
        Проверяет минимальную длину названия мероприятия.
        Args:
            value: Название мероприятия
        """
        if len(value) < 3:
            raise serializers.ValidationError("Название мероприятия должно содержать минимум 3 символа.")
        return value

    def validate_event_date(self, value):
        """
        Проверяет что дата мероприятия не находится в будущем.
        Args:
            value: Дата мероприятия
        """
        if value and value > timezone.now().date():
            raise serializers.ValidationError(
                'Дата мероприятия не может быть в будущем.'
            )
        return value

    def validate(self, data: dict) -> dict:
        result = data.get('result', '')
        certificate_image = data.get('certificate_image')

        if self.instance:
            if not result and result != self.instance.result:
                result = self.instance.result
            if certificate_image is None and self.instance.certificate_image:
                certificate_image = self.instance.certificate_image

        if not result and not certificate_image:
            raise serializers.ValidationError(
                'Необходимо указать либо результат участия, либо загрузить изображение сертификата.'
            )

        return data
