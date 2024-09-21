import re
from bigxml import Parser, xml_handle_element
import time

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
        accepted_answer_id = node.attributes['AcceptedAnswerId']
    except KeyError:
        accepted_answer_id = 'N/A'
    
    yield {
        'id': id,
        'body': body,
        'tags': tags,
        'accepted_answer_id': accepted_answer_id
    }


# filter out wanted questions and save them in a separate file for quicker access
def filter_postgresql_questions(file_name: str) -> None:
    postgresql_tags = get_postgresql_tags('D:\stackoverflow.com\Tags.xml')
    output_file = open('D:\postgresql_questions.txt', 'a', encoding='utf8')
    count = 0

    start = time.time()
    with open(file_name, 'rb') as XML_file:
        for item in Parser(XML_file).iter_from(handler):
            for correct_tag in postgresql_tags:
                if correct_tag in item['tags']:
                    output_file.write(str(item) + '\n')
            print(count)
            count += 1
    end = time.time()
    print(f'Time elapsed: {(end - start) / 60}')

    output_file.close()

if __name__ == "__main__":
    filter_postgresql_questions('D:\stackoverflow.com\Posts.xml')