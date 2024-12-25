from django.contrib import admin
from .models import InterestCategory, UserIntroduction

@admin.register(InterestCategory)
class InterestCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(UserIntroduction)
class UserIntroductionAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_interests')
    search_fields = ('user__username', 'user__email')
    
    def get_interests(self, obj):
        return ", ".join(obj.interests) if obj.interests else "No interests selected"
    get_interests.short_description = 'Selected Interests'
