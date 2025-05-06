
def _get_error_details(data, default_code=None):
    if isinstance(data, str):
        return {"message": data, "code": default_code}
    elif isinstance(data, dict):
        ret = {
            key: value
            for key, value in data.items()
        }
        ret['code'] = default_code
        return ret

class MailTransportValidationError(Exception):
    """Custom exception for API errors."""
    status_code = 400
    default_detail = 'An error occurred while processing your request.'
    default_code = 'invalid'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        self.detail = _get_error_details(detail, code)
    
    def __str__(self):
        return str(self.detail)
    
class MailTransportAPIError(MailTransportValidationError):
    pass
