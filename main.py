from handling_dataset.main import retrieve_linked, find_code_section
import sqlparse
from sqlparse.tokens import Whitespace, Newline
import re

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

def print_parsed(id: str, codes: list) -> None:   
    for code in codes: 
        tmp = erase_html(code)
        
        statements = sqlparse.split(tmp)

        for statement in statements:
            parsed = sqlparse.parse(statement)
            for parsed_statement in parsed:
                print(f'Statement: {parsed_statement}')
                print('Tokens: ')
                for token in parsed_statement.tokens:
                    if token.ttype not in (Whitespace, Newline):
                        print(f'    - {token}')
        
    print('-----------')

if __name__ == "__main__":
    codes = find_code_section(retrieve_linked('D:\\final.txt'))

    count = 0
    for key, values in codes.items():
        if count > 10:
            break
        print_parsed(key, values)
        count += 1
    