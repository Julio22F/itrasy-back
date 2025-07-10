import math
import sys
import time
from datetime import datetime

from drf_yasg import openapi
from lib.loguru import logger

DEFAULT_PER_PAGE = 12

def get_queryset_from_request(request, model_reference, queries=None):
    """
    Filtre un queryset sans pagination, en utilisant les paramètres GET.
    Conserve un QuerySet (pas de list) pour pouvoir appeler .values() ensuite.
    """
    start_time = time.time()
    model_fields = [field.name for field in model_reference._meta.get_fields()]
    filter_params = request.GET
    custom_filter = {}

    # Construction du filtre
    if filter_params:
        for k, v in filter_params.items():
            if k in model_fields:
                field_type = model_reference._meta.get_field(k).get_internal_type()
                if field_type in ("ForeignKey", "IntegerField"):
                    custom_filter[k] = v
                else:
                    custom_filter[f"{k}__icontains"] = v
            else:
                k_rsplit = k.rsplit('__', 1)
                if k_rsplit[-1] in ['from', 'to']:
                    field_type = model_reference._meta.get_field(k_rsplit[0]).get_internal_type()
                    if field_type in [
                        "DateField", "DateTimeField", "DecimalField",
                        "FloatField", "IntegerField", "PositiveIntegerField"
                    ]:
                        compare = '__gte' if k_rsplit[-1] == 'from' else '__lte'
                        if field_type == "DateTimeField":
                            v = v + " 00:00:00" if k_rsplit[-1] == 'from' else v + " 23:59:59"
                        custom_filter[f"{k_rsplit[0]}{compare}"] = v
                elif k_rsplit[-1] == 'array':
                    custom_filter[f"{k_rsplit[0]}__in"] = v
                elif k_rsplit[-1] == 'exact':
                    custom_filter[f"{k_rsplit[0]}__exact"] = v
                else:
                    pass

    # Création du QuerySet
    queryset_filter = model_reference.objects.filter(**custom_filter)
    if queries:
        queryset_filter = queryset_filter.filter(queries)

    elapsed = time.time() - start_time

    # Mesure de la performance via un list() temporaire, sans casser le QuerySet
    qs_list = list(queryset_filter)
    data_count = len(qs_list)
    data_size_mb = sys.getsizeof(qs_list) / (1024 * 1024)

    logger.debug(
        f"[get_queryset_from_request] Model={model_reference.__name__}, "
        f"count={data_count}, (~{data_size_mb:.2f} MB) in {elapsed:.3f}s"
    )

    return queryset_filter  # On retourne le QuerySet


class FilterPagination:
    """
    Filtrage + Pagination optimisé.
    - On ne transforme pas le queryset final en list pour permettre .values() plus tard.
    - On mesure le temps et la taille mémoire via une variable temporaire.
    - On peut utiliser .only(), .select_related(), .prefetch_related() avant la conversion.
    """

    @staticmethod
    def filter_and_pagination(request, model_reference, queries=None,
                              order_by_array=None, special_order_by=None):
        start_time = time.time()

        model_fields = [field.name for field in model_reference._meta.get_fields()]
        filter_params = request.GET
        custom_filter = {}

        # Construction du filtre
        if filter_params:
            for k, v in filter_params.items():
                if k in model_fields:
                    field_type = model_reference._meta.get_field(k).get_internal_type()
                    if field_type in ("ForeignKey", "IntegerField"):
                        custom_filter[k] = v
                    else:
                        custom_filter[f"{k}__icontains"] = v
                else:
                    k_rsplit = k.rsplit('__', 1)
                    if k_rsplit[-1] in ['from', 'to']:
                        field_type = model_reference._meta.get_field(k_rsplit[0]).get_internal_type()
                        if field_type in [
                            "DateField", "DateTimeField", "DecimalField",
                            "FloatField", "IntegerField", "PositiveIntegerField"
                        ]:
                            compare = '__gte' if k_rsplit[-1] == 'from' else '__lte'
                            if field_type == "DateTimeField":
                                v = v + " 00:00:00" if k_rsplit[-1] == 'from' else v + " 23:59:59"
                            custom_filter[f"{k_rsplit[0]}{compare}"] = v
                    elif k_rsplit[-1] == 'array':
                        custom_filter[f"{k_rsplit[0]}__in"] = v
                    elif k_rsplit[-1] == 'exact':
                        custom_filter[f"{k_rsplit[0]}__exact"] = v
                    else:
                        pass

        queryset_filter = model_reference.objects.filter(**custom_filter)
        if queries:
            queryset_filter = queryset_filter.filter(queries)

        # Tri
        order_by_field = filter_params.get('order_by') if (
            'order_by' in filter_params and filter_params['order_by'] in model_fields
        ) else 'id'
        order_type = filter_params.get('order_type', '')
        if order_type != '-':
            order_type = ''
        order_by = order_type + order_by_field

        # Pagination
        per_page = int(filter_params.get('per_page', DEFAULT_PER_PAGE) or DEFAULT_PER_PAGE)
        if per_page == 0:
            per_page = DEFAULT_PER_PAGE
        page_no = int(filter_params.get('page_no', 1) or 1)

        start_limit = (per_page * page_no) - per_page
        end_limit = per_page * page_no

        total_object_count = queryset_filter.count()
        total_pages = math.ceil(total_object_count / per_page)

        # Order
        if order_by_array:
            oba = order_by_array + (order_by,)
            queryset_filter = queryset_filter.order_by(*oba)
        else:
            queryset_filter = queryset_filter.order_by(order_by)

        # special_order_by => pas de slicing
        if special_order_by:
            queryset = queryset_filter.filter(special_order_by['queries'])
            if special_order_by.get('orders'):
                queryset = queryset.order_by(special_order_by['orders'])
        else:
            queryset = queryset_filter[start_limit:end_limit]

      
        queryset = (
            queryset
            .only("id", "created_at", "updated_at")  # + autres champs si nécessaire
            # .select_related("some_fk_field")        # si une FK
            # .prefetch_related("some_m2m_field")     # si un M2M
        )

        # On fait un list(...) pour la mesure, SANS l'affecter au 'dataset'
        qs_list = list(queryset)
        data_count = len(qs_list)
        data_size_mb = sys.getsizeof(qs_list) / (1024 * 1024)
        elapsed = time.time() - start_time

        logger.debug(
            f"[filter_and_pagination OPTIM] Model={model_reference.__name__}, "
            f"count={data_count}, (~{data_size_mb:.2f} MB) in {elapsed:.3f}s"
        )

        # On retourne un QuerySet dans le dataset pour pouvoir faire .values() 
        dataset = {
            'queryset': queryset,  
            'pagination': {
                'per_page': per_page,
                'current_page': page_no,
                'total_count': total_object_count,
                'total_pages': total_pages
            }
        }
        return dataset

    @staticmethod
    def filter_and_pagination_by_queryset(request, queryset):
        """
        Paginer un queryset déjà prêt.
        On ne le convertit pas en liste, pour qu'on puisse faire .values() si besoin.
        """
        filter_params = request.GET
        per_page = int(filter_params.get('per_page', DEFAULT_PER_PAGE) or DEFAULT_PER_PAGE)
        page_no = int(filter_params.get('page_no', 1) or 1)
        return FilterPagination.pagination_by_queryset(queryset, per_page, page_no)

    @staticmethod
    def pagination_by_queryset(queryset, per_page, page_no):
        """
        Paginer un queryset déjà filtré/trié.
        On peut rajouter only/select_related/prefetch_related ici si besoin.
        """
        start_time = time.time()

        start_limit = (int(per_page) * int(page_no)) - int(per_page)
        end_limit = int(per_page) * int(page_no)

        total_object_count = queryset.count()
        total_pages = math.ceil(total_object_count / int(per_page))

        # On slice 
        page_qs = queryset[start_limit:end_limit]

        # On fait un list(...) pour la mesure, mais on retourne le QuerySet
        qs_list = list(page_qs)
        data_count = len(qs_list)
        data_size_mb = sys.getsizeof(qs_list) / (1024 * 1024)
        elapsed = time.time() - start_time

        logger.debug(
            f"[pagination_by_queryset OPTIM] Page={page_no}, "
            f"Count={data_count} (~{data_size_mb:.2f} MB), total={total_object_count} "
            f"in {elapsed:.3f}s"
        )

        dataset = {
            'queryset': page_qs,  # On conserve un QuerySet (slice)
            'pagination': {
                'per_page': per_page,
                'current_page': page_no,
                'total_count': total_object_count,
                'total_pages': total_pages
            }
        }
        return dataset

    @staticmethod
    def filter_and_pagination_by_array(request, array_data):
        """
        Paginer une simple liste en mémoire, 
        en la retournant toujours comme liste (pas de .values() possible).
        """
        start_time = time.time()

        filter_params = request.GET
        per_page = int(filter_params.get('per_page', DEFAULT_PER_PAGE) or DEFAULT_PER_PAGE)
        if per_page == 0:
            per_page = DEFAULT_PER_PAGE
        page_no = int(filter_params.get('page_no', 1) or 1)

        start_limit = (per_page * page_no) - per_page
        end_limit = per_page * page_no

        total_object_count = len(array_data)
        total_pages = math.ceil(total_object_count / per_page)

        queryset_filter = array_data[start_limit:end_limit]
        qs_list = list(queryset_filter)
        data_count = len(qs_list)
        data_size_mb = sys.getsizeof(qs_list) / (1024 * 1024)
        elapsed = time.time() - start_time

        logger.debug(
            f"[filter_and_pagination_by_array OPTIM] Page={page_no}, Count={data_count} "
            f"(~{data_size_mb:.2f} MB) out of {total_object_count} in {elapsed:.3f}s"
        )

        dataset = {
            'queryset': qs_list, 
            'pagination': {
                'per_page': per_page,
                'current_page': page_no,
                'total_count': total_object_count,
                'total_pages': total_pages
            }
        }
        return dataset

    @staticmethod
    def generate_pagination_params(description=None, additional_params=None):
        """
        Génère les paramètres pour la doc (Swagger).
        """
        if additional_params is None:
            additional_params = []

        per_page_param = openapi.Parameter(
            'per_page',
            openapi.IN_QUERY,
            description="counts per page",
            type=openapi.TYPE_NUMBER
        )
        page_no_param = openapi.Parameter(
            'page_no',
            openapi.IN_QUERY,
            description="page numbers",
            type=openapi.TYPE_NUMBER
        )
        order_by_param = openapi.Parameter(
            'order_by',
            openapi.IN_QUERY,
            description="name of field to sort",
            type=openapi.TYPE_STRING
        )
        order_type_param = openapi.Parameter(
            'order_type',
            openapi.IN_QUERY,
            description="type of field to sort. Must be '-' or ''",
            type=openapi.TYPE_STRING
        )

        desc = "Search keyword. You can input any field name and value"
        if description:
            desc = description

        search_param = openapi.Parameter(
            'keyword',
            openapi.IN_QUERY,
            description=desc,
            type=openapi.TYPE_STRING
        )

        res = [per_page_param, page_no_param, order_by_param, order_type_param, search_param]
        if additional_params:
            res += additional_params
        return res

    @staticmethod
    def get_paniation_data(request, model_class, serializer_class,
                           queries=None, order_by_array=None, special_order_by=None):
        """
        Retourne data sérialisée + pagination.
        On conserve un QuerySet, donc .values() reste possible plus tard.
        """
        queryset_info = FilterPagination.filter_and_pagination(
            request,
            model_class,
            queries,
            order_by_array,
            special_order_by
        )
        # sérialise la partie 'queryset' (qui est encore un QuerySet).
        serialized = serializer_class(queryset_info['queryset'], many=True).data
        return {
            'dataset': serialized,
            'pagination': queryset_info['pagination']
        }

    @staticmethod
    def get_paniation_data_by_queryset(request, queryset, serializer_class):
        """
        Paginer + sérialiser un queryset existant, 
        sans le convertir définitivement en liste dans le 'dataset'.
        """
        res = FilterPagination.filter_and_pagination_by_queryset(request, queryset)
        serialized = serializer_class(res['queryset'], many=True).data
        return {
            'dataset': serialized,
            'pagination': res['pagination']
        }

    @staticmethod
    def get_paniation_data_by_queryset_for_post(request, queryset,
                                                serializer_class,
                                                per_page, page_no):
        """
        Paginer + sérialiser en POST (ou autre) via per_page/page_no.
        """
        res = FilterPagination.pagination_by_queryset(queryset, per_page, page_no)
        serialized = serializer_class(res['queryset'], many=True).data
        return {
            'dataset': serialized,
            'pagination': res['pagination']
        }

    @staticmethod
    def get_paniation_data_by_array(request, array_data, serializer_class):
        """
        Paginer + sérialiser une liste en mémoire.
        """
        res = FilterPagination.filter_and_pagination_by_array(request, array_data)
        # pour sérialiser :
        # serialized = serializer_class(res['queryset'], many=True).data
        return {
            'dataset': res['queryset'],
            'pagination': res['pagination']
        }
