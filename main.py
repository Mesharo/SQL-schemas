import sqlglot.optimizer
import sqlglot.optimizer.qualify
from handling_dataset.main import filter_postgresql_questions, load_code_sections, get_questions, link_questions_with_answers, save_code_sections
import re
import os.path
import sqlglot
import copy

from io import StringIO
from html.parser import HTMLParser
class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def erase_html(code_section: str) -> str:
    result = strip_tags(' '.join(code_section))
    
    pattern = r"\\+['a-zA-Z]"
    matches = re.findall(pattern, result)

    matches = list(set(matches))
    matches.sort(key=len)
    matches.reverse()

    for match in matches:
        if match[-1] == "'":
            result = result.replace(match, '\'')
        if match[-1] == 'n':
            result = result.replace(match, '\n')
        else:
            result = result.replace(match, match[-2:])
    
    return result



def analyze(id: str, codes: list) -> None:
    print('CODES: ')
    for code in codes:
        code = erase_html(code)

        #print(f'-- code: {code}')
        expression_tree = False
        try:
            expression_trees = sqlglot.parse(code, dialect='postgres')
        except sqlglot.errors.ParseError:
            #print(f'Sqlglot failed to parse given statement')
            continue
        except sqlglot.errors.TokenError:
            #print(f'Sqlglot failed to tokenize given statement')
            continue

        for expression_tree in expression_trees:
            #print(f'-- tree: {repr(expression_tree)}')
            
            solved = False
            try:
                undo = copy.deepcopy(expression_tree)
                sqlglot.optimizer.qualify.qualify(expression_tree)

                root = sqlglot.optimizer.build_scope(expression_tree)
                
                if root:
                    for column in sqlglot.optimizer.find_all_in_scope(root.expression, sqlglot.exp.Column):
                        print(f"{column} => {root.sources[column.table]}")

                solved = True
            except sqlglot.errors.OptimizeError:
                #print(f'Sqlglot failed to optimize given statement.')
                expression_tree = undo
                continue
        
    print('--- --- ---')


def run(input_filepath_all_answers: str, input_filepath_postgresql_questions: str, input_filepath_linked: str, input_filepath_codes: str) -> None:
    """Main function.

    Automatization/serialization.
    Go through the filepaths in function args, check if they exist.
    Depending on the stage the project is in, take the correct steps.

    Arguments:
    input_filepath_all_answers -- path to the file with all answers from Posts.xml.
    input_filepath_postgresql_questions -- path to the file with only postgresql questions from Posts.xml.
    input_filepath_linked -- path to the file with postgresql questions linked with their corresponding answers.
    input_filepath_codes -- path to the file with filtered code sections out of postgresql questions and their corresponding answers.
    """

    if os.path.isfile(input_filepath_codes):
        codes = load_code_sections(input_filepath_codes)
        count = 0
        for key, values in codes.items():
            if count < 6:
                analyze(key, values)
                count += 1
        return

    if os.path.isfile(input_filepath_linked):
        save_code_sections(input_filepath_linked, input_filepath_codes)
        run(input_filepath_all_answers, input_filepath_postgresql_questions, input_filepath_linked, input_filepath_codes)

    if os.path.isfile(input_filepath_postgresql_questions):
        link_questions_with_answers(input_filepath_all_answers, get_questions(input_filepath_postgresql_questions), input_filepath_linked)
        save_code_sections(input_filepath_linked, input_filepath_codes)
        run(input_filepath_all_answers, input_filepath_postgresql_questions, input_filepath_linked, input_filepath_codes)
    
    # creates input_filepath_all_answers, input_filepath_postgresql_questions
    filter_postgresql_questions('D:\\stackoverflow\\Posts.xml', 'D:\\stackoverflow\\Tags.xml', input_filepath_postgresql_questions, input_filepath_all_answers)
    # creates input_filepath_linked
    link_questions_with_answers(input_filepath_all_answers, get_questions(input_filepath_postgresql_questions), input_filepath_linked)
    #creates input_filepath_codes
    save_code_sections(input_filepath_linked, input_filepath_codes)

    run(input_filepath_all_answers, input_filepath_postgresql_questions, input_filepath_linked, input_filepath_codes)

if __name__ == "__main__":
    run('D:\\all_answers', 'D:\\postgresql_questions.txt', 'D:\\linked.txt', 'D:\\codes.txt')
    

"""
DONE:
    1. Kapitola ohledně výběru parseru (stránka 10)
    2. Automatizace/serializace na základě aktuálního progresu
    partially 3. Parser - tabulky s jejich aliasy

OTÁZKY:
    1. zahodit pokud sqlglot nedokáže qualify?
    2. cíl bakalářky - knihovna
"""