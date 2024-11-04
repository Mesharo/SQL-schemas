import os

current_directory = os.getcwd()

filepaths = dict(
    posts = 'D:\\stackoverflow.com\\Posts.xml',
    tags = 'D:\\stackoverflow.com\\Tags.xml',
    all_answers = f'{current_directory}\\files\\all_answers.txt',
    postgresql_questions = f'{current_directory}\\files\\postgresql_questions.txt',
    linked = f'{current_directory}\\files\\linked.txt',
    codes = f'{current_directory}\\files\\codes.txt'
)