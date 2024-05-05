from django.core.paginator import Paginator


PAGINATION_LIMIT = 10


def get_page_obj(obj_list, request):
    paginator = Paginator(obj_list, PAGINATION_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
