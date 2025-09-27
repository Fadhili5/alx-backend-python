from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

User = get_user_model()

@login_required
@require_POST
def delete_user(request):
    user = request.user
    user.delete()
    return JsonResponse({'message': 'User account and related data deleted successfully.'})





