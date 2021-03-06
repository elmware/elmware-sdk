# -*- coding: utf-8 -
#
from elmsdk.configuration import settings
from elmsdk.utilities.api import APIRequests
from elmsdk.utilities.storage import StoreFile
import time


class ELMSDK:
    def __init__(self, instance_key, url_override=False, dev_mode=False):
        self.instance_key = instance_key
        self.url_override = url_override
        self.dev_mode = dev_mode

    def setup_dev_run(self, func):
        """
        This method must be run before doing a dev move run. Will set up function to be called. Returns True is successful, False if not.  Only used for dev.
        """
        results = APIRequests.post_request(
            "setup_dev_run",
            self.instance_key,
            data={"func": func},
            dev_mode=True,
            url_override=self.url_override,
        )

    def begin_run(self):
        """
        This method must be called at the beginning of every tool run.  It will block until a task is assigned.  Then it will return either a run or a kill task

        returns a dictionary with keys function, inputs, and role
        """
        status = "wait"
        results = {}
        while status == "wait":
            results = APIRequests.get_request(
                "begin_run",
                self.instance_key,
                dev_mode=self.dev_mode,
                url_override=self.url_override,
            )
            status = results.get("state", "wait")
            if status == "wait":
                time.sleep(settings.TASK_WAIT_SLEEP)
        return {
            k: results.get(k, None)
            for k in ["func", "inputs", "role"]
            if results.get(k, None) is not None
        }

    def push_notification(self, message):
        """
        This method can only be called during a cron run.  It will send a message to the user.
        """
        results = APIRequests.post_request(
            "push_notification",
            self.instance_key,
            data={"message": message},
            dev_mode=self.dev_mode,
            url_override=self.url_override,
        )
        return True

    def find_callback_url(self):
        """
        This method returns a callback url that can be used for external webhooks, an email address that will forward to the same webhook, and a retreival key

        returns a dictionary with keys url key, and email
        """
        results = APIRequests.get_request(
            "find_callback_url",
            self.instance_key,
            dev_mode=self.dev_mode,
            url_override=self.url_override,
        )
        return {
            k: results.get(k, None)
            for k in ["url", "key", "email"]
            if results.get(k, None) is not None
        }

    def find_callback_redirect_url(self):
        """
        This method returns a callback url that can be used for external webhooks,  and a retreival key.  In this case, though the callback url will always be the same (/appstash).  The callback must be made by an authenticated user.

        returns a dictionary with keys url & key
        """
        results = APIRequests.get_request(
            "find_callback_redirect_url",
            self.instance_key,
            dev_mode=self.dev_mode,
            url_override=self.url_override,
        )
        return {
            k: results.get(k, None)
            for k in ["url", "key"]
            if results.get(k, None) is not None
        }

    def callback_url_results(self, url_key):
        """
        This method returns a list of requests that have been made to the externally facing url or email address associated with the url_key.  Once this method is called, the store of requests will be emptied.  

        returns a dictionarty with key data
        """
        results = APIRequests.get_request(
            "callback_url_results",
            self.instance_key,
            args={"url_key": url_key},
            dev_mode=self.dev_mode,
            url_override=self.url_override,
        )
        return {
            k: results.get(k, None)
            for k in ["data"]
            if results.get(k, None) is not None
        }

    def db_read(
        self, table_number, query, is_global=False, order_by=False, limit=False
    ):
        """
        This is a method to read from the db.  table number must be an integer.  query must be a list.  is_global determines whether the table is shared between different users of the same tool. limit is the max number of records returned.  order_by, if provided, is a string representing the key that is used in order to determine the sort order of the result. A negative sign as a first character in the string reverses the sort order.  

        returns a list of dictionaries
        """
        results = APIRequests.post_request(
            "db_read",
            self.instance_key,
            data={
                "table": table_number,
                "query": query,
                "is_global": is_global,
                "order_by": order_by,
                "limit": limit,
            },
            dev_mode=self.dev_mode,
            url_override=self.url_override,
        )
        return results.get("data", [])

    def modify_db_state(self, db_creates=[], db_updates=[], db_deletes=[]):
        """
        This is a method to run any sort of db state change operations before the end of the run. all kwargs should be a list of entries.  Returns None
        """
        APIRequests.change_db_state(
            self.instance_key,
            db_creates=db_creates,
            db_updates=db_updates,
            db_deletes=db_deletes,
            dev_mode=self.dev_mode,
            url_override=self.url_override,
        )

    def file_upload(self, path, is_perm=False):
        """
        This method will upload a file to storage.  It returns a key that can be used to retreive the file later.  setting is_perm to true will cause the file to persist indefinitely.  otherwise it is deleted after 24 hours.
        """
        results = APIRequests.get_request(
            "request_file_upload",
            self.instance_key,
            args={"is_perm": is_perm},
            dev_mode=self.dev_mode,
            url_override=self.url_override,
        )
        StoreFile.store_file(results.get("url", ""), path)
        return results.get("file_key", False)

    def del_perm_file(self, file_key):
        """
        This method deletes a file in storage.  It can only be called on permenent files.  It takes the file key as an arg
        """
        results = APIRequests.post_request(
            "del_perm_file",
            self.instance_key,
            data={"file_key": file_key},
            dev_mode=self.dev_mode,
            url_override=self.url_override,
        )
        return True

    def file_download_link(self, file_key, name, is_perm=False):
        """
        This method will return a link that can be used to download a file. The link will expire after an hour. is_perm must be the same value as when the file was uploaded
        """
        results = APIRequests.get_request(
            "file_download_link",
            self.instance_key,
            args={"is_perm": is_perm, "name": name, "file_key": file_key},
            dev_mode=self.dev_mode,
            url_override=self.url_override,
        )
        return results.get("file_link", False)

    def report_error(self, error_message):
        """
        This method will pass an error message to the server, then trigger the shutdown of the container.  Response from the server will be an error coded message.
        """
        APIRequests.post_request(
            "report_error",
            self.instance_key,
            data={"error_message": error_message},
            dev_mode=self.dev_mode,
            url_override=self.url_override,
        )

    def end_run(
        self,
        message="",
        link="",
        continue_run=False,
        db_creates=[],
        db_updates=[],
        db_deletes=[],
    ):
        """
        This method ends the current run.  After it is invoked, the program should then call begin run again.  If error != False, it should be a string, such as a stack trace.  The error will be stored and the message will be returned to the client as an error message.  Any continue_run arguments will be ignored. Returns True if it doesn't error.
        """
        if db_deletes or db_creates or db_updates:
            APIRequests.change_db_state(
                self.instance_key,
                db_creates=db_creates,
                db_updates=db_updates,
                db_deletes=db_deletes,
                dev_mode=self.dev_mode,
                url_override=self.url_override,
            )
        results = APIRequests.post_request(
            "end_run",
            self.instance_key,
            data={"message": message, "link": link, "continue_run": continue_run},
            dev_mode=self.dev_mode,
            url_override=self.url_override,
        )
        return True
