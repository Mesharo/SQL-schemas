import sqlglot.dialects
import sqlglot.dialects.dialect
import sqlglot.errors
import sqlglot.optimizer
import sqlglot.optimizer.qualify
from handling_dataset.main import filter_postgresql_questions, load_code_sections, get_questions, link_questions_with_answers, save_code_sections
import re
import os.path
import sqlglot
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

def can_be_parsed(code: str) -> bool:
    try:
        expression_tree = sqlglot.parse(code, dialect='postgres')

        if expression_tree == [None]:
            return False

        return True
    except:
        return False

def can_be_scoped(ast) -> bool:
    try:
        root = sqlglot.optimizer.scope.build_scope(ast)
        return True
    except:
        return False

def can_be_qualified(ast) -> bool:
    try:
        sqlglot.optimizer.qualify.qualify(ast)

        return True
    except:
        return False

def solve_with_scopes(ast) -> list:
    result = []
    columns = []
    tables = []
    aliases = []

    root = sqlglot.optimizer.scope.build_scope(ast)   
    for scope in root.traverse():
        pass

def solve_without_scopes(ast) -> list:
    result = []
    columns = []
    tables = []
    aliases = []

    tmp = list(ast.find_all(sqlglot.exp.Column))
    for column in tmp:
        columns.append(str(column))            

    tmp = list(ast.find_all(sqlglot.exp.Table))
    for table in tmp:
        tables.append(str(table))

    tmp = list(ast.find_all(sqlglot.exp.Alias))
    for alias in tmp:
        aliases.append(str(alias))

    print(f'Cols: {columns}\nTabs: {tables}\nAliases: {aliases}')

    #TODO traversing again using walk and link together


def analyze(id: str, codes: list) -> tuple:
    result = []
    columns_tables = []

    for code_list in codes:
        all_codes_string = erase_html(code_list)
        for code in all_codes_string.split(';'):
            if not can_be_parsed(code):
                continue

            try:
                expression_tree = sqlglot.parse(code, dialect='postgres')
                
                for ast in expression_tree:
                    if (can_be_qualified(ast)):
                        sqlglot.optimizer.qualify.qualify(ast)

                    if (can_be_scoped(ast)):
                        columns_tables = solve_with_scopes(ast)
                    
                    columns_tables = solve_without_scopes(ast)

                    if columns_tables:
                        result.append(columns_tables)
                        columns_tables.clear()

            except sqlglot.errors.ParseError as pe:
                continue
            except sqlglot.errors.TokenError as te:
                continue
            except sqlglot.errors.OptimizeError as oe:
                continue
            except:
                continue

    return (id, result)

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
            if not values:
                continue
            
            while count < 100:
                tmp = analyze(key, values)
                print(f'ID: {tmp[0]}, columns and tables: {tmp[1]}')

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
    