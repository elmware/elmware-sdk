Testing Sandbox
===============

The SDK provides a testing sandbox that can be used when developing containers to run on elmware.  Unlike a running elmware instance, the sandbox does not wait for user input before returning results back to the container.  As such, it can be used to quickly test.


**Usage**

In order to use the sandbox, a special development sandbox key must be obtained.  Please contact support@elmware.com in order to obtain one.  The development sandbox key is used in place of the instance_key when instantiating the ELMSDK class.  In addition, the dev_mode = True key word argument must be passed.


.. code-block:: python

    from elmsdk import ELMSDK

    elm = ELMSDK(development_sandbox_key, dev_mode = True)
    


**Differences between Sandbox and Production**


There are a few differences between the Sandbox and Production Environments:

``1) Beginning a run``

In production, a run of the container is begun by the user through the UI.  In the sandbox, this behavior is emulated using the ‘setup_dev_run’ method of the ELMSDK class.  This method is passed the func key that is being tested.  After that, the begin_run method can be called normally.

.. code-block:: python

    from elmsdk import ELMSDK

    elm = ELMSDK(development_sandbox_key, dev_mode = True)
    elm.setup_dev_run('report')
    while True:
        elm.begin_run()
        ...


``2) Persistence``

Anything saved using the sandbox has limited persistence.  This can can include writes to the database, file uploads and error logging.  Do not expect anything written during a sandbox session to persist long term.


``3) end_run - continue_run``

When using the sdk in the production environment, passing a continue_run argument to the end_run method will result in the container waiting for the user to input the needed information.  In the development sandbox, the user_input will be returned immediately using default values.  Inputs will return with their value equal to their name.  File uploads will return with an empty link.  The begin_run method will immediately receive the results the next time it is called.


.. code-block:: python

    #when done in the development sandbox
    elm.end_run(message = 'Input data', continue_run={'func':'part2', 'inputs':[{'name':'data1'}, {'name':'data2'}]})
    #this will return as soon as the api request completes. it will not block waiting for user input as it normally does
    status = elm.begin_run()
    print(status['func'])
    # returns 'part2'
    print(status['inputs']['data1'])
    #returns 'data1'


