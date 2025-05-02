Setup for Snowflake Native App
==============================

This guide explains how to use Kumo SDK with `Kumo Snowflake Native Application <https://kumo.ai/docs/snowflake-native-application>`_.

Running SDK Outside Snowflake
-----------------------------

When running the SDK outside Snowflake, you can initialize it with your Snowflake credentials:

.. code-block:: python

    import kumoai as kumo
    credentials = {
        "user": "<your username>",
        "password": "<your password>",
        "account": "<your account>",
    }
    kumo.init(url="https://<kumo_spcs_deployment_url>/api", snowflake_credentials=credentials)

For detailed examples of using the SDK outside Snowflake, refer to our `Introduction by Example <https://kumo-ai.github.io/kumo-sdk/docs/get_started/introduction.html#id1>`_.

Running SDK on Snowflake
------------------------

To run the SDK directly on Snowflake, you'll need to use a Snowflake notebook configured for Snowpark Container (choose `Run on Container`). This setup provides a managed environment for running machine learning workloads.

.. image:: ../../assets/snowflake_notebook.png
   :alt: Snowflake Notebook Configuration
   :width: 50%
   :align: center

For instructions on setting up your notebook environment, refer to the `Snowflake ML Notebooks on SPCS documentation <https://docs.snowflake.com/developer-guide/snowflake-ml/notebooks-on-spcs>`_.

Using External Access
^^^^^^^^^^^^^^^^^^^^^

If your notebook environment has external access configured (see `External Access Configuration <https://docs.snowflake.com/user-guide/ui-snowsight/notebooks-external-access>`_), you can install Kumo SDK directly using pip:

.. code-block:: bash

    pip install kumoai=<kumo_app_version>

Using Package Installation
^^^^^^^^^^^^^^^^^^^^^^^^^^

If external access is not available or not permitted in your environment, follow these steps:

1. Contact the Kumo team to obtain the SDK package zip file
2. Upload the package to your Snowflake stage
3. Install the package from the stage

The recommended way to upload the package is using the Snowsight UI:

.. image:: ../../assets/package_install.png
   :alt: Package Installation Flow
   :width: 50%
   :align: center

1. Sign in to Snowsight
2. Select Data » Add Data
3. On the Add Data page, select Load files into a Stage
4. In the Upload Your Files dialog:
   - Select the kumoai.zip file (maximum file size: 250 MB)
   - Select the database and schema where you want to create the stage
   - Select or create your stage (e.g., 'kumo_stage')
   - Optionally, specify a path within the stage
5. Select Upload

For detailed instructions, you can refer to:
- `Staging files using Snowsight UI <https://docs.snowflake.com/en/user-guide/data-load-local-file-system-stage-ui>`_
- `Using SnowSQL Client <https://docs.snowflake.com/en/user-guide/data-load-local-file-system-stage>`_ (command line alternative)

Getting Started
---------------

When running in a Snowflake notebook environment, the SDK automatically uses the Snowflake context, eliminating the need for additional credentials. This is different from the normal SDK initialization process, making it simpler to get started:

.. code-block:: python

    import kumoai as kumo
    
    # Initialize with just the application name - no additional credentials needed
    kumo.init(snowflake_application='YOUR_APP_NAME')

    # Create a Snowflake connector with your Snowflake resources
    my_connector = kumo.SnowflakeConnector(
        name="YOUR_CONNECTOR_NAME",
        account="YOUR_SNOWFLAKE_ACCOUNT_NAME",
        warehouse="YOUR_SNOWFLAKE_ACCOUNT_NAME",
        database="YOUR_SNOWFLAKE_DATABASE_NAME",
        schema_name="YOUR_SNOWFLAKE_SCHEMA_NAME",
    )
    
    # Start using Kumo's features with your connector
    # ...

For the rest of code block, including graph and training setup, refer to :doc:`/get_started/introduction`.

Additional Resources
--------------------

- `Snowpark Container Services Documentation <https://docs.snowflake.com/en/user-guide/snowpark-container-services-overview>`_
- `Snowflake Native Apps Documentation <https://docs.snowflake.com/en/user-guide/nativeapps-intro>`_
- `Snowflake ML Notebooks Documentation <https://docs.snowflake.com/developer-guide/snowflake-ml/notebooks-on-spcs>`_ 