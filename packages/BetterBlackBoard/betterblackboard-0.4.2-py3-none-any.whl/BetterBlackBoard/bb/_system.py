import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re

from ..url import generate_url
from ..cas import CASClient
from ._course import Course
from ._task import Task

_ua = UserAgent(platforms="desktop")

class BlackBoard:
    def __init__(self, client: CASClient):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = _ua.random
        self.__course_list = list[Course]()
        res = requests.get(generate_url("bb", ""))
        if "nginx_auth" in res.url:
            auth_url = generate_url("bb", "nginx_auth/login.php")
            auth_ticket = client.get_ticket(auth_url)
            self.session.get(auth_url, params = {"ticket": auth_ticket})
        login_url = generate_url("bb", "webapps/bb-SSOIntegrationDemo-BBLEARN/execute/authValidate/customLogin")
        ticket = client.get_ticket(login_url)
        res = self._request("webapps/bb-SSOIntegrationDemo-BBLEARN/execute/authValidate/customLogin?returnUrl=http://www.bb.ustc.edu.cn/webapps/portal/frameset.jsp&authProviderId=_103_1", params = {"ticket": ticket})
        if not res.url.endswith("webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1"):
            raise RuntimeError("Failed to login")
        
        self.__init_course()

    def _request(self, url: str, method: str = "get", **kwargs):
        return self.session.request(
            method,
            generate_url("bb", url),
            **kwargs
        )
    
    def __init_course(self):
        self.__course_list = list[Course]()
        res = self._request("webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1")
        soup = BeautifulSoup(res.text, "html.parser")
        all_links = soup.find_all('li')
        for link in all_links:
            if re.search('img alt', str(link)) != None:
                id = re.search('id=(.*)&', str(link)).group(1)
                code = re.search('_top">(.*): (.*)</a>', str(link)).group(1)
                name = re.search('_top">(.*): (.*)</a>', str(link)).group(2)
                self.__course_list.append(
                    Course({
                        "classId": id,
                        "lessonCode": code,
                        "courseName": name
                    }, self._request)
                )
        
        self.__course_list.sort(key=lambda x: - int(x._id.split('_')[1]))

    def get_course_list(self):
        return self.__course_list