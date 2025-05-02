.. _key_management:

API Key Provisioning and Management
===================================

Once you have successfully installed the Kumo SDK, you next need to ensure that
the SDK can establish a secure connection with your provisioned Kumo platform.
Doing so varies slightly based on your Kumo platform deployment model.

Kumo Free Trial
---------------

.. note::

    The public API URL of your Kumo platform is ``https://<environment_id>.trial.kumoai.cloud/api``.

In the Free Trial environments, your environment URL and API keys are
provisioned for you and sent to your sign-up e-mail. Your environment and API
key will last for 7 days.

You can verify your API key's usage by initializing the Kumo SDK against your
running Kumo platform. To do so, we will use the :meth:`~kumoai.init` method,
which initializes the SDK by establishing a connection to your platform
(passing the platform URL and API key).

.. code-block:: python

    import kumoai as kumo
    kumo.init(url="https://<environment_id>.trial.kumoai.cloud/api", api_key="<api_key>")


Kumo SaaS and Databricks Edition
--------------------------------

.. note::

    The public API URL of your Kumo platform is ``https://<customer_id>.kumoai.cloud/api``.

In the SaaS and Databricks Edition environments, API keys are provisioned and
managed by a Kumo platform administrator. The instructions to generate a
public API key are located in the
`Kumo documentation <https://docs.kumo.ai/docs/rest-api#generating-an-api-key>`__;
upon performing these steps, you should be presented with an API key of the
form

.. code-block::

    <customer_id>:<secret_value>

.. warning::

    Please store this API key in a secure location; if you lose the key, you
    will need to generate a new one from scratch.

Once you have generated your API key, you can verify its usage by initializing
the Kumo SDK against your running Kumo platform. To do so, we will use the
:meth:`~kumoai.init` method, which initializes the SDK by establishing a
connection to your platform (passing the platform URL and API key).

.. code-block:: python

    import kumoai as kumo
    kumo.init(url="https://<customer_id>.kumoai.cloud/api", api_key="<api_key>")

Rotating Your API Key
~~~~~~~~~~~~~~~~~~~~~~

It is best practice to periodically rotate/re-generate your API Key in case it
gets breached. To rotate your API Key, you can follow the same steps as above to
generate an API Key. Once an API Key is generated, any previous API Keys are
automatically invalidated.

Kumo Snowpark Container Services
---------------------------------

.. note::

    The public API URL of your Kumo platform is ``https://<kumo_spcs_deployment_url>/api``.

In the Snowpark Container Services (SPCS) environment, API keys are unnecessary
as authentication is handled by the Snowflake environment. Instead, you must
provide your Snowflake credentials, which are forwarded to the SPCS
application.

Once you have your Snowflake username, password, and account, you can verify
their usage by initializing the Kumo SDK against your running Kumo platform. To
do so, we will use the :meth:`~kumoai.init` method, which initializes the SDK
by establishing a connection to your platform.

.. code-block:: python

    import kumoai as kumo
    credentials = {
        "user": <your username>,
        "password": <your password>,
        "account": <your account>,
    }
    kumo.init(url="https://<kumo_spcs_deployment_url>/api", snowflake_credentials=credentials)
