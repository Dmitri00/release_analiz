import os
import sys
import configparser
#from _search import searcher, analyzer, argparser
from searcher import Searcher, Downloader
from analyzer import Analyzer
import threading
from argparser import parser


fields_definitions = {'article_text':'текст статьи','article_title':'заголовок статьи','article_url':'адрес в интрнете','hero':'герой статьи','institute':'организация-герой',
        'article_doi':'DOI-ссылка на статью','release_date':'дата публикации'}

def accept_key():
    print('Введите Y для подтвреждения, N для отмены')
    key = input()
    while key  not in set('YyNn'):
        key = input()
    if key in set('Yy'):
        return True
    else:
        return False
def main():
    cli_args = parser.parse_args(sys.argv[1:])
    config_name = cli_args.input
    output_file = cli_args.output

    config = configparser.ConfigParser()
    config.read(config_name)
    args = config['MAIN']
    """
    article_text = args['article']
    article_url = args['url']
    article_title = args['title']
    article_doi = args['doi']
    """

    
    print('Внимание! Проверьте правильность входных данных:')
    timer = threading.Event()
    timer.clear()
    timer.wait(3)
    for key,value in config['MAIN'].items():
        print(fields_definitions[key])
        timer.wait(3)
        print(value)
        if not accept_key():
            print('Завершение работы.')
            return
    print('Запуск поискового бота')
    timer.wait(3)
    results = run(**args)

    print('Поиск завершен. Найдены следующие ссылки:')

    header = 'Название страницы, Оценка точности, URL-адрес \n'
    with open(output_file,'w') as f:
        f.write(header)
        print(header)
        for line in results:
            f.write(line)
            print(line)

    print('Все ссылки сохранены в файле {}'.format(output_file))
    input('Поиск завершен. Нажмите любую клавишу для завершения')

    
def run(article_title,article_text,article_url,article_doi,hero,institute,release_date,search_depth=2):
    searcher = Searcher(article_text, search_depth=search_depth)
    dwld = Downloader()
    analyzer = Analyzer(article_title,article_text,article_url,article_doi,hero,institute)
    result_count = 150
    i = 0
    for url in searcher.gen():
        if url == '' or url == None:
            continue
        if i == result_count:
            break
        i+=1
        print('Обнаружена новая ссылка:\n{}\nОбработка...'.format(url))
        if 'pdf' in url:
            print('Обработка PDF-документов не поддерживается. Документ будет добавлен для проверки')
            page = None
        else:
            page = dwld.download(url,default_agent=True, timeout=15)
        print('Оценка близости текста - {:.2}/10'.format(analyzer.analyze(url,page)))
    results = sorted(analyzer.get_results(),key=lambda x: x[2], reverse=True)
    line_fmt = '{score:2.2},{title:},{url:}\n'
    lines = []
    i=0
    for url,title,score in results:
        line = line_fmt.format(title=title,url=url,score=score)
        lines.append(line)
        i+=1
    return lines

        

    
if __name__ == '__main__':
    main()
