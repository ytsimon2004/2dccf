Installation
===============

There are two options for setting up the environment and installing the package.
Clone the repository and change the directory to

.. code-block:: bash

    cd [CLONE_DIR]/ccf2d


UV Environment (Recommended)
---------------------------------

.. code-block:: bash

    # Create virtual environment (inside the package after cloning)
    uv venv

    # Activate environment
    source .venv/bin/activate         # Linux/macOS
    source .venv/Scripts/activate     # Windows

    # Install package
    uv pip install -e .

Conda Environment
----------------------

.. code-block:: bash

    # Create conda environment
    conda create -n ccf2d python=3.12 -y

    # Activate environment
    conda activate ccf2d

    # Install package
    pip install -e .