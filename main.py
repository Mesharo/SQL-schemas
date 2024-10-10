import re
from bigxml import Parser, xml_handle_element
import time

from tests import *

# wanna find postgresql and postgresql-version tags
def get_postgresql_tags(file_name: str) -> list:
    result = []
    file = open(file_name, 'r', encoding='utf8')

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
    correct = False
    for tag in postgresql_tags:
        if tag in question_tags:
            correct = True
            break
    return correct

# filter out wanted questions and save them in a separate file for quicker access
def filter_postgresql_questions(file_name: str) -> None:
    postgresql_tags = get_postgresql_tags('D:\stackoverflow.com\Tags.xml')
    output_file_questions = open('D:\postgresql_questions.txt', 'a', encoding='utf8')
    output_file_all_answers = open('D:\\all_answers.txt', 'a', encoding='utf8')

    with open(file_name, 'rb') as XML_file:

        rows = XML_file.readlines(1000000000)

        # todo - encoding to utf8 for each readlines (insert header into list)
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

def get_questions() -> list:
    input_file_questions = open('D:\postgresql_questions.txt', 'r', encoding='utf8')
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

def save_linked(linked_questions_answers: dict) -> None:
    output_file = open('D:\\final.txt', 'a', encoding='utf8')

    for question, answers in linked_questions_answers.items():
        output_file.write(str(question) + '\n')

        for answer in answers:
            output_file.write(str(answer) + '\n')

    output_file.close()

def link_questions_with_answers(questions: list) -> None:
    input_file_answers = open('D:\\all_answers.txt', 'r', encoding='utf8')
    result = {}

    questions.sort(key = lambda x: int(x[1]))

    for tuple_key in questions:
        result[tuple_key[1]] = []

    rows = input_file_answers.readlines(1000000000)

    while len(rows) > 0:
        print(f'Start: {rows[0]}')
        print(f'End: {rows[-1]}')
        for answer in rows:
            id_body_parent = re.search("{'post_type_id': '2', 'id': '(.+?)', 'body': (.+?), 'parent_id': '(.+?)'", answer)

            if not id_body_parent:
                print('Failed to read answer from file!')
                continue

            tuple_id_body_parent = id_body_parent.group(1, 2, 3)

            if result.get(tuple_id_body_parent[2]) is not None:
                result[tuple_id_body_parent[2]].append(('2',) + tuple_id_body_parent)
                # (2, id, body, parent_id)

        rows = input_file_answers.readlines(1000000000)

    input_file_answers.close()

    result = dict(zip(questions, result.values()))
    save_linked(result)

    return result

def retrieve_linked() -> dict:
    input_file = open('D:\\final.txt', 'r', encoding='utf8')
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

if __name__ == "__main__":
    # filter_postgresql_questions('D:\stackoverflow.com\Posts.xml')
    # print(len(get_questions())) # 180282
    # link_questions_with_answers(get_questions())
    questions_answers = retrieve_linked()