Methods
=======

``The SDK Usage`` 
The elmware sdk is the main way that the application will communicate with the server, and receive instructions.  Typically once instanciated, the application runs an outer python loop as shown in the example below:

.. code-block:: python

    from elmsdk import ELMSDK

    elm = ELMSDK(instance_key)
    while True:
        staus = elm.begin_run()
        “””
        do some things
        “””
        elm.end_run(message=”job done”)

within this loop, calls to all the business logic of the app should be performed.

``class and methods``

**ELMSDK class**

``arguments``

instance_key – str – a string representation of the instance key passed to the container at startup.  This is used to communicate with the server

``key word arguments``

dev_mode – bool – default : False – Indicates whether the container is in development mode

url_override – bool/str – default : False – An alternate root url that the sdk can use for api calls. 

``usage``

The ELMSDK class is instantiated with the instance_key as an argument, and two key word arguments that default to False. dev_mod and url_override. 

.. code-block:: python

    from elmsdk import ELMSDK

    elm = ELMSDK(instance_key, url_override=False , dev_mode=False)
    

The instance key is passed to the docker container on startup.  

dev_mode=True is used for testing purposes.  This will cause the server to immediately return responses to the container rather than waiting for the client. A dev instance_key (provided after dev application process) should be used in place of the normal instance key during testing.  Note that any information passed to the server while in dev mode is kept in a sandbox, and is not available during non-dev runs.

url_override is used to pass a different base url other than the default ``”https://www.elmware.com”``.  This should not be used under normal circumstances.



**setup_dev_run**

``arguments`` 

func – str – a string representing the function called by the user

``output``

None

``usage``

This is a method used only in dev mode.  It will simulate an instantiation of a new docker container.  This should **only** be used in dev mode.  It must be called before the start_run method when doing development testing. 

.. code-block:: python

    “””
    a simulated run while in dev mode
    “””
    from elmsdk import ELMSDK

    elm = ELMSDK(dev_instance_key, dev_mode=True)
    elm.setup_dev_run(‘main’)
    status = elm.begin_run()
    “””
    do some things
    “””
    elm.end_run(message=”job done”)

The only argument that setup_dev_run takes is func.  This is a string representation of the func that the container should be performing.  Normally this would be supplied by the user, but in development mode, this must be supplied prior to beginning the normal run process.


    
**begin_run**

``arguments``

None

``Output``

{‘func’:str, ‘inputs’:dict, ‘role’:str}

func – A string representation of the function that the container should run. The next function to be run is specified at the end of the run using the end_run method.  NOTE: If func is returned as an empty string (func == ‘’), this means that the container is being shut down. *However*, it is not advisable to have any sort of required break-down or cleanup procedure that runs when this happens.  This is because, when the empty string is returned, a separate command is issued at the system level to shut down the container.  There is no guarantee that any sort of cleanup procedure will finish before the container shutdown occurs. 

inputs – A dictionary of keys and values.  Desired user inputs for the next run are specified at the end of the run using the end_run method.  If a file was uploaded by the user, this dictionary will contain a ‘file_upload’ key.  The value will be a dictionary with two keys. The first one, 'key', can be used to generate a download link using the file_download_link method, and 'name', representing the original file name.

role – A string representation of the role the container is currently functioning under.  Typically these will either be ‘primary’ or ‘cron’.  Primary means the container is currently being run by a user.  Cron means that the container has been triggered by a cron job, and has no active user.  

``Usage``

This method is called at the beginning of each run.  It will block until a task comes in from the user.  Then it will return details about the run.  After the end_run method is called at the end of the run, the begin_run method should be immediately called again.  If the end_run method specified a certain function or inputs that should be provided on the next run, they will be received by the begin_run method once the user has entered them.

`EX:`

.. code-block:: python

    from elmsdk import ELMSDK

    elm = ELMSDK(instance_key)
    while True:
        staus = elm.begin_run()
        if status['func'] == '':
            break
        elif status['func'] == 'run':
            target = status['inputs']['target']
            “””
            do some things
            “””
        elm.end_run(message=”job done”)






**find_callback_url**


``arguments``

None

``Output``

{‘url’:str, ‘key’:str, 'email':str}

url – This is a externally facing URL that is able to request incoming web traffic.  It can be used to process callbacks. Requests sent to it will be accessible to the app by using the key

key – This is a key that can be used to access the last request made to the related url.  It should be stored for later use.

email - This is an externally facing email address.  Email sent to it will be accessible to the app using the key. This does not work in test mode.


``Usage``

This method is used to find a callback url that can be used for webhooks from external resources.  For example, the oauth process requires an incoming request from an external source. Using this method, a container is able to open up an external url to incoming traffic, and then later access details of the latest request that was made to that url.  It is also able to accept incoming email messages at the address returned. NOTE: The email address only works in production, not in test mode.


`EX:`

.. code-block:: python

    from elmsdk import ELMSDK

    elm = ELMSDK(instance_key)
    url_info = elm.find_callback_url()
    some_function_to_send_to_external_resource(url_info['url'])
    some_function_to_store_the_retreival_key(url_info['key'])



**callback_url_results**


``arguments``

url_key – str – a key obtained from a previous call to the ‘find_callback_url’ method.

``Output``

{‘data’:list}

data – This is a list of dictionaries, representing, in chronological order, the data contained in the requests made to the callback_url or email address linked to the url_key.  If no request has been made in the last 24 hours, data will be an empty string. Once this data has been accessed once, it will be deleted from the server. 



``Usage``

This method is used to retrieve the data contained in requests made to the externally facing endpoints exposed using the ‘find_callback_url’ method.  NOTE: Request data is only stored for 24 hours.  Accessing it once will delete it on the server.  So this method should be called only once per run and the results stored if important



`EX:`

.. code-block:: python

    from elmsdk import ELMSDK

    elm = ELMSDK(instance_key)
    url_key = some_retreival_function()
    webhook_results = elm.callback_url_results(url_key)
    if webhook_results['data']:
        hook_data = webhook_results['data']
        do_something_with_data(hook_data)




Database Operations
===================


``elmware standard query format``
Elmware allows you to query your container’s db using the following format

[key, operation, value]

the allowed operations are:

‘eq’ = Equal to

‘neq’ = not equal to

‘in’ = is in (the value must be a list)

‘nin’ = is not in (the value must be a list)

‘gt’ = greater than

‘lt’ = less than

‘and’ = combines two other queries using and ‘AND’ operator

‘or’ = combines two other queries using an ‘OR’ operator.


``EX``

.. code-block:: python

    #searches for records where name == 'bob'
    query1 = ['name', 'eq', 'bob']

    #searches for records where age is greater than 20
    query2 = ['age', 'gt', 20]

    #searches for records where name == 'bob' and age is greater than 20
    queryA = [query1, 'and', query2]

    #search for records where job is in the list ['baker', 'butcher', 'miller']
    query3 = ['job', 'in', ['baker', 'butcher', 'miller']]

    #search for records where (name =='bob' AND age >20) OR job in the list ['baker', 'butcher', 'miller']  
    queryO = [queryA, 'or', query3]



**db_read**


``arguments``

table_number -int – The integer representing which table you want to query.

query – list – A database query structured in the elmware standard query format.  To search for 'all', and empty list should be provided

 ``key word arguments``

is_global -bool (default = False) – If this is set to True, the query will be performed on a cross installation database (ie for all users using this container)  If False, it will be performed on the database used by this user only.

order_by -str (default = False) - If this is set to a string, the results returned will be ordered by that key field. Results that do not have that key field will be excluded. A minus sign as the first charcter in the string indicates a reversal of order.  For example, if the query was elm.db_read(1, [], order_by='-age') might return [{'name':'john', 'age':10},  {'name':'bill', 'age':5}] 

limit - int (default = False) - The maximum number of results to be returned


``Output``

query_results - list

This is a list of dictionaries representing the results of the query.



``Usage``

This method is used to retrieve data from the elmware database assigned to this container.  If is_global is false, it will only query data for this specific user.  If not, it will query for data across all installations of this container.



``EX``

.. code-block:: python

    from elmsdk import ELMSDK

    elm = ELMSDK(instance_key)
    data = elm.db_read(1, ['name', 'eq', 'bob'], limit=3)
    for d in data:
        do_something(d)



**modify_db_state**



 ``key word arguments``

db_creates – list (default = []) - This is a list of entries into the database for the container.  To avoid race conditions, all db operations that change state should ideally be performed at the end of the run (except in cases where order of operations is important).  Each entry should be of the format {‘table’:int, is_global:bool, data: dict} where table represents the table you want to insert into, is_global is a boolean that determines whether the data written into the table will be readable by other users of the same container (defaults to False) and data is the data you want to insert.  Data must be a json serializable dictionary.

db_updates – list (default= []) This is a list of updates to preform on the container’s database.  To avoid race conditions, all db operations that change state should ideally be performed at the end of the run (except in cases where order of operations is important).  Each entry should be of the format {‘table’:int, is_global:bool, update: dict, query:list} where table represents the table you want to insert into,  , is_global is a boolean that determines whether the data written into the table will be readable by other users of the same container (defaults to False), update is a dictionary representing updates you want to make to the object, and query is a list in the elmware standard query format representing which objects should be updated.

db_deletes – list (default = []) This is a list of deletions that should be made on the container’s database.   To avoid race conditions, all db operations that change state should ideally be performed at the end of the run (except in cases where order of operations is important).  Each entry should be of the format {‘table’:int, is_global:bool,  query:list} where table represents the table you want to delete objects from,  , is_global is a boolean that determines whether the data written into the table will be readable by other users of the same container (defaults to False),  and query is a list in the elmware standard query format representing which objects should be deleted.


``Output``

None


``Usage``

*WARNING* The elmware database is eventually consistent.  This method should only be used in cases where the order of operations is important (ex if you need to make sure deletes happen before creates), or in cases where there is too much data to hold in memory until the end of the run.  Otherwise, it is usually better to pass all operations that change the state of the db to the end_run method.  

This method is used to modify the state of the database.  It can be passed lists of create, update, and delete operations that will be applied to the database.  These should be structured using the same format as the data passed to the end_run method.   The order of operations cannot be guaranteed. 



``EX``

.. code-block:: python

    from elmsdk import ELMSDK

    elm = ELMSDK(instance_key)
    elm.modify_db_state (db_creates=[{'table':1, 'is_global':False, 'data':{'name':'bob'}}])



**file_upload**


``arguments``

path -str – The full system path of the file you want to upload


``key word arguments``

is_perm -bool (default = False) – If this is set to True, the file you upload will persist in storage indefinitely.  If False, it will be deleted in 24 hours. 


``Output``

str or bool

This is a string that can be used to retrieve the uploaded file. It returns False if the upload failed.



``Usage``

This method is used to upload a file to storage.  It can also be used in conjunction with the file_download_link method to pass a file to a user.  Once the file is uploaded with this method, the file_download_link method can be used to generate a link.  The link can then be passed to the user at the end of the run.




``EX``

.. code-block:: python

    from elmsdk import ELMSDK

    elm = ELMSDK(instance_key)
    f = open('new_file', 'w')
    f.write('some data')
    f.close()
    key = elm.file_upload(f.name)
    some_function_to_store_the_key(key)




**file_download_link**


``arguments``

file_key -str – This is the key that was provided by the file_upload method when this file was uploaded

name -str - Tihs will be the name of the file that is downloaded.


``key word arguments``

is_perm -bool (default = False) – This determines which storage bucket to pull the file from.  It must be the same value as was used when uploading the file.


``Output``

str or bool

 This returns a url that can be used to download the file.  It requires no authentication, but the link is only valid for 100 seconds.  It can be downloaded locally, or passed to the user. It returns False if the link doesn't exist.



``Usage``

This is the primary method of retrieving static files that were stored earlier with the upload_file method.  Using the link, the file can be downloaded to the container using curl or another http request method.  It is also the primary method used for passing files to the user.  At the end of the run, the results of this method can be passed to the user using the ‘link’ kwarg in end_run.  This will cause the user to download the file. 




``EX``

.. code-block:: python

    from elmsdk import ELMSDK
    import urllib.request

    elm = ELMSDK(instance_key)
    key =some_function_to_retreive a previous_file_key()
    url = elm.file_download_link(key, 'myfile.txt')
    response = urllib.request.urlopen(url)
    data = response.read()


**del_perm_file**


``arguments``

file_key -str – This is the key that was provided by the file_upload method when this file was uploaded



``key word arguments``
 
 None

``Output``

True



``Usage``

This is used to delete an existing permanent file.   




``EX``

.. code-block:: python

    from elmsdk import ELMSDK
    import urllib.request

    elm = ELMSDK(instance_key)
    key =some_function_to_retreive a previous_file_key()
    elm.del_perm_file(key)
    




**report_error**


``arguments``

error_message -str – This is any information you want to save from the error.  A stacktrace is often used here.



``Output``

None



``Usage``

This method should be called if an error occurs during execution of code in the container.  This will report the error to the server, inform the user that an error has occurred, log the error message, and shut down the container.  Lower level error handling is left up to the container.  Errors that bubble to the top and are not caught will not trigger this method.  This method MUST be called explicitly in those cases.  It is advised to wrap your code in a top level try/except block with this method called after except.




.. code-block:: python

    from elmsdk import ELMSDK
    import traceback

    elm = ELMSDK(instance_key)
    while True:
        staus = elm.begin_run()
        try:
            some_main_task_function()
        except Exception as e:
            error_message = ''.join(traceback.extract_stack().format())
            error_message += repr(e)
            elm.report_error(error_message)
            break
        elm.end_run(message=”job done”)




**end_run**


``arguments``

None

``key word arguments``

message -string (default = ‘’) – This is the message passed to the user at the end of the run.
  
link -string (default = ‘’) – If a value other than empty string is entered here, the user will be directed to this link after the run ends.  If it is a download link, the user will automatically download the file.

continue_run – dict/bool (default=False) – If this value is False, the run will end after the results are returned to the user.  If a dictionary, the user will be prompted to input the fields defined in the dictionary.  The results will then be fed back to the process next time the start_run method is called. More info can be found below.

db_creates – list (default = []) - This is a list of entries into the database for the container.  To avoid race conditions, all db operations that change state should ideally be performed at the end of the run (except in cases where order of operations is important).  Each entry should be of the format {‘table’:int, is_global:bool, data: dict} where table represents the table you want to insert into, is_global is a boolean that determines whether the data written into the table will be readable by other users of the same container (defaults to False) and data is the data you want to insert.  Data must be a json serializable dictionary.

db_updates – list (default= []) This is a list of updates to preform on the container’s database.  To avoid race conditions, all db operations that change state should ideally be performed at the end of the run (except in cases where order of operations is important).  Each entry should be of the format {‘table’:int, is_global:bool, update: dict, query:list} where table represents the table you want to insert into,  , is_global is a boolean that determines whether the data written into the table will be readable by other users of the same container (defaults to False), update is a dictionary representing updates you want to make to the object, and query is a list in the elmware standard query format representing which objects should be updated.

db_deletes – list (default = []) This is a list of deletions that should be made on the container’s database.   To avoid race conditions, all db operations that change state should ideally be performed at the end of the run (except in cases where order of operations is important).  Each entry should be of the format {‘table’:int, is_global:bool,  query:list} where table represents the table you want to delete objects from,  , is_global is a boolean that determines whether the data written into the table will be readable by other users of the same container (defaults to False),  and query is a list in the elmware standard query format representing which objects should be deleted.


``continue run additional info``

The continue_run dict needs to be of the format {‘func’:str ,  ‘file_upload’:bool,  inputs: list}
This will determine what is passed to the begin_run function after the user input is gathered.

func – str – this is the name of the func that will be passed to begin_run after the user submits input.   

file_upload – bool – If this is True, the user will be prompted to upload a file before the next run.

inputs – list – this is a list of inputs required from the user before the next run.  Each input should be a dictionary of one of two formats

1) {‘name’:name, 'display_name':display_name} – this will display to the user as a free form text entry field.  The text entry from the user will be returned to the begin_run method with key = name.  The display_name field is optional.  If set, the user will see the display name rather than the actual name of the field.

2) {‘name’:name, 'display_name':display_name, ‘options’: [[‘value1’, ‘display1’], [‘value2’, ‘display2’]]} - This will display to the user as a select field.  The user will have to choose between the different options.  They will see the second value in each list (the display value), however the begin_run method will receive the first value in each list if it is selected.  The display_name field is optional.  If set, the user will see the display name rather than the actual name of the field.



 


``Output``

True



``Usage``

This method must be called at the end of a run.  It contains all the information that needs to be passed to the use, all information that should be persisted in the database, and all information pertaining to the next run, including what information the user must supply.  In many cases, one ‘run’ from the users perspective actually consists of many runs for the container.  In between each, the end_run method is called with inputs needed from the user, and the func that should be called after the user has provided the desired input.




.. code-block:: python

    #example 1 - a simple process that runs one operation and returns a message to the user

    from elmsdk import ELMSDK

    elm = ELMSDK(instance_key)
    while True:
        staus = elm.begin_run()
        if status['func'] != '':
            some_main_task_function()
        else:
            break
        elm.end_run(message=”job done”)


    #example 2 - a two part function that asks first for input from a user about their vehicle, then enters that infromation into the database or updates an existing record. When uploading this container, the initial func entrypoint for this operation will be defined as 'first'

    from elmsdk import ELMSDK

    elm = ELMSDK(instance_key)
    while True:
        staus = elm.begin_run()
        if status['func'] == '':
            break
        elif status['func'] == 'first':
            inputs = []
            inputs.append({
                'name':'vehicle'
            })
            inputs.append({
                'name':'color'
                'options': [
                    ['red','Red']
                    ['green', 'Green']
                    ['black', Black]
                ]
            })
            elm.end_run(message = 'Please input the following information about your vehicle', continue_run = {'func':'second', 'inputs':inputs})
        elif status['func'] == 'second':
            updates = []
            creates = []
            update = {'color': status['inputs']['color']}
            query = ['vehicle', 'eq', v]
            v = status['inputs']['vehicle']
            data_ob = elm.db_read(1, query)
            if data_ob:
                updates.append({'table':1, 'query':query, 'is_global':False, 'update':update })
            else:
                to_add = {'vehicle':v}
                to_add.update(update)
                creates.append({'table':1, 'is_global':False, 'data':to_add})
            elm.end_run(message = 'Your vehicle information has been saved', db_updates = updates, db_creates = creates)
        









    


    





