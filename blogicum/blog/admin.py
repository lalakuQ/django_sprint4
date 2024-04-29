from django.contrib import admin
from django.db import models
from django.forms import Textarea
from .models import Post, Category, Location


admin.site.empty_value_display = 'Не задано'


class PostInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 40})},
    }
    model = Post
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at',
    )
    list_editable = (
        'author',
        'location',
        'category',
        'is_published',
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title', )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
    )
    list_filter = (
        'title',
        'created_at',
    )
    list_display_links = (
        'title',
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'name',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
    )
    list_display_links = (
        'name',
    )
