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
    id = node.attributes['Id']
    body = node.attributes['Body']

    try:
        tags = node.attributes['Tags']
    except KeyError:
        tags = 'N/A'

    try:
        parent_id = node.attributes['ParentId']
    except KeyError:
        parent_id = 'N/A'

    try:
        accepted_answer_id = node.attributes['AcceptedAnswerId']
    except KeyError:
        accepted_answer_id = 'N/A'
    
    yield {
        'id': id,
        'body': body,
        'tags': tags,
        'parent_id': parent_id,
        'accepted_answer_id': accepted_answer_id
    }

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
        while len(rows) > 1:
            rows.append(b'</posts>')
            
            for item in Parser(rows).iter_from(handler):
                # answer
                if item['tags'] == 'N/A':
                    output_file_all_answers.write(str(item) + '\n')
                    continue
                
                # question
                if is_question_tagged_postgresql(postgresql_tags, item['tags']):
                    output_file_questions.write(str(item) + '\n')

            rows = XML_file.readlines(1000000000)
            rows.insert(0, b'<posts>')

    output_file_questions.close()
    output_file_all_answers.close()

def get_questions() -> list:
    input_file_questions = open('D:\postgresql_questions.txt', 'r', encoding='utf8')
    result = []

    for row in input_file_questions:
        id_body = re.search("{'id': '(.+?)', 'body': '(.+?)'", row)

        if not id_body:
            print('Failed to read question from file!')
            continue
        
        tuple_id_body = id_body.group(1, 2)
        result.append(tuple_id_body)

    input_file_questions.close()
    return result

# not tested
def link_questions_with_answers(questions: list) -> dict:
    input_file_answers = open('D:\\all_answers.txt', 'r', encoding='utf8')
    result = {}

    for tuple_key in questions:
        result[tuple_key] = []

    rows = input_file_answers.readlines(1000000000)

    while len(rows) > 0:
        for answer in rows:
            id_body_parent = re.search("{'id': '(.+?)', 'body': '(.+?)', 'tags': 'N/A', 'parent_id': '(.+?)'", answer)

            if not id_body_parent:
                print('Failed to read answer from file!')
                continue

            tuple_id_body_parent = id_body_parent.group(1, 2, 3)

            for key in result:
                if key[0] == tuple_id_body_parent[2]:
                    result[key].append(tuple_id_body_parent)
                    break

        rows = input_file_answers.readlines(1000000000)

    input_file_answers.close()
    return result

#{'id': id, 'body': body, 'tags': tags, 'parent_id': parent_id, 'accepted_answer_id': accepted_answer_id}


if __name__ == "__main__":
    # filter_postgresql_questions('D:\stackoverflow.com\Posts.xml')
    questions = get_questions()
    # questions_answers = link_questions_with_answers(get_questions)