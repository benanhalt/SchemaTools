from . import base
from .conversion import reflect_record, reflect_table, get_primary_key_col, gen_table_uuid, gen_row_uuid, postprocess_record
from .generics import method, next_method

from sqlalchemy import select, Table, Column, ForeignKey, Text, Integer
from sqlalchemy.dialects import postgresql

class Sp6TreeMeta(base.TreeMeta):
    pass

def Sp6Tree(*, treedef_table, treedef_id):
    class TreeMeta(Sp6TreeMeta):
        treedef_table_name = treedef_table
        treedef_id_value = treedef_id

    class Tree(metaclass=TreeMeta):
        pass

    return Tree

@method(reflect_record)
def reflect_sp6tree(tree: Sp6TreeMeta, metadata):
    next_method(reflect_sp6tree, tree, metadata)
    meta = tree.__class__
    meta.treedef_table = reflect_table(meta.treedef_table_name, metadata)

    treedefitem_table_name = meta.treedef_table.name + 'item'
    meta.treedefitem_table = reflect_table(treedefitem_table_name, metadata)

@method(postprocess_record)
def postprocess_sp6tree(tree: Sp6TreeMeta, output_metadata, connection):
    next_method(postprocess_sp6tree, tree, output_metadata, connection)

    meta = tree.__class__
    output_table = output_metadata.tables[tree.output_record._meta.full_name]
    treedefid_col = meta.treedefitem_table.c[get_primary_key_col(meta.treedef_table).name]

    scratch_table = Table(tree.output_record._meta.name + 'ConversionScratch', output_metadata,
        Column('id', postgresql.UUID, nullable=False),
        Column('p_id', postgresql.UUID, nullable=True),
        Column('name', Text, nullable=False),
        Column('rank', Text, nullable=False),
        schema=tree.output_record._meta.schema._meta.name)

    scratch_table.drop(connection, checkfirst=True)
    scratch_table.create(connection)

    query = select([get_primary_key_col(tree.source_table),
                    tree.source_table.c.ParentID,
                    tree.source_table.c.Name,
                    meta.treedefitem_table.c.Name]) \
        .select_from(tree.source_table.join(meta.treedefitem_table)) \
        .where(treedefid_col == meta.treedef_id_value)

    table_uuid = gen_table_uuid(tree.source_table)
    print(table_uuid)

    data = [dict(id = gen_row_uuid(table_uuid, row[0]),
                 p_id = gen_row_uuid(table_uuid, row[1]),
                 name = row[2],
                 rank = row[3])
            for row in query.execute()]

    connection.execute(scratch_table.insert(), data)

    roots = select([scratch_table.c.id,
                    postgresql.hstore(scratch_table.c.rank, scratch_table.c.name) \
                    .label('tree_structure')]) \
            .where(scratch_table.c.p_id == None) \
            .cte(recursive=True)

    node = scratch_table.alias('node')
    nodes = roots.alias('nodes')

    nodes = nodes.union_all(
        select([node.c.id,
                nodes.c.tree_structure + postgresql.hstore(
                    node.c.rank, node.c.name)]) \
        .select_from(node.join(nodes, node.c.p_id == nodes.c.id)))


    query = select([nodes.c.tree_structure]).where(nodes.c.id == output_table.c.uuid)
    update = output_table.update().values(tree_structure=query)
    connection.execute(update)

    scratch_table.drop(connection)
