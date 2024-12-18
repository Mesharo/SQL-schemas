def test_dict_str_format() -> str:
    f = open('C:\\Users\\Hecko\\Desktop\\tmp.txt', 'a', encoding='utf8')
    id = '5'
    body = 'Hello world'
    mydict = {
        'id': id,
        'body': body
    }
    f.write(str(mydict) + '\n')
    f.close()

    f = open('C:\\Users\\Hecko\\Desktop\\xd.txt', 'r', encoding='utf8')
    mystr = f.readline()
    f.close()
    return mystr

def test_dict_tuple_key() -> None:
    tmp = [('5', 'Hello'), ('3', 'World'), ('4', 'Anything')]
    result = {}

    for tuple_key in tmp:
        result[tuple_key] = [tuple_key[0]]

    id = '3'

    for key in tmp:
        print(key)
        if key[0] == id:
            print('Match')
        else:
            print('No match')

    print(result)
    print(type(result))

def wtha():
    with open('D:\\all_answers.txt', 'r', encoding='utf8') as f:
        for row in f:
            row_tmp = eval(row)
            if row_tmp['id'] == '4416':
                print(row)

def testing():
    with open('C:\\Users\\Hecko\\Desktop\\tmp.txt', 'w', encoding='utf8') as output_fule:
        output_fule.write(str(('1', 'Hello1')) + '\n')
        output_fule.write(str(('2', 'Hello2')) + '\n')
        output_fule.write(str(('2', 'Hello3')) + '\n')
        output_fule.write(str(('1', 'Hello4')) + '\n')
        output_fule.write(str(('2', 'Hello5')) + '\n')

    result = {}
    with open('C:\\Users\\Hecko\\Desktop\\tmp.txt', 'r', encoding='utf8') as input_fule:
        row = input_fule.readline()
        current = eval(row)[1]
        while row:
            if (eval(row)[0] == '1'):
                current = eval(row)[1]
                result[current] = []
            else:
                result[current].append(eval(row))
            row = input_fule.readline()
    
    print(result)

def testing2():
    questions = [('1', 'hello', 'yush')]
    mydict = {
        ('1', '2'): "any",
        ('2', '3'): "any2",
        ('3', '4'): "any3",
        ('4', '5'): "any4",
        ('5', '6'): "any5",
    }

    print(mydict)

    mydict = dict(zip(questions, mydict.values()))

    print(mydict)

import sqlglot.expressions
import sqlglot.optimizer.scope
import sqlparse
def erasing_backslashes():
    xd = """SELECT \\\'ALTER TABLE "\\\'||nspname||\\\'"."\\\'||relname||\\\'" DROP CONSTRAINT "\\\'||conname||\\\'";\\\'
    FROM pg_constraint
    INNER JOIN pg_class ON conrelid=pg_class.oid
    INNER JOIN pg_namespace ON pg_namespace.oid=pg_class.relnamespace
    ORDER BY CASE WHEN contype=\\\'f\\\' THEN 0 ELSE 1 END,contype,nspname,relname,conname
    SELECT \\\'ALTER TABLE "\\\'||nspname||\\\'"."\\\'||relname||\\\'" ADD CONSTRAINT "\\\'||conname||\\\'" \\\'|| pg_get_constraintdef(pg_constraint.oid)||\\\';\\\'   
    FROM pg_constraint
    INNER JOIN pg_class ON conrelid=pg_class.oid
    INNER JOIN pg_namespace ON pg_namespace.oid=pg_class.relnamespace
    ORDER BY CASE WHEN contype=\\\'f\\\' THEN 0 ELSE 1 END DESC,contype DESC,nspname DESC,relname DESC,conname DESC;"""
    
    #xd = xd.replace('\\\'', '\'')
    xd2 = sqlparse.split(xd)
        
    for x in xd2:
        parsed = sqlparse.parse(x)
        for statement in parsed:
            print(f'Statement: {statement}')
            print('Tokens: ')
            for token in statement.tokens:
                print(f'    - {token}')

from sql_metadata import Parser
def sqlmetadata():
    try:
        print(Parser('TABLE hello').tables)
    except ValueError:
        print('Disgustingly dumb user')
    print(Parser("SELECT a, b + 1 AS c FROM d").columns_aliases)

    print('--- NEXT ---')

    print(Parser("CREATE TABLE cars (brand VARCHAR(255),model VARCHAR(255),year INT);").tables)
    print(Parser("CREATE TABLE cars (brand VARCHAR(255),model VARCHAR(255),year INT);").columns)

import sqlglot
import sqlglot.optimizer
import sqlglot.optimizer.qualify
from sqlglot import exp
def sqlglottry():
    for column in sqlglot.parse_one("""
insert into EscapeTest (text) values (E'This is the first part 
 And this is the second');
 insert into EscapeTest (text) values (E'This is the first part 
 And this is the second');
""").find_all(sqlglot.exp.Table):
        print(column.alias_or_name)
    
    print('--- NEXT ---')

    statement = "CREATE TABLE cars (brand VARCHAR(255),model VARCHAR(255),year INT);"
    for column in sqlglot.parse_one(statement, dialect="postgres").find_all(sqlglot.exp.Column):
        print(column.alias_or_name)

import copy
def tmp():
    expression_tree = sqlglot.parse_one("""
                                        SELECT
                                        a,
                                        c
                                        FROM (
                                        SELECT
                                            a,
                                            b
                                        FROM x
                                        ) AS x
                                        JOIN (
                                        SELECT
                                            b,
                                            c
                                        FROM y
                                        ) AS y
                                        ON x.b = y.b
                                        """,
                                        dialect="postgres")

    solved = False
    try:
        undo = copy.deepcopy(expression_tree)
        sqlglot.optimizer.qualify.qualify(expression_tree)

        root = sqlglot.optimizer.build_scope(expression_tree)
        for column in sqlglot.optimizer.find_all_in_scope(root.expression, sqlglot.exp.Column):
            print(f"{column} => {root.sources[column.table]}")

        solved = True
    except sqlglot.errors.OptimizeError:
        expression_tree = undo

def solve_schema(schema: str) -> list:
    pass

def solve_subquery(subquery: str) -> list:
    # Rekurze - ast
    pass

def whatever():
    #expr = "SELECT hello FROM a INNER JOIN b;"
    expr = 'SELECT xd, (SELECT a FROM b) FROM c;'
    #expr = "INSERT INTO first(xdd, xdd2) VALUES((SELECT x FROM third), 1);"
    #expr = """WITH x AS (SELECT a FROM y) SELECT a FROM x"""
    try:
        expression_tree = sqlglot.parse(expr)
        print(repr(expression_tree))
                
        for ast in expression_tree:
            """
            tmp = list(ast.find_all(sqlglot.exp.Schema))
            for column in tmp:
                print(column)  

            tmp = list(ast.find_all(sqlglot.exp.Column))
            for column in tmp:
                columns.append(str(column))            

            tmp = list(ast.find_all(sqlglot.exp.Table))
            for table in tmp:
                tables.append(str(table))

            tmp = list(ast.find_all(sqlglot.exp.Alias))
            for alias in tmp:
                aliases.append(str(alias))"""
            
            walk = []
            sub_result = []
            
            tmp = list(ast.find_all(sqlglot.exp.Schema))
            for schema in tmp:
                pass
                #sub_result.append(f'Schema:{solve_schema(schema)}')
                #ast.args['schema'].replace(sqlglot.exp.Alias(this=sqlglot.exp.Identifier("SOLVED")))
            #print('first (xdd, xdd2)' == 'first(xdd, xdd2)')

            tmp = list(ast.find_all(sqlglot.exp.Subquery))
            for subquery in tmp:
                pass
                #sub_result.append(f'Subquery:{solve_subquery(subquery)}')
                #ast.args['subquery'].replace(sqlglot.exp.Alias(this=sqlglot.exp.Identifier("SOLVED")))

            for node in ast.walk(bfs=False):
                if isinstance(node, sqlglot.expressions.Table):
                    walk.append(f'Table:{str(node)}')
                    continue
                if isinstance(node, sqlglot.expressions.Column):
                    walk.append(f'Column:{str(node)}')
                    continue
                if isinstance(node, sqlglot.expressions.Join):
                    walk.append(f'Join')
                    continue
                #if isinstance(node, sqlglot.expressions.Alias):
                    #aliases.append(str(node))

        print(expr)
        print(f'Walk: {walk}')
        #print(f'Cols: {columns}\nTabs: {tables}\nAliases: {aliases}')
            

    except sqlglot.errors.ParseError as pe:
        print(pe)
    except sqlglot.errors.TokenError as te:
        print(te)
    except sqlglot.errors.OptimizeError as oe:
        print(oe)
    except:
        print('GG')

if __name__ == '__main__':
    whatever()