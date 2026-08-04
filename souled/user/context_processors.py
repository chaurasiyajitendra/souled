from .models import Category,User

def global_data(request):

    user = None
    userId = request.session.get("user_id")

    if userId:
        user = User.objects.filter(id=userId).first()

    return {
        "categories": Category.objects.prefetch_related(
            "subcategories__childcategories"
        ),
        "user" :user,
        "is_login": "username" in request.session,
    }