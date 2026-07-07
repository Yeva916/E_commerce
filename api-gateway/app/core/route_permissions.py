PUBLIC_ROUTES = [

    ("POST","/api/auth/login"),
    ("GET","/api/auth/login/google"),
    ("GET","/api/auth/google/callback"),

    ("","/api/auth/register"),

    ("GET","/api/auth/verify-email"),

    ("POST","/api/auth/forgot-password"),
    ("POST","/api/auth/reset-password"),

    ("GET","/api/auth/refresh-token"),

    ("GET","/api/products"),
]