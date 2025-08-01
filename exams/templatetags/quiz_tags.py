from django import template
from ..models import UserAnswer

register = template.Library()

@register.filter(name='has_answered')
def has_answered(question, user):
    """Check if a user has answered a question"""
    return UserAnswer.objects.filter(question=question, user=user).exists()