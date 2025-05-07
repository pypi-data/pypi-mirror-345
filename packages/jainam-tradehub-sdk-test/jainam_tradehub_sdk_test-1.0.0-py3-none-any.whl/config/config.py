
class ServiceProps:
    """Service Props class for API settings and endpoints."""

    # Base URL for API requests
    BASE_URL = "https://protrade.jainam.in/"
    API_NAME = "Codifi ProTrade - Python Library"
    CONTRACT_BASE_URL = "https://protrade.jainam.in/contract/csv/"

    # Endpoints for authorization
    GET_VENDOR_SESSION = "omt/auth/sso/vendor/getUserDetails"

    # Endpoint for client profile
    GET_PROFILE = "omt/api-order-rest/v1/profile//"

    # Endpoint for funds
    GET_FUNDS = "omt/api-order-rest/v1/limits/"

    # Endpoints for positions and holdings
    GET_POSITIONS = "omt/api-order-rest/v1/positions"
    GET_HOLDINGS = "omt/api-order-rest/v1/holdings"

    # Endpoints for position conversion & margin
    POSITION_CONVERSION = ""
    SINGLE_ORDER_MARGIN = "omt/api-order-rest/v1/orders/checkMargin"

    # Endpoints for orders
    ORDER_EXECUTE = "omt/api-order-rest/v1/orders/placeorder"
    ORDER_MODIFY = "omt/api-order-rest/v1/orders/modify/"
    ORDER_CANCEL = "omt/api-order-rest/v1/orders/cancel/"

    # Endpoints for orders details
    GET_ORDER_BOOK = "omt/api-order-rest/v1/orders/book"
    GET_TRADE_BOOK = "omt/api-order-rest/v1/orders/trades"
    GET_ORDER_HISTORY = "omt/api-order-rest/v1/orders/history/"

    # Placeholder for chart history endpoint
    GET_CHART_HISTORY = ""  # Replace with a valid endpoint or remove if not needed

    @staticmethod
    def get_full_url(endpoint):
        """Return full URL for a given endpoint."""
        return f"{ServiceProps.BASE_URL}{endpoint}"


