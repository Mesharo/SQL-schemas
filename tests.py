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