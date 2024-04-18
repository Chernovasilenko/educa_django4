from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from courses.fields import OrderField

User = get_user_model()


class Subject(models.Model):
    """Предмет."""
    title = models.CharField(verbose_name='Название предмета', max_length=200)
    slug = models.SlugField(verbose_name='Слаг', max_length=200, unique=True)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title


class Course(models.Model):
    """Курс."""
    owner = models.ForeignKey(
        User,
        verbose_name='Преподаватель',
        related_name='courses_created',
        on_delete=models.CASCADE
    )
    subject = models.ForeignKey(
        Subject,
        verbose_name='Предмет',
        related_name='courses',
        on_delete=models.CASCADE
    )
    title = models.CharField(verbose_name='Название курса', max_length=200)
    slug = models.SlugField(verbose_name='Слаг', max_length=200, unique=True)
    overview = models.TextField(verbose_name='Краткий обзор',)
    created = models.DateTimeField(
        verbose_name='Время создания курса',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title


class Module(models.Model):
    """Модуль курса."""
    course = models.ForeignKey(
        Course,
        verbose_name='Курс',
        related_name='modules',
        on_delete=models.CASCADE
    )
    title = models.CharField(verbose_name='Название модуля', max_length=200)
    description = models.TextField(verbose_name='Описание', blank=True)
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return f'{self.order}. {self.title}'


class Content(models.Model):
    """Содержимое курса."""
    module = models.ForeignKey(
        Module,
        related_name='contents',
        on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={'model__in': ('text', 'video', 'image', 'file')}
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ('order',)


class ItemBase(models.Model):
    """Абстрактная модель для  содержимого курса."""
    owner = models.ForeignKey(
        User,
        related_name='%(class)s_related',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Text(ItemBase):
    """Текстового содержимое."""
    content = models.TextField()


class File(ItemBase):
    """Файлы курса."""
    file = models.FileField(upload_to='files')


class Image(ItemBase):
    """Изображения курса."""
    file = models.FileField(upload_to='images')


class Video(ItemBase):
    """Видео курса."""
    url = models.URLField()
