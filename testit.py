from src.abstract_solcatcher import call_solcatcher_py,call_solcatcher_db
def get_connection():
    return call_solcatcher_db('aggregate_rows').json()['result']
def fetch_filtered_transactions_paginated(
    sol_amount, 
    operator="<", 
    timestamp=None, 
    timestamp_operator=None, 
    limit=50, 
    offset=0
):
    # SQL Query
    query = f"""
    SELECT
        p.*, 
        t.*,
        m.*,
        t2.id AS related_txn
    FROM 
        transactions t
    JOIN 
        pairs p ON t.pair_id = p.id
    LEFT JOIN 
        metadata m ON p.meta_id = m.id
    LEFT JOIN 
        transactions t2 ON t.pair_id = t2.pair_id AND t.signature != t2.signature
    WHERE 
        t.signature IN (
            SELECT signature FROM pairs WHERE signature IS NOT NULL
        )
    AND 
        t.program_id = p.program_id
    AND 
        EXISTS (
            SELECT 1
            FROM jsonb_array_elements(t.tcns) AS elem
            WHERE (elem ->> 'sol_amount')::numeric {operator} %s
    """

    # Parameters for query execution
    params = [sol_amount]

    # Add timestamp filtering if provided
    if timestamp and timestamp_operator:
        query += f" AND (elem ->> 'timestamp')::bigint {timestamp_operator} %s"
        params.append(int(timestamp))

    # Add sorting and pagination
    query += f") ORDER BY t.updated_at DESC LIMIT %s OFFSET %s;"
    params.extend([limit, offset])

    # Database connection and execution
    conn = call_solcatcher_db('aggregate_rows',query=query,values=params,solcatcherSettings={"getResult":True,"getResponse":True})
    return conn
params = call_solcatcher_db('fetch_filtered_transactions_paginated',sol_amount = 10).json()
print({'limit': 50, 'offset': 0, 'operator': '>', 'sol_amount': 10})
input(fetch_filtered_transactions_paginated(**{'limit': 50, 'offset': 0, 'operator': '>', 'sol_amount': 5}))
