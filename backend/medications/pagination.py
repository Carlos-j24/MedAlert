from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    """
    Paginación por defecto para toda la API.

    - 10 resultados por página por defecto.
    - El cliente puede pedir más con ?page_size=N (hasta 100),
      útil para pantallas que necesitan "todo" sin paginar
      visualmente (ej. conteos del dashboard, un <select>).
    """

    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
