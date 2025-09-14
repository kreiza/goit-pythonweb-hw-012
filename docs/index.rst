Contacts API Documentation
==========================

Welcome to the Contacts API documentation. This API provides endpoints for managing contacts with authentication and authorization.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Features
--------

* JWT Authentication with Redis caching
* Email verification
* Password reset functionality
* Role-based access control (user/admin)
* Contact management with search
* Upcoming birthdays tracking
* Rate limiting
* Avatar upload via Cloudinary

API Modules
-----------

.. automodule:: contacts_api.main
   :members:

.. automodule:: contacts_api.auth
   :members:

.. automodule:: contacts_api.crud
   :members:

.. automodule:: contacts_api.models
   :members:

.. automodule:: contacts_api.schemas
   :members:

.. automodule:: contacts_api.redis_cache
   :members:

.. automodule:: contacts_api.email_service
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`