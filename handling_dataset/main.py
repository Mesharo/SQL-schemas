import re
from bigxml import Parser, xml_handle_element

def get_postgresql_tags(input_filepath_tags_xml: str) -> list:
    """Return a list of wanted postgresql tags.
    
    Argument:
    input_filepath_tags_xml -- path to the Tags.xml from Stackoverflow's data dump.
    """
    
    result = []
    file = open(input_filepath_tags_xml, 'r', encoding='utf8')

    for row in file:
        id_tagname = re.search('<row Id="(.+?)" TagName="(.+?)"', row)

        if not id_tagname:
            # Either meta data or <tags> element.
            continue
        
        tagname = id_tagname.group(2)
        
        if tagname != 'postgresql':
            postgresql_version = re.search('postgresql-(.+?)', tagname)

            if not postgresql_version:
                continue

            try:
                float(postgresql_version.group(1))
            except ValueError:
                # Not a version of postgresql.
                continue

        result.append(tagname)

    file.close()
    return result


@xml_handle_element('posts', 'row')
def handler(node):
    """Handler for BigXML parser.
    
    Function which parses the XML row and
    yields user-defined structure.
    """
    post_type_id = node.attributes['PostTypeId']
    id = node.attributes['Id']
    body = node.attributes['Body']

    # question
    if post_type_id == '1':
        try:
            tags = node.attributes['Tags']

            yield {
                'post_type_id': post_type_id,
                'id': id,
                'body': body,
                'tags': tags,
            }
        except KeyError:
            yield 'N/A'

    # answer
    elif post_type_id == '2':
        try:
            parent_id = node.attributes['ParentId']

            yield {
                'post_type_id': post_type_id,
                'id': id,
                'body': body,
                'parent_id': parent_id
            }
        except KeyError:
            yield 'N/A'
    else:
        yield 'N/A'

def is_question_tagged_postgresql(postgresql_tags: list, question_tags: str) -> bool:
    """
    Check for postgresql tags.
    Return true when found.

    Arguments:
    postgresql_tags -- list of wanted postgresql tags ('postgresql', versions).
    question_tags -- string of the current question's tags.
    """
    
    correct = False
    for tag in postgresql_tags:
        if tag in question_tags:
            correct = True
            break
    return correct

def filter_postgresql_questions(input_filepath_posts_xml: str, input_filepath_tags_xml: str, output_filepath_questions: str, output_filepath_answers: str) -> None:
    """Filter out postgresql questions.
    
    Read posts from a file by doses (1GB).
    Let parser and handler yield row values in expected structure.
    Distinguish between questions and answers.
    Check for postgresql tags, save if found. 

    Arguments:
    input_filepath_posts_xml -- path to the Posts.xml from Stackoverflow's data dump.
    input_filepath_tags_xml -- path to the Tags.xml from Stackoverflow's data dump.
    output_filepath_questions -- path where we save filtered questions.
    output_filepath_answers -- path where we save all answers.
    """

    postgresql_tags = get_postgresql_tags(input_filepath_tags_xml)
    output_file_questions = open(output_filepath_questions, 'a', encoding='utf8')
    output_file_all_answers = open(output_filepath_answers, 'a', encoding='utf8')

    with open(input_filepath_posts_xml, 'rb') as XML_file:

        rows = XML_file.readlines(1000000000)

        while len(rows) > 2:
            if rows[len(rows) - 1] != b'</posts>':
                rows.append(b'</posts>')
            
            for item in Parser(rows).iter_from(handler):
                # answer
                if item == 'N/A':
                    continue

                if item['post_type_id'] == '2':
                    output_file_all_answers.write(str(item) + '\n')
                    continue
                
                # question
                if is_question_tagged_postgresql(postgresql_tags, item['tags']):
                    output_file_questions.write(str(item) + '\n')

            rows = XML_file.readlines(1000000000)
            rows.insert(0, b'<?xml version="1.0" encoding="utf-8"?>')
            rows.insert(1, b'<posts>')

    output_file_questions.close()
    output_file_all_answers.close()

def get_questions(input_filepath_questions) -> list:
    """
    Read postgresql questions into a list, represented as tuples.

    Argument:
    input_filepath_questions -- path to the file with postgresql questions.
    """
    
    input_file_questions = open(input_filepath_questions, 'r', encoding='utf8')
    result = []

    for row in input_file_questions:
        id_body = re.search("{'post_type_id': '1', 'id': '(.+?)', 'body': (.+?), 'tags'", row)

        if not id_body:
            print('Failed to read question from file!')
            continue
        
        tuple_id_body = id_body.group(1, 2)
        result.append(('1',) + tuple_id_body)

    input_file_questions.close()
    return result

def save_linked(output_filepath: str, linked_questions_answers: dict) -> None:
    """
    Write linked postgresql questions with their answers into a file.

    Arguments:
    output_filepath -- path where we want to save everything.
    linked_questions_answers -- dictionary with questions as keys and lists of answers as values
    """

    output_file = open(output_filepath, 'a', encoding='utf8')

    for question, answers in linked_questions_answers.items():
        output_file.write(str(question) + '\n')

        for answer in answers:
            output_file.write(str(answer) + '\n')

    output_file.close()

def link_questions_with_answers(input_filepath_answers: str, questions: list) -> None:
    """Link postgresql questions with corresponding answers.
    
    Sort postgresql question based on their ID.
    Load answers, check their parent_id attribute.
    Link postgresql answers to their questions.
    Call function save_linked(result: dict) to save all into a file.

    Arguments:
    input_filepath_answers -- path to the file with answers.
    questions -- list with postgresql questions, represented as tuples.
    """

    input_file_answers = open(input_filepath_answers, 'r', encoding='utf8')
    result = {}

    questions.sort(key = lambda x: int(x[1]))

    for tuple_key in questions:
        result[tuple_key[1]] = []

    rows = input_file_answers.readlines(1000000000)

    while len(rows) > 0:
        for answer in rows:
            id_body_parent = re.search("{'post_type_id': '2', 'id': '(.+?)', 'body': (.+?), 'parent_id': '(.+?)'", answer)

            if not id_body_parent:
                print('Failed to read answer from file!')
                continue

            tuple_id_body_parent = id_body_parent.group(1, 2, 3)

            if result.get(tuple_id_body_parent[2]) is not None:
                result[tuple_id_body_parent[2]].append(('2',) + tuple_id_body_parent)

        rows = input_file_answers.readlines(1000000000)

    input_file_answers.close()

    result = dict(zip(questions, result.values()))
    save_linked(result)

    return result

def retrieve_linked(input_filepath_linked: str) -> dict:
    """Get questions and answers.
    
    Read saved postgresql questions with their corresponding
    answers from a file into a dictionary.

    Argument:
    input_filepath_linked -- path to the file with questions and answers.
    """

    input_file = open(input_filepath_linked, 'r', encoding='utf8')
    result = {}

    row = input_file.readline()
    current = -1

    while row:
        row_tuple = eval(row)
        if row_tuple[0] == '1':
            current = row_tuple[1::]
            result[current] = []
        else:
            result[current].append(row_tuple[1::])
        
        row = input_file.readline()

    input_file.close()
    return result

def find_code_section(linked: dict) -> dict:
    """Filter <code></code>.
    
    Iterate through keys and values of given dictionary of questions and answers.
    Search for code section in each, return list of found sections.
    Save found into a dictionary under question's ID.
    Return result dictionary.

    Argument:
    linked -- dictionary, keys = questions, values = lists of answers.
    """

    result = {}

    for question, answers in linked.items():
        list_of_questions_list = []

        list_code_question = re.findall("<code>(.+?)</code>", str(question))

        if len(list_code_question) > 0:
           list_of_questions_list.append(list_code_question)

        for answer in answers:
            list_code_answer = re.findall("<code>(.+?)</code>", str(answer))

            if len(list_code_answer) > 0:
                list_of_questions_list.append(list_code_answer)

        result[question[0]] = list_of_questions_list

    return result