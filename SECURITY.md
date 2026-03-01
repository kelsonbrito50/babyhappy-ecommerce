# Security Policy — BabyHappy E-Commerce

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |

---

## Reporting a Vulnerability

**Please do NOT open a public GitHub issue for security vulnerabilities.**

Use one of the following channels:

1. **GitHub Private Vulnerability Reporting** (preferred): open a [private security advisory](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability) in this repository.
2. **Email:** ecommdev02@gmail.com — subject line `[SECURITY] BabyHappy`.

**Include in your report:**
- Description of the vulnerability and affected component
- Steps to reproduce (minimal PoC preferred)
- Potential impact (data exposure, privilege escalation, etc.)
- Suggested remediation (if any)

We will acknowledge within **48 hours** and resolve:
- **Critical / High** within 7 days
- **Medium** within 30 days
- **Low** within 90 days

---

## Security Audit — Results (2026-03-01)

### ✅ Passed Checks

| Control | Status | Detail |
|---|---|---|
| Password Hashing | ✅ PASS | Django's PBKDF2-SHA256 (default) via `set_password()`. `AbstractUser` ensures passwords are never stored in plaintext. |
| Password Validators | ✅ PASS | All four Django validators active: similarity, min-length, common-passwords, numeric-only. |
| CSRF Protection | ✅ PASS | `CsrfViewMiddleware` active in `MIDDLEWARE`. `CSRF_COOKIE_SECURE=True` and `CSRF_COOKIE_SAMESITE='Strict'` in production. |
| Session Cookie Security | ✅ PASS | `SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE='Lax'` set in production settings. |
| SQL Injection | ✅ PASS | All queries use Django ORM (`objects.get`, `objects.filter`, etc.). No raw SQL or string interpolation found. |
| Hardcoded Credentials | ✅ PASS | No credentials in source code. All secrets loaded via `python-decouple` from environment variables. |
| HTTPS Enforcement | ✅ PASS | `SECURE_SSL_REDIRECT=True` in production. HSTS 1-year with `includeSubDomains` and `preload`. |
| Rate Limiting | ✅ PASS | DRF throttling: anonymous 100/hour, authenticated 1000/hour. |
| Debug Mode | ✅ PASS | `DEBUG=False` in production (no default fallback — will raise if env var missing). |
| Admin URL | ✅ PASS | `ADMIN_URL` configurable via env var — default path can be obfuscated in production. |

### ⚠️ Observations (Low Risk)

| Finding | Risk | Detail |
|---|---|---|
| `'unsafe-inline'` in script-src CSP | Low | Required for Bootstrap/jQuery snippets loaded from CDNs. Mitigated by CDN allowlist. Nonce-based CSP is the ideal long-term fix. |
| Payment gateway is a mock | Info | `CieloGateway` is a demo stub. Real production integration must validate card data server-side and never log full card numbers. |
| CPF stored as plain text | Info | `CustomUser.cpf` is stored as a plain char field. Consider masking/encrypting PII at rest for LGPD compliance. |

### 🚫 No Critical/High Vulnerabilities Found

---

## Security Configurations Implemented

### HTTP Security Headers (`config/middleware.py` — `SecurityHeadersMiddleware`)

| Header | Value |
|---|---|
| `Content-Security-Policy` | `default-src 'self'`; CDN allowlist for scripts/styles/fonts; `frame-ancestors 'none'`; `base-uri 'self'`; `form-action 'self'` |
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | Restricts camera, microphone, geolocation, payment, USB, etc. |
| `X-XSS-Protection` | `1; mode=block` (legacy browser compat) |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` (HTTPS only) |

### Content-Security-Policy Detail

```
default-src 'self';
script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com;
style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com;
font-src 'self' https://fonts.gstatic.com;
img-src 'self' data: https:;
connect-src 'self';
frame-ancestors 'none';
base-uri 'self';
form-action 'self';
```

### Django Security Settings (Production)

```python
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Strict"
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
```

### Authentication & Authorisation

- **Custom user model** (`CustomUser`) with email-based login, no username enumeration.
- **JWT + Session dual auth** via `rest_framework_simplejwt`.
- **Password hashing** via Django's PBKDF2-SHA256 (upgradeable to Argon2 by installing `argon2-cffi` and prepending to `PASSWORD_HASHERS`).

### Error Monitoring

- **Sentry** integration in production when `SENTRY_DSN` is set. PII stripping enabled (`send_default_pii=False`).

---

## Recommended Future Improvements

1. **Argon2 password hasher** — add `argon2-cffi` and set `PASSWORD_HASHERS = ["django.contrib.auth.hashers.Argon2PasswordHasher", ...]` for stronger hashing.
2. **Nonce-based CSP** — replace `'unsafe-inline'` with per-request nonces for even stronger XSS protection.
3. **CPF encryption** — encrypt PII fields at rest (`django-cryptography` or field-level encryption) for LGPD compliance.
4. **2FA / MFA** — add TOTP-based two-factor authentication for admin users (`django-otp` or `allauth` MFA).
5. **Dependency scanning** — integrate `safety check` or GitHub Dependabot alerts for CVE tracking on Python packages.
6. **Security headers score** — validate at [securityheaders.com](https://securityheaders.com) after deploy.
