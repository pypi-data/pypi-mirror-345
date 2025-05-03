****# 🛡️ Nilva User Session Management

This module provides a robust and secure implementation of user session management based on **database-backed token
authentication**, with features like caching, session expiration, user agent validation, and session invalidation.

---

## 📁 File Structure

nilva_session/
│
├── models.py # UserSession model
├── serializers.py # SessionSerializer , TokenSessionObtainPairSerializer
├── authentication.py # Custom authentication
├── utils.py # Token utilities
├── urls.py # Endpoint routes
├── apis.py # API views
└── admin.py # Django admin customization

## 📦 Components Overview

### 1. **Model: `UserSession`**

This model keeps track of each authenticated session for a user.

#### Fields:

- `id` (UUID): Unique identifier for the session.
- `user` (ForeignKey): Link to the authenticated user.
- `key` (CharField): A unique session token (used for authentication).
- `expire_at` (DateTimeField): Expiration timestamp of the session.
- `is_active` (Boolean): Indicates if the session is currently valid.
- `last_online` (DateTimeField): Last activity timestamp.
- `last_ip` (GenericIPAddressField): IP address of the user.
- `user_agent` (TextField): Raw user agent string from the request.
- `detail` (TextField): Additional context (e.g., reason for suspension).
- `created_at` (DateTimeField): Session creation timestamp.

#### Methods:

- `is_expired`: Checks if the session has expired and updates `last_online`.
- `user_agent_data`: Parses and returns user agent info (OS, browser, device).
- `get_cache_key(key)`: Generates a cache key for storing/retrieving the session key.
- `get_cache_key_by_session_id(session_id)`: Generates a cache key for storing/retrieving the session id.
- `invalidate_cache(key)`: Deletes the cached session from memory.
- `invalidate_cache_by_session_id(session_id)`: Deletes the cached session from memory.

---

### 2. **Serializer: `SessionSerializer`**

Serializes session data for API representation.

#### Fields:

- `session_id`: Read-only primary key (UUID).
- `user_id`: Associated user ID.
- `user_agent_data`: Structured data from the user agent string.
- `last_online`: Last activity timestamp.
- `last_ip`: User's IP address.
- `created_at`: Creation time of the session.

---

### 3. **Authentication: `UserSessionDBTokenAuthentication`**

Custom authentication class replacing `TokenAuthentication`.

#### Features:

- Checks session token validity (via DB and cache).
- Validates the user agent; suspends session if it changes.
- Caches active sessions to improve performance.
- Automatically saves updated session data if IP changes.

#### Important Methods:

- `authenticate`: Extracts token and authenticates the user.
- `authenticate_credentials`: Loads session from cache or DB.
- `check_user_agent`: Suspends session if user agent changes.
- `create_user_session_from_request(user, request)`: Factory to create a session from request meta.

---

### 4. **Authentication: `UserSessionDBJwtAuthentication`**

Custom authentication class replacing `JWTAuthentication`.

#### Features:

- Checks session token validity (via DB and cache).
- Validates the user agent; suspends session if it changes.
- Caches active sessions to improve performance.
- Automatically saves updated session data if IP changes.

#### Important Methods:

- `authenticate`: Extracts token and authenticates the user.
- `get_user`: get user from session .
- `check_user_agent`: Suspends session if user agent changes.
- `create_user_session_from_request(user, request)`: Factory to create a session from request meta.

---

### 5. **Utility Functions: `utils.py`**

Reusable utility logic for session creation and management.

- `random_token_generator(size)`: Generates a random token of given size.
- `token_generator()`: Generates session token using app settings.
- `token_expire_at_generator()`: Returns expiration time using settings.
- `hash_data(data)`: Hashes a string with SHA-256.

---

### 6. **API View: `ListDestroyActiveSessionsApi`**

RESTful endpoint to list and delete sessions.

#### Features:

- `GET /active/`: List all active sessions for the authenticated user.
- `DELETE /active/?token_id=...`: Log out (deactivate) one or more sessions.

#### Permissions:

- `IsAuthenticated`: User must be logged in to interact with this endpoint.

---

### 7. **Admin: `UserSessionAdmin`**

Django Admin panel configuration for `UserSession`.

#### Features:

- Displays key session info (`id`, `key`, `user`, `expire_at`, etc.).
- Read-only fields: prevents changing sensitive data post-creation.
- Filters: View active/inactive sessions easily.

---

## 🚀 Usage Guide

Follow these steps to integrate and use the **Nilva User Session Management** system in your Django project:

---

### 8. Add App to `INSTALLED_APPS`

In your `settings.py`:

INSTALLED_APPS = [
    ...
    'nilva_session',
]

---


## 🔧 Configuration

### 9. Configure REST Framework Authentication

To enable token-based session authentication, add the following to your `settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'nilva_session.backends.UserSessionDBTokenAuthentication',
        'nilva_session.backends.UserSessionDBJwtAuthentication',
        ...
    ],
}****
