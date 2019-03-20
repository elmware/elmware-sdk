# -*- coding: utf-8 -
#
from configuration import settings
from utilities.api import APIRequests
from utilities.storage import StoreFile
import time




class ElmwareSDK:


    @classmethod
    def setup_dev_run(cls, instance_key, func, url_override=False):
        """
        This method must be run before doing a dev move run. Will set up function to be called. Returns True is successful, False if not.  Only used for dev.
        """
        results = APIRequests.post_request('setup_dev_run', instance_key, data={'func':func}, dev_mode=True, url_override=url_override)
    @classmethod
    def begin_run(cls, instance_key, dev_mode=False, url_override=False):
        """
        This method must be called at the beginning of every tool run.  It will block until a task is assigned.  Then it will return either a run or a kill task

        returns a dictionary with keys function, input, and role
        """
        status = 'wait'
        results = {}
        while status == 'wait':
            results = APIRequests.get_request('begin_run', instance_key, dev_mode=dev_mode, url_override=url_override)
            status = results.get('state', 'wait')
            if status == 'wait':
                time.sleep(settings.TASK_WAIT_SLEEP)
        return {k:results.get(k,None) for k in ['func', 'input', 'role'] if results.get(k, None) is not None}


    @classmethod
    def find_callback_url(cls, instance_key, url_key, dev_mode=False, url_override=False):
        """
        This method returns a callback url that can be used for external webhooks, as well as retreival key

        returns a dictionary with keys url and url_key
        """
        results = APIRequests.get_request('find_callback_url', instance_key, args={'url_key':url_key}, dev_mode=dev_mode, url_override=url_override)
        return {k:results.get(k,None) for k in ['url'] if results.get(k, None) is not None}

    @classmethod
    def callback_url_results(cls, instance_key, url_key, dev_mode=False, url_override=False):
        """
        This method returns a callback url that can be used for external webhooks, as well as retreival key

        returns a dictionarty with key data
        """
        results = APIRequests.get_request('callback_url_results', instance_key, args={'url_key':url_key}, dev_mode=dev_mode, url_override=url_override)
        return {k:results.get(k,None) for k in ['data'] if results.get(k, None) is not None}

    @classmethod
    def db_read(cls, instance_key, table_number, query, is_global=False, dev_mode=False, url_override=False):
        """
        This is a method to read from the db.  table number must be an integer.  query must be a list.  is_global determines whether the table is shared between different users of the same tool

        returns a list of dictionaries
        """
        results = APIRequests.post_request('db_read', instance_key, data={'table':table_number, 'query':query, 'is_global':is_global}, dev_mode=dev_mode, url_override=url_override)
        return results.get('data', [])


    @classmethod
    def file_upload(cls, instance_key, path, dev_mode=False, is_perm=False, url_override=False):
        """
        This method will upload a file to storage.  It returns a key that can be used to retreive the file later.  setting is_perm to true will cause the file to persist indefinitely.  otherwise it is deleted after 24 hours.
        """
        results = APIRequests.get_request('request_file_upload', instance_key, args={'is_perm':is_perm}, dev_mode=dev_mode, url_override=url_override)
        StoreFile.store_file(results.get('url', ''), path)
        return results.get('file_key', False)


    @classmethod
    def file_download_link(cls, instance_key, file_key, name, dev_mode=False, is_perm=False, url_override=False):
        """
        This method will return a link that can be used to download a file. The link will expire after an hour. is_perm must be the same value as when the file was uploaded
        """
        results = APIRequests.get_request('file_download_link', instance_key, args={'is_perm':is_perm, 'name':name, 'file_key':file_key}, dev_mode=dev_mode, url_override=url_override)
        return results.get('file_link', False)

    @classmethod
    def report_error(cls, instance_key, error_message, dev_mode=False,  url_override=False):
        """
        This method will pass an error message to the server, then trigger the shutdown of the container.  Response from the server will be an error coded message.
        """
        APIRequests.post_request('report_error', instance_key, data={'error_message':error_message}, dev_mode=dev_mode, url_override=url_override)


    @classmethod
    def end_run(cls, instance_key, message='', link='', continue_run=False, db_creates=[], db_updates=[], db_deletes=[], dev_mode=False, url_override=False  ):
        """
        This method ends the current run.  After it is invoked, the program should then call begin run again.  If error != False, it should be a string, such as a stack trace.  The error will be stored and the message will be returned to the client as an error message.  Any continue_run arguments will be ignored. Returns True if it doesn't error.
        """
        if db_deletes or db_creates or db_updates:
            APIRequests.post_request('save_data', instance_key, data={'db_creates':db_creates, 'db_updates':db_updates, 'db_deletes':db_deletes}, dev_mode=dev_mode, url_override=url_override) 
        results = APIRequests.post_request('end_run', instance_key, data={'message':message, 'link':link, 'continue_run':continue_run}, dev_mode=dev_mode, url_override=url_override)
        return True



    







