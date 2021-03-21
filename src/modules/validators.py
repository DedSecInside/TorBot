import validators

def validate_email(email):
    return validators.email(email)

def validate_link(link):
    return validators.url(link)