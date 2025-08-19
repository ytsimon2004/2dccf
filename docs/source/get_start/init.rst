Initialize Project
===================

Once you've installed the `ccf2d` package, proceed with the following steps to initialize and configure the environment.

Download Atlas Data
-------------------

Run the init command to download the Allen Brain Atlas reference data and templates. This will create a ``.ccf2d`` directory in your home folder containing the necessary atlas files.

.. code-block:: bash

    ccf2d init

.. note::
    
    This command downloads approximately 5GB of atlas data. Ensure you have a stable internet connection and sufficient disk space.