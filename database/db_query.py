########################################################################
# db_query.py contains functionality to return PC specification data
# from the relevant database tables
########################################################################

# Query database to get PC specification data
def find_pc_recommendations(connection, filters, offset=0):
    sql = """
        SELECT 
            l.*,
            m.*,
            g.*,
            p.*,
            a.*
        FROM listing l
        JOIN model m ON l.model_id = m.model_id
        LEFT JOIN graphics g ON m.graphics_id = g.graphics_id
        LEFT JOIN processor p ON m.processor_id = p.processor_id
        LEFT JOIN laptop a ON m.model_id = a.model_id
        WHERE 1=1
    """

    # Build sql string and generate values list to be used in database query
    values = []
    
    if filters.get("price") is not None:
        sql += " AND l.price <= %s"
        values.append(filters["price"])

    machine_type = filters.get("machine_type")

    if machine_type and machine_type.lower() != "undecided":
        sql += " AND LOWER(m.machine_type) = LOWER(%s)"
        values.append(machine_type)

    if filters.get("ram_gb") is not None:
        sql += " AND m.ram_gb >= %s"
        values.append(filters["ram_gb"])

    if filters.get("graphics_type") is not None:
        gpu_type = filters["graphics_type"]
        sql += " AND g.graphics_type = %s"
        values.append(gpu_type)

    sql += " ORDER BY l.price DESC LIMIT 2 OFFSET %s"
    values.append(offset)

    # Perform database query
    with connection.cursor() as cur:
        cur.execute(sql, values)
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        results = [dict(zip(columns, row)) for row in rows]

    return results

