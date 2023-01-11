from constants import NUM_OF_POSTS
from django.core.paginator import Paginator


def paginate_page(request, post_list):
    paginator = Paginator(post_list, NUM_OF_POSTS)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)
    return page_object
