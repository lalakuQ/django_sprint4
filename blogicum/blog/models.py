from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class BaseModel(models.Model):
    is_published = models.BooleanField(default=True,
                                       verbose_name='Опубликовано',
                                       help_text=('Снимите галочку, '
                                                  'чтобы скрыть публикацию.'))
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Добавлено',
                                      )

    class Meta:
        abstract = True


class CustomManager(models.Manager):
    def custom_filter(self, date_now) -> models.QuerySet:
        return super().select_related(
            'location', 'category', 'author').filter(
            is_published=True,
            category__is_published=True,
            pub_date__lt=date_now
        )


class Post(BaseModel):
    objects = CustomManager()
    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        on_delete=models.CASCADE,
    )
    location = models.ForeignKey(
        'Location',
        verbose_name='Местоположение',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    category = models.ForeignKey(
        'Category',
        verbose_name='Категория',
        on_delete=models.CASCADE,
        null=True,
        related_name='posts',
    )
    image = models.ImageField('Фото', blank=True, upload_to='post_images')
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=('Если установить дату и время в будущем — '
                   'можно делать отложенные публикации.'),
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Добавлено',)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    text = models.TextField('Текст комментария')

    class Meta:
        ordering = ('-created_at',)


class Category(BaseModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=('Идентификатор страницы для URL; '
                   'разрешены символы латиницы, цифры, дефис '
                   'и подчёркивание.'),
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField(max_length=256, verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name
