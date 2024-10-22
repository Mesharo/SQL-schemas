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
