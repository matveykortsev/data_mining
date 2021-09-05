import scrapy
from scrapy.http import HtmlResponse
import re
import json
from urllib.parse import quote
from copy import deepcopy
from instaparser.items import InstaparserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    username = ""
    enc_password = ""
    login_url = "https://www.instagram.com/accounts/login/ajax/"


    graphql_url = 'https://www.instagram.com/graphql/query/?'
    following_hash = '3dec7e2c57367ef3da3d987d89f9dbc8'
    followers_hash = '5aefa9893005572d237da5068082d8d5'

    def __init__(self, users_to_scrape, **kwargs):
        super().__init__(**kwargs)
        self.users_to_scrape = users_to_scrape

    def parse(self, response: HtmlResponse):
        yield scrapy.FormRequest(
            self.login_url,
            callback=self.user_login,
            method="POST",
            formdata={"username": self.username, "enc_password": self.enc_password},
            headers={"X-CSRFToken": self.fetch_csrf_token(response.text)}
        )

    def user_login(self, response: HtmlResponse):
        print()
        json_data = response.json()
        if json_data["user"] and json_data["authenticated"]:
            self.user_id = json_data["userId"]
            user_to_scrape_urls = [f'/{user_to_scrape}' for user_to_scrape in self.users_to_scrape]
            for user_to_scrape_url, user_to_scrape in zip(user_to_scrape_urls, self.users_to_scrape):
                yield response.follow(
                    user_to_scrape_url,
                    callback=self.user_data_parse,
                    cb_kwargs={"username": user_to_scrape}
                )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {"id": user_id, "first": 24}
        str_variables = quote(str(variables).replace(" ", "").replace("'", '"'))
        following_url = self.graphql_url + f"query_hash={self.following_hash}&variables={str_variables}"
        followers_url = self.graphql_url + f"query_hash={self.followers_hash}&variables={str_variables}"
        print()
        yield response.follow(
            following_url,
            callback=self.parse_following,
            cb_kwargs={
                "username": username,
                "user_id": user_id,
                "variables": deepcopy(variables)
            },
        )
        yield response.follow(
            followers_url,
            callback=self.parse_followers,
            cb_kwargs={
                "username": username,
                "user_id": user_id,
                "variables": deepcopy(variables)
            },
        )

    def parse_following(self, response: HtmlResponse, username, user_id, variables):
        data = response.json()
        data = data["data"]["user"]["edge_follow"]
        page_info = data.get("page_info", None)
        if page_info["has_next_page"]:
            variables["after"] = page_info["end_cursor"]
            str_variables = quote(str(variables).replace(" ", "").replace("'", '"'))
            url = self.graphql_url + f"query_hash={self.following_hash}&variables={str_variables}"
            yield response.follow(
                url,
                callback=self.parse_following,
                cb_kwargs={
                    "username": username,
                    "user_id": user_id,
                    "variables": deepcopy(variables)
                }
            )
        followings = data["edges"]
        followings_summary = []
        for following in followings:
            following_summary = {}
            following_summary['username'] = following['node']['username']
            following_summary['user_id'] = following['node']['id']
            following_summary['photo'] = following['node']['profile_pic_url']
            following_summary['is_private'] = following['node']['is_private']
            followings_summary.append(following_summary)
        yield InstaparserItem(followings=followings_summary, user_id=user_id, username=username)


    def parse_followers(self, response: HtmlResponse, username, user_id, variables):
        data = response.json()
        data = data["data"]["user"]["edge_followed_by"]
        page_info = data.get("page_info", None)
        if page_info["has_next_page"]:
            variables["after"] = page_info["end_cursor"]
            str_variables = quote(str(variables).replace(" ", "").replace("'", '"'))
            url = self.graphql_url + f"query_hash={self.followers_hash}&variables={str_variables}"
            yield response.follow(
                url,
                callback=self.parse_followers,
                cb_kwargs={
                    "username": username,
                    "user_id": user_id,
                    "variables": deepcopy(variables)
                }
            )
        print()
        followers = data["edges"]
        followers_summary = []
        for follower in followers:
            follower_summary = {}
            follower_summary['username'] = follower['node']['username']
            follower_summary['user_id'] = follower['node']['id']
            follower_summary['photo'] = follower['node']['profile_pic_url']
            follower_summary['is_private'] = follower['node']['is_private']
            followers_summary.append(follower_summary)
        yield InstaparserItem(followers=followers_summary, user_id=user_id, username=username)

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
