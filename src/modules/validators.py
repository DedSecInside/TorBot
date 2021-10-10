import validators


def validate_email(email):
    if not isinstance(email, str):
        return False
    return validators.email(email)


def validate_link(link):
    if not isinstance(link, str):
        return False
    return validators.url(link)
