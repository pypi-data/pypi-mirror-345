def create_index(db_util, col_name):
    index_create = [('symbol', 1), ('time', 1)]
    db_util.create_index(col_name, index_create)
    index_create_01 = [('time', 1)]
    db_util.create_index(col_name, index_create_01)
    index_create_02 = [('symbol', 1)]
    db_util.create_index(col_name, index_create_02)


