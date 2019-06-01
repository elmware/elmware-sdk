

SAMPLE APP
==========

This is a sample elmware container that for a non-existant financial reporting app.  It pulls information out of a hypothetical ERP system and puts the results into a spreadsheet.  It has 2 entrpoints from the normal UI,  ``func = 'collect_report_information'`` and ``func = 'get_instructions'``.  In addition, it has one admin only entrypoint ``func='set_instructions_getter'``



``appstart``

entrypoint - /usr/local/bin/appstart.sh

This will be called via the command line when the container starts.  It will be passed a single argument representing the instance key.  The entrypoint to call is entered into elmware when you upload your container.




.. code-block:: bash

    #!/bin/bash
    python3 /usr/local/bin/mainApp.py $1




``mainApp``

This is the primary python app.  


.. code-block:: bash

    import sys
    from elmsdk import ELMSDK
    import traceback
    import urllib.request
    import erp_module
    import json
    import pandas as pd


    #this is a function that can be called by the user directly.  It lets the user download the current version of the instruction manual if it exists.  If not, it will return a message stating that there is no instruction manual available
    def get_instructions(elm):
        """
        there will only be 1 instruction manual available to all users using this container. so the key should be stored in a global db.  This function will return to the user a link to the manual or a message saying it doesnt exist
        """
        key_check = elm.db_read(1, ['name', 'eq', 'instruction_key'], is_global=True)
        if not key_check:
            return elm.end_run(message="No instruction manual has been uploaded.")
        link = elm.elm.file_download_link(key_check[0]['key'], 'instructions.docx', is_perm=True)
        return elm.end_run(link=link)


    #set instructions is an admin level function.  The permissions will be set when uploading the container to limit it to an admin user.
    # the set instructions function has two parts.  The first part gets the file uploaded from the user.  the second will set that file as the default instruction manual in the db.

    def set_instructions_getter(elm):
        """
        This is the getter function to set the instruction manual. It returns a request for input from the user asking them to upload the instruction manual
        """
        continue_run = {'func':'set_instructions_setter', 'file_upload':True}
        return elm.end_run(message = 'Please select the instruction manual file you would like to upload.', continue_run=continue_run)


    def set_instructions_setter(elm, status):
        """
        This is the setter function to set the instruction manual. It returns a message to the user stating the the upload was successful.  If no file was uploaded, it will invoke the getter function again.
        """
        link_key = status['input'].get('file_upload', '')
        if not link_key:
            return set_instructions_getter(elm)
        link = elm.file_download_link(link_key, 'file')
        #download the file from the link the user provided
        response = urllib.request.urlopen(link)
        path = '/tmp/temp_file'
        with open(path, 'wb') as w:
            w.write(response.read())
        #upload the file to static storage
        key = elm.file_upload(path, is_perm=True)
        #create a record of the file in the db table 1.  is_global since this should be acessible to all users
        creates = []
        updates = []
        query = ['name', 'eq', 'instruction_key']
        key_check = elm.db_read(1, query, is_global=True)
        if not key_check:
            creates.append({'table':1, 'is_global':True, 'data':{'key':key, 'name':'instruction_key'})
        else:
            elm.del_perm_file(key_check[0]['key'])
            updates.append({'table':1, 'is_global':True, 'query':query, 'updates':{'key':key}})
        elm.end_run(message = 'The instruction manual has been added!', db_creates=creates, db_updates=updates)


    def parse_endpoint_data(key, token_check, db_creates, db_updates):
        data = elm.callback_url_results(key)['data']
        if not data:
            return False
        data = data[-1]
        token = data['form_data'].get('token', False)
        if not token:
            return False
        if not erp_module.check_access(token):
            return False
        if token_check:
            query = ['name', 'eq', 'oauth_token']
            db_updates.append({'table':1, 'query':query, 'update':{'token':token}})
        else:
            db_creates.append({'table':1, 'data':{'token':token, 'name':'oauth_token'}})
        return True




    def collect_report_information(elm):
        """
        This function will check if there is an oauth token present for the erp.  if yes, it will return and ask the user for report details.  if not, it will send the user through the oauth process for the erp before calling itself again
        """
        db_creates = []
        db_updates = []
        oauth_ready = False
        token_query = ['name', 'eq', 'oauth_token']
        token_check = elm.db_read(1, token_query)
        endpoint_query = ['name', 'eq', 'oauth_endpoint']
        endpoint_check = elm.db_read(1, endpoint_query)

        #check if already have a working oauth token
        if token_check and erp_module.check_access(token_check[0]['token']):
            oauth_ready = True

        #check if a token has already been sent to one of our endpoints. if so, save if for future use
        elif endpoint_check and parse_endpoint_data(endpoint_check[0]['endpoint_key'], token_check, db_creates, db_updates):
            oauth_ready = True
        #if system doesn't have a working oauth token,  it needs to redirect the user to the erp system's oauth startpoint.  it needs to include a callback url that the users will be sent to.
        if not oauth_ready:
            callback_url = elm.find_callback_url()
            if endpoint_check:
                db_updates.append({'table':1, 'query':endpoint_query, 'update':{'endpoint_key':callback_url['key']}})
            else:
                db_creates.append({'table':1, 'data':{'name': 'oauth_endpoint', 'endpoint_key':callback_url['key']}})
            link = erp_module.get_oauth_link(callback = callback_url['url'])
            return elm.end_run(link = link, db_creates=creates, db_updates=updates)
        else:
            inputs = [
                {'name':'report',
                 ‘options’: [[‘agg_fin’, ‘Aggregate Financial Summary’], [‘ytds’, ‘Year To Date Sales’], [‘acc_p’, ‘Accounts Payable’]]
                 },
                 {'name':'department'},
            ]
            return elm.end_run(message = 'Please input the following information in order to generate your report. Department is optional.', db_creates=creates, db_updates=updates, continue_run = {'inputs':inputs, 'func':'generate_report'})


    def generate_report(elm, status):
        report = status['inputs']['report']
        token_query = ['name', 'eq', 'oauth_token']
        token_check = elm.db_read(1, token_query)
        if not (token_check and erp_module.check_access(token_check[0]['token'])):
            return elm.end_run(message = 'Your access to the ERP system has expired.  Please run this tool again.')
        token = token_check[0]['token']
        department = False
        if status['inputs']['department'] != '':
            department = status['inputs']['department']
        path = '/tmp/report.json'
        xcel_path = '/tmp/report.xlsx'
        with open(path, 'wb') as w:
            if report == 'agg_fin':
                w.write(erp_module.load_aggregate_data(token, department))
            if report == 'ytds':
                w.write(erp_module.load_year_to_date_sales_data(token, department))
            if report == 'acc_p':
                w.write(data = erp_module.load_accounts_payable_data(token, department))
        dataframe = pd.read_json(path_or_buf = path)
        writer = pd.ExcelWriter(xcel_path, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
        key = elm.file_upload(xcel_path)
        link = elm.file_download_link(key, 'report.xlsx')
        return elm.end_run(message = 'Your report has been generated. Your download will begin shortly.', link=link)

















    

    def main_loop(instance_key):
        elm = ELMSDK(instance_key)
        while True:
            try:
                staus = elm.begin_run()
                if status['func'] == 'get_instructions':
                    get_instructions(elm)
                elif status['func'] == 'set_instructions_getter':
                    set_instructions_getter(elm)
                elif status['func'] == 'set_instructions_setter':
                    set_instructions_setter(elm, status)
                elif status['func'] == 'collect_report_information':
                    collect_report_information(elm)
                elif status['func'] == 'generate_report':
                    generate_report(elm, status)
                else:
                    break


            except Exception as e:
                error_message = ''.join(traceback.extract_stack().format())
                error_message += repr(e)
                elm.report_error(error_message)
                break

    if __name__ == '__main__':
        main_loop(sys.argv[1])
