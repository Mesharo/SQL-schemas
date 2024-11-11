import sqlglot.dialects
import sqlglot.dialects.dialect
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

def replace_unrecognized_letters(result: str) -> str:
    result = result.replace('E\'', '\'')
    result = result.replace('`', '')
    result = result.replace('ł', 'l')
    result = result.replace('ø', 'o')
    if 'psql:latest.dump:1601: invalid command' in result:
        return ''
    result = result.replace('£', '$')
    result = result.replace('è', 'e').replace('é', 'e').replace('É', 'e')
    result = result.replace('í', 'i')
    result = result.replace('ç', 'c')
    result = result.replace('õ', 'o')
    if '<?php if($funcao==1 )' in result:
        return ''
    result = result.replace('á', 'a')
    result = result.replace('ó', 'o')
    result = result.replace('ń', 'n')
    result = result.replace('ñ', 'n')
    if 'else {       $GLOBALS[komunikat_edycja_agenta' in result:
        return ''
    result = result.replace('ã', 'a')
    result = result.replace('©', 'c')
    result = result.replace('ü', 'u')
    result = result.replace('×', 'x')
    result = result.replace('ú', 'u')
    result = result.replace('ê', 'e')
    result = result.replace('«', '').replace('»', '')
    result = result.replace('à', 'a')
    result = result.replace('ф', '')
    result = result.replace('ô', 'o')
    result = result.replace('ä', 'a')
    result = result.replace('§', '$')
    result = result.replace('Ú', 'U')
    result = result.replace('ö', 'o')
    result = result.replace('â', 'a')
    result = result.replace('º', '')
    result = result.replace('¡', '')
    result = result.replace('ȼ', '')
    result = result.replace('ß', 's')
    result = result.replace('с', 'c')
    result = result.replace('С', 'C')
    result = result.replace('Â', 'A')
    result = result.replace('÷', '').replace('®', '').replace('¤', '').replace('¦', '')

    return result

def erase_html(code_section: list) -> str:
    result = strip_tags(';'.join(code_section))
    
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

    return replace_unrecognized_letters(result)

def analyze(id: str, codes: list) -> tuple:
    parsed = 0
    not_parsed = 0
    is_none = 0
    for code_list in codes:
        all_codes_string = erase_html(code_list)
        for code in all_codes_string.split(';'):
            #print('----------------------')
            #print(code)

            correct = False
            try:
                expression_tree = sqlglot.parse(code, dialect='postgres')
                if expression_tree == [None]:
                    is_none += 1
                correct = True
            except sqlglot.errors.ParseError as pe:
                correct = False
                #print(f'----\nParseError: {pe}\n-----')
            except sqlglot.errors.TokenError as te:
                correct = False
                #print(f'----\nTokenError: {te}\n-----')
            except:
                correct = False

            if correct:
                parsed += 1
            else:
                not_parsed += 1   

    return (parsed, not_parsed, is_none)

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
        parsed = 0
        not_parsed = 0
        is_none = 0

        for key, values in codes.items():
            if not values:
                continue

            tmp = analyze(key, values)
            parsed += tmp[0]
            not_parsed += tmp[1]
            is_none += tmp[2]
            
        print(f'Parsed: {parsed}, not parsed: {not_parsed}, None: {is_none} (included in Parsed)')
        print('DONE!')
        # Parsed: 931, not parsed: 1802 (původně)
        # Parsed: 1122, not parsed: 2251 (ignor prázdných)
        # Parsed: 5189, not parsed: 3887 (split na sekce, bez dialektu postgres)
        # Parsed: 9723, not parsed: 6415 (split ;)
        # Parsed: 9769, not parsed: 6369 (E' -> ', no `)

        # Parsed: 9571, not parsed: 6567 (added dialect='postgres')
        # Parsed: 1192213, not parsed: 886185 (all)
        # Parsed: 1192213, not parsed: 886185, None: 198696 (included in Parsed)
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

    - PL/pgSQL zahazuju (DECLARE @OuterPageSize int)
"""

#TODO Fix analyze()