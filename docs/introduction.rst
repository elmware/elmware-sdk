Introduction
============

``Overview`` 
    Elmware is a system for allowing users to run and interact directly with containers through a standard UI.  This SDK allows python developers to build applications within a docker container that are able to run on Elmware. While there is no firm requirement that applications running on Elmware are written in python, it is currently the only SDK that we provide.


**Application Structure**


``Building a Container``
    In order to build a container able to run on Elmware, the Elmware SDK must be installed using pip **in the dockerfile**.  This ensures that changes to the SDK can be incorporated into the container by rebuilding it. Ex: 
    ``RUN pip install elmsdk``


``Container Resources``
    The container will have access to a number of system resources that it can use with no configuration.  The first is a schemaless database that takes json objects. The database provides and arbitrary number of tables to each container that can be separated by user or span multiple users (for common data sets).

    The second resource is static file storage and retrieval.  The container can store files from its local file system.  It can also access retrieval urls for these files that it can use itself or pass to the user.

    The third resource is externally facing http endpoints.  These can be used to receive incoming webhooks.

    Finally, the container is able to access user input in between runs.




``Container Lifecycle``
    When a user loads a tool associated with a given container, an instance of the container will be loaded.  The container will be passed an instance key at load time via a shell command.  The exact shell command structure can be specified when the container is pushed to elmware.  Typically it will be of the format ``"/usr/local/bin/appstart.sh <instance_key>"``  This instance key is used by the SDK to access the server. Once the container is loaded, the application should instanciate the SDK.  A typical python script doing this would look like:

.. code-block:: python

    from elmsdk import ELMSDK

    elm = ELMSDK(instance_key)
    while True:
        staus = elm.begin_run()
        “””
        do some things
        “””
        elm.end_run(message=”job done”)

The begin_run method will block until a task has come in to the container from the user.  It will then return information about the task the container should perform. The job of the container is to run the job and report back when done using the end_run method.  It should then repeat the cycle again until shut down. More information about the sdk methods can be found in the methods documentation.

``Stateless Containers``
    Containers in Elmware are stateless.  But are often able to perform many different functions.  To deal with this, they are passed a ‘func’ argument from the begin_run method.  This represents the current task that the container should be working on. 

    At some points, input from the user might be required to continue the task.  At this point, the end_run method is called.  It can be passed arguments detailing what input is needed from the user, and what func string should be passed to begin_run after that information has been provided.  

A typical workflow might look like this:

``1)``
A user starts a reporting app on elmware, that pulls data out of a remote database and returns that data to the user.

``2)``
A container is started up with instance key ‘abcde’. It calls a python script calls run.py with the instance key.  The python script instantiates the elmware sdk with the instance key and calls the begin_run method.

``3)``
The begin run method returns the func ‘start’

``4)``
The script runs its start function, which calls end_run.  Arguments are passed to end_run specifying what information is needed from the user, as well as what func should be called after the user has provided the information. In this case, we will say the next func should be ‘gen_report’. The python script then calls begin_run again, which will block until the user has provided the desired information.

``5)``
The user inputs the information. 

``6)``
The begin_run function then returns the information the users provided as well as func = ‘gen_report’.  The python script runs its gen_report function and returns the results to the user.  

An example of this can be seen in the sample_financial_report_app documentation