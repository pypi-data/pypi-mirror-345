import datetime
from bs4 import BeautifulSoup
import re
import html

from ._task import Task

class Course:
    def __init__(self, data: dict[str], request_func):
        self._id: str = data["classId"]
        self.code: str = data["lessonCode"]
        self.year: str = data["lessonCode"].split(".")[2][:-2]
        self.season: str = data["lessonCode"].split(".")[2][-2:]
        self.name: str = data["courseName"]
        self._tasks = list[Task]()
        self._request_func = request_func
        self._initialized = False

    def __repr__(self):
        return self._id
    
    def __get_task_list(self):
        res = self._request_func(f"webapps/blackboard/execute/launcher?type=Course&id={self._id}&url=")
        soup = BeautifulSoup(res.text, "html.parser")
        tmp = soup.find_all('a')
        for link in tmp:
            if re.search('title="作业区"', str(link)) != None:
                link = html.unescape(re.search('href="/(.*)" ', str(link)).group(1))
                self.__find_all_task(link)
                return
        self._initialized = True
            
    def __find_all_task(self, url: str):
        self._tasks = list[Task]()
        res = self._request_func(url)
        soup = BeautifulSoup(res.text, "html.parser")
        tmp = soup.find_all('a')
        for link in tmp:
            if re.search('uploadAssignment', str(link)) != None:
                title = re.search('<span style="color:#(.*);">(.*)</span>', str(link)).group(2)
                link = html.unescape(re.search('href="/(.*)"><', str(link)).group(1))
                self._tasks.append(self.__init_task(link, title))
        
        self._tasks.sort()
        return self._tasks
    
    def __init_task(self, url: str, title: str):
        res = self._request_func(url)
        soup = BeautifulSoup(res.text, "html.parser")
        method = soup.find('title').get_text().split(' ')[0][:-1]
        deadline = None
        submission = False

        if method == "上载作业":
            tmp = soup.find_all('div', class_='metaSection')
            for block in tmp:
                if re.search('截止日期', str(block)) != None:
                    block = block.find('div', class_='metaField')
                    deadline = block.get_text().split('\n')[1].strip().split(' ')[0] + ' ' + block.get_text().split('\n')[2].strip()
        elif method == "复查提交历史记录":
            tmp = soup.find_all('div', class_='attempt gradingPanelSection')
            for block in tmp:
                if re.search('截止日期', str(block)) != None:
                    block = str(block).replace('\n', '')
                    deadline = re.search('<h3>截止日期</h3><p>(.*)</p>', block).group(1)
            submission = True
        else:
            raise RuntimeError("Task error")
        
        if deadline != None:
            if re.search('上午', deadline) != None:
                deadline = datetime.datetime.strptime(deadline, "%Y年%m月%d日 上午%H:%M")
            else:
                deadline = datetime.datetime.strptime(deadline, "%Y年%m月%d日 下午%H:%M") + datetime.timedelta(hours=12)
        
        return Task(title, submission, deadline)
    
    def get_tasks(self) -> list[Task]:
        if self._initialized == False:
            self.__get_task_list()
        return self._tasks