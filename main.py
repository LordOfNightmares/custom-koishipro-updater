import json
import logging
import os
import traceback
from datetime import datetime
from urllib.parse import urljoin, unquote

import dateutil.parser as dparser
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from methods.Concurrency import threaded
from methods.Config import FileConfig, Temp
from methods.GeneralMethods import create_folder
from methods.diff import diff_removal, diff_merge

logging.basicConfig(format='%(asctime)s:\t%(threadName)s:%(levelname)s:\t%(message)s',
                    level=logging.INFO,
                    datefmt="%H:%M:%S")


@threaded(workers=32)
def downloading_concurrently(*args):
    args[1].update(1)
    url = args[0]
    try:
        path = '/'.join([config.data['path'], url['path']]).replace("/", "\\")
        status = ""
        try:
            args[2].download_file(url['link'], path + ".tmp")
        except:
            status = "Failed:\t"
            logging.exception(f"Failed:\t{path}\n {traceback.format_exc()}")
        finally:
            with open(Temp.files, 'a') as output_file:
                output_file.write(f"{status}{path}\n")
        # logging.info(f'{args=}\t{url=}')
        return url
    except:
        logging.exception(f'\nItem:{args}\n')


@threaded(workers=4)
def concur_check(*args):
    # logging.info(f'{args[1].urls_to_visit}')
    if args[1].urls_to_visit:
        url = args[1].urls_to_visit.pop(0)
        try:
            # if len(self.hrefs) > 50:
            #     raise Exception("STOP")
            args[1].crawl_call(url)
            # logging.info(f'{args=}\t{url=}')
            return concur_check(args[1].urls_to_visit, args[1])
        except Exception:
            logging.exception(f'\nUrl:{url}\n')


def href_gather(url, soup):
    hrefs = [{"path": url.replace(config.data['url'], '') + unquote(href),
              "link": urljoin(url, href),
              "time": dparser.parse(link.nextSibling[-27:-8:], fuzzy=True).timestamp()}
             for link in soup.body.find_all('a')
             if link.contents[0] in unquote((href := link.get('href'))) and href != '../']
    if not (la := len(soup.body.find_all('a')) - 1) == (lh := len(hrefs)):
        #     logging.info(f"{la},{lh}")
        # else:
        logging.warning(f"{la},{lh}\n{hrefs}")
    return hrefs


class Crawler:
    def __init__(self, urls=[], ):
        self.visited_urls = []
        self.urls_to_visit = urls
        self.hrefs = []
        self.context = "Checking"

    def download_url(self, url):
        try:
            text = requests.get(url).text
        except ConnectionError:
            text = requests.get(url).text
        except Exception != ConnectionError:
            raise Exception

        return text

    def download_file(self, url, path):
        if os.path.exists(path):
            os.remove(path)
        try:
            req = requests.get(url, stream=True)
            output_file = open(path, 'wb')
            output_file.write(req.content)
            output_file.close()
            if Temp.max_requests == 0:
                logging.exception(f"Too many threads on Downloading {req.status_code=}")
        except requests.ConnectionError:
            self.download_file(url, path)
            Temp.max_requests -= 1
        except Exception:
            raise
        os.renames(path, path[:-4])

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        return href_gather(url, soup)

    def add_url_to_visit(self, url):
        if url not in self.visited_urls and url not in self.urls_to_visit:
            self.urls_to_visit.append(url)

    def downloading(self, main_url):
        html = self.download_url(main_url)
        hrefs = self.get_linked_urls(main_url, html)
        with open(Temp.cache, 'r') as c:
            self.cache = json.loads(c.read())
        for url in hrefs:
            if url['link'].endswith('/'):
                self.add_url_to_visit(url['link'])

        # downloadable = form_dls(hrefs)
        '''
        downloadable = [url for url in hrefs
                        if not url['path'].endswith("/")
                        and not any(url['path'].startswith(path) for path in config.data['ignore'])
                        and (any(url['path'] == file["path"] and url["time"] > file["time"] for file in self.cache)
                             or not os.path.exists('/'.join([config.data['path'], url['path']]).replace("/", "\\")))]
        '''
        try:
            downloadable = [url for url in hrefs if not url['path'].endswith("/")
                            and not any(url['path'].startswith(path) for path in config.data['ignore'])]
            exist = [url for url in downloadable if
                     not os.path.exists('/'.join([config.data['path'], url['path']]).replace("/", "\\"))]
            downloadable = diff_removal(downloadable, self.cache, 'path', 'time')
            downloadable = diff_merge(downloadable, exist, 'path', 'time')
        except Exception:
            raise
        if (dl := len(downloadable)) > 0:
            progress = tqdm(desc=main_url + "\t", total=dl)
            downloading_concurrently(downloadable, progress, crawler)
            progress.close()

    def checking(self, url):
        try:
            html = self.download_url(url)
        except:
            html = self.download_url(url)
        hrefs = self.get_linked_urls(url, html)
        for url in hrefs:
            if url['link'].endswith('/'):
                self.add_url_to_visit(url['link'])
        self.hrefs += hrefs

    def crawl_call(self, url):
        if not any(url.startswith(urljoin(config.data['url'], path)) for path in config.data['ignore']):
            self.cur_url = url
            try:
                logging.info(f'{self.context}: {url}')
                if self.context == "Checking":
                    self.checking(url)
                if self.context == "Downloading":
                    self.downloading(url)
            except Exception:
                raise
                # logging.exception(f'Failed to crawl: {url}')
            finally:
                self.visited_urls.append(url)

    def run(self, context="Checking"):
        self.context = context
        with open(Temp.files, 'w') as output_file:
            output_file.write("#Files downloaded \n")
        if context == "Checking":
            logging.info("Checking")
            concur_check(self.urls_to_visit, crawler)
        if context == "Downloading":
            logging.info("Downloading")
            self.urls_to_visit = [config.data['url']]
            self.visited_urls = []
            while self.urls_to_visit:
                url = self.urls_to_visit.pop(0)
                self.crawl_call(url)


def prep_folder_structure(cache, config):
    folder_paths = []
    for file in cache:
        if file['path'].endswith("/") and not any(file['path'].startswith(path) for path in config.data['ignore']):
            path = '/'.join([config.data['path'], file['path']]).replace("/", "\\")
            try:
                folder_paths.append(file['path'])
                os.listdir(path)
            except:
                create_folder(path)
    with open("current_paths.txt", 'w') as current_paths:
        current_paths.write("#Updater will check for these paths\n")
        for folder_path in folder_paths:
            current_paths.write(f"  - {folder_path}\n")


if __name__ == '__main__':
    try:
        Temp.cache = 'check.json'
        Temp.files = "file.txt"
        Temp.max_requests = 10
        config = FileConfig("config.yaml")
        crawler = Crawler(urls=[config.data['url']])
        crawler.run("Checking")
        if not os.path.exists(Temp.cache):
            with open(Temp.cache, 'w') as file:
                json.dump(crawler.hrefs, file)
        with open(Temp.cache, 'r') as file:
            cache = json.loads(file.read())
        prep_folder_structure(cache, config)
        # #testcase for dowloading 1 file
        # url="https://koishi.pro/ygopro/script/utility.lua"
        # path="script/utility.lua"
        # print(not path.endswith("/"))
        # print(not any(path.startswith(pathr) for pathr in config.data['ignore']))
        # print(not os.path.exists('/'.join([config.data['path'], path]).replace('/', '\\'))
        #       or any(path == cached_file['path'] and 1614509821.0> cached_file['time'] for cached_file in cache))
        # crawler.download_file(url,'/'.join([config.data['path'],path]).replace("/", "\\"))
        crawler.run("Downloading")
        with open(Temp.cache, 'w') as file:
            json.dump(crawler.hrefs, file)
    except Exception:
        with open("error.txt", 'a') as error_file:
            error_file.write(f'{datetime.now().strftime("%d/%m/%Y | %H:%M:%S |")}\n{traceback.format_exc()}\n\n')
    finally:
        input("Press enter to leave")
