import sqlglot.optimizer
import sqlglot.optimizer.qualify
from handling_dataset.main import filter_postgresql_questions, load_code_sections, get_questions, link_questions_with_answers, save_code_sections
import re
import os.path
import sqlglot
import copy
import config

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



def analyze(id: str, codes: list) -> tuple:
    parsed = 0
    not_parsed = 0
    for code in codes:
        code = erase_html(code)

        correct = False
        try:
            expression_tree = sqlglot.parse(code, dialect='postgres')
            correct = True
        except sqlglot.errors.ParseError:
            correct = False
        except sqlglot.errors.TokenError:
            correct = False
        except:
            correct = False

        if correct:
            parsed += 1
        else:
            not_parsed += 1     
    return (parsed, not_parsed)


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
        parsed = 0
        not_parsed = 0
        for key, values in codes.items():
            if count < 1000:
                tmp = analyze(key, values)
                parsed += tmp[0]
                not_parsed += tmp[1]
                count += 1
        print(f'Parsed: {parsed}, not parsed: {not_parsed}')
        # Parsed: 931, not parsed: 1802
        return

    if os.path.isfile(input_filepath_linked):
        save_code_sections(input_filepath_linked, input_filepath_codes)
        run(input_filepath_all_answers, input_filepath_postgresql_questions, input_filepath_linked, input_filepath_codes)

    if os.path.isfile(input_filepath_postgresql_questions):
        link_questions_with_answers(input_filepath_all_answers, get_questions(input_filepath_postgresql_questions), input_filepath_linked)
        save_code_sections(input_filepath_linked, input_filepath_codes)
        run(input_filepath_all_answers, input_filepath_postgresql_questions, input_filepath_linked, input_filepath_codes)
    
    # creates input_filepath_all_answers, input_filepath_postgresql_questions
    filter_postgresql_questions(config.filepaths['posts'], config.filepaths['tags'], input_filepath_postgresql_questions, input_filepath_all_answers)
    # creates input_filepath_linked
    link_questions_with_answers(input_filepath_all_answers, get_questions(input_filepath_postgresql_questions), input_filepath_linked)
    #creates input_filepath_codes
    save_code_sections(input_filepath_linked, input_filepath_codes)

    run(input_filepath_all_answers, input_filepath_postgresql_questions, input_filepath_linked, input_filepath_codes)

if __name__ == "__main__":
    run(config.filepaths['all_answers'], config.filepaths['postgresql_questions'], config.filepaths['linked'], config.filepaths['codes'])
    

"""
DONE:
    1. config file, soubory do files/
    2. struktura kapitoly, nová kapitola ohledně schémat
    3. test na větším počtu
"""

#TODO Fix analyze()