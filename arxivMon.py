import os
import sys
import logging
import requests
import parsel
import urllib.parse
from arxivdb import ArxivDB
from wechat_notification import WechatNotification

#url_left = 'https://arxiv.org/search/?query='
#url_right = '&searchtype=author&abstracts=show&order=-announced_date_first&size=100'

url_left = 'https://arxiv.org/search/advanced?advanced=&terms-0-operator=AND&terms-0-term='
url_right = '&terms-0-field=author&classification-computer_science=y&classification-physics_archives=all&classification-include_cross_list=include&date-filter_by=past_12&date-year=&date-from_date=&date-to_date=&date-date_type=submitted_date&abstracts=show&size=200&order=-announced_date_first'

db = ArxivDB()
project_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
logging.basicConfig(level=logging.DEBUG,
         format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
         datefmt='[%Y-%m_%d %H:%M:%S]',
         filename=project_path + '/log/arxiv.log',
         filemode='a')

def getSendKey():
    with open(project_path + '/conf/sendkey.txt', 'r') as f:
        return f.read()

def getMonAuthors():
    authors = []
    with open(project_path + '/conf/authors.txt', 'r') as f:
        for line in f:
            authors.append(line.strip())
    return authors


def getNewPapersByAuthor(arxiv_results, author_mon):
    new_papers = []
    for paper_sec in arxiv_results:
        p_sel = parsel.Selector(paper_sec)
        arxiv_label = p_sel.css('.is-marginless a::text').get()

        if not db.selectByAuthorLable((arxiv_label,)):
            arxiv_link = p_sel.css('.is-marginless a::attr(href)').get()
            title = p_sel.css('.title::text').get().strip()
            authors = ', '.join(['__' + a + '__' if a.lower() == author_mon.lower() else a for a in p_sel.css('.authors a::text').getall()])
            abstract = p_sel.css('.abstract-short::text').get().strip()
            submitted = p_sel.xpath('//p[4]/text()[1]').get().strip()
            comments = p_sel.xpath('//p[5]/span[2]/text()').get()
            paper = (arxiv_label, author_mon, arxiv_link, title, authors, abstract, submitted, comments)
            logging.debug('the new paper is %s', paper)
            db.insertPaper(paper)
            new_papers.append(paper)

    return new_papers

def checkArxivByAuthor(authors):
    new_papers = []
    status = 0
    for author in authors:
        url = url_left + urllib.parse.quote('"' + author + '"') + url_right
        logging.debug('url: %s', url)
        retry_times = 0
        while(True):
            response = requests.get(url)
            if requests.codes.ok == response.status_code:
                break
            elif ++retry_times == 5:
                logging.info('newwork error!')
                status = 1
                return [], status

        selector = parsel.Selector(response.text)
        arxiv_results = selector.css('.arxiv-result').getall()
        new_papers += getNewPapersByAuthor(arxiv_results, author)

    logging.info('new papers number: {}'.format(len(new_papers)))
    status = 0 if new_papers else 2
    return new_papers, status 


def main():
    sendkey = getSendKey().strip()
    authors = getMonAuthors()
    new_papers, status = checkArxivByAuthor(authors)

    wn = WechatNotification()
    try:
        wn.send(sendkey, status, new_papers)
    except Exception as e:
        logging.error('WechatNotification send error!')
    
    db.close

if __name__ == '__main__':
    main()