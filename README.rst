========================
Elmware SDK: For Building Containers to Run on Elmware 
========================


Highlights:
 * Compatible with Python 3
 * Built on top of requests - the sole dependency
 * Installable with pypi
 * Includes a full test suite able to interact with the server
 * For use in any linux based docker container builds running on elmware



For more information, please refer to the documentation in the docs directory




Installation
------------

.. code-block:: bash

    pip install elmsdk


Usage
-----
.. code-block:: python

    from elmsdk import ELMSDK

    elm = ELMSDK(instance_key)
    staus = elm.begin_run()




For more information, please refer to the documentation in the docs directory


Support
=======

If you need technical support, please reach out to support@elmware.com
