from django.contrib import admin

from .models import FlashCard, LearningUnit


class FlashCardInline(admin.TabularInline):
    model = FlashCard
    extra = 0
    ordering = ('order',)


@admin.register(LearningUnit)
class LearningUnitAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title', 'raw_content')
    inlines = [FlashCardInline]


@admin.register(FlashCard)
class FlashCardAdmin(admin.ModelAdmin):
    list_display = ('learning_unit', 'order', 'created_at')
    list_filter = ('learning_unit',)
    search_fields = ('content',)
