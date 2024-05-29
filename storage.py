

def create_record(table_name, data, supabase):
    """
    Create a new record in the specified table using the provided data.

    Args:
        table_name (str): The name of the table to insert the record into.
        data (dict): The data to be inserted as a new record.
        supabase (SupabaseClient): The Supabase client object.

    Returns:
        None
    """
    response, count = supabase.table(table_name).insert(data).execute()

def read_records(table_name, supabase):
    """
    Read records from the specified table.

    Args:
        table_name (str): The name of the table to read records from.
        supabase (SupabaseClient): The Supabase client object.

    Returns:
        None
    """
    response = supabase.table(table_name).select().execute()
    if response['status_code'] == 200:
        records = response['data']
        for record in records:
            print(record)
    else:
        print('Failed to fetch records.')

def delete_record(table_name, record_id, supabase):
    """
    Delete a record from the specified table based on the record ID.

    Args:
        table_name (str): The name of the table to delete the record from.
        record_id (str): The ID of the record to be deleted.
        supabase (SupabaseClient): The Supabase client object.

    Returns:
        None
    """
    response = supabase.table(table_name).delete().eq('id', record_id).execute()
    if response['status_code'] == 200:
        print('Record deleted successfully.')
    else:
        print('Failed to delete record.')

def create_data(user, product_name, product_description, output, is_create_new):
    """
    Create a data dictionary with the provided parameters.

    Args:
        user (str): The user associated with the data.
        product_name (str): The name of the product.
        input_prompt (str): The input prompt for the product.
        output (str): The output of the product.
        is_create_new (bool): Flag indicating whether to create a new record.

    Returns:
        dict: The data dictionary.
    """
    data = {
        'user': user,
        'product_name': product_name,
        'product_description': product_description,
        'output': output,
        'is_create_new': is_create_new
    }
    return data