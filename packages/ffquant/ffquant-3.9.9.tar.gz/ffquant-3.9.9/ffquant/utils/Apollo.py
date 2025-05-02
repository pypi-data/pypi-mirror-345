#!/usr/bin/python
# coding=utf-8

# Copyright 2022 Python Apollo OpenApi Client
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# title                     Python Apollo OpenApi Client
# description               functions to call openapi through python
# author                    ikool
# date                      2022-09-22
# reference website         https://www.apolloconfig.com/#/zh/usage/apollo-open-api-platform?id=_32-api%e6%8e%a5%e5%8f%a3%e5%88%97%e8%a1%a8

import logging
from typing import Dict
import requests
from ffquant.utils.Logger import stdout_log
import os

__ALL__ = ['Apollo']

class Apollo(object):
    LOCAL_CACHE = {}

    def __init__(self, app_id="RiskMaster", namespace="application", local=False):
        """
        Initialize an Apollo instance.

        Parameters:
        app_id (str): The application ID for Apollo. Default is "RiskMaster".
        namespace (str): The namespace to use for configuration. Default is "application".
        local (bool): If True, use local cache for configuration. Default is False.
        """
        self.app_id = app_id
        self.namespace = namespace
        self.local = local
        host = os.getenv("APOLLO_HOST", default="http://192.168.25.144:8070")
        token = os.getenv("APOLLO_TOKEN", default="7d60ed4d6b7f7b77f847a0364cc01466f8191ea92e96aa5791546f5393365eb2")
        stdout_log(f"APOLLO_HOST: {host}, APOLLO_TOKEN: {token}")
        self.client = ApiClient(host=host, token=token)
    
    def get_config(self, key, default=None):
        """
        get config value from apollo server
        
        Parameters:
        key (str): the key of config
        default: the default value if key not found
        
        Returns:
        str: the value of the key
        """
        if self.local:
            return self.LOCAL_CACHE.get(key, default)
        else:
            self._makesure_namespace_exists()

            item = self.client.get_item(appid=self.app_id, key=str(key), namespace_name=self.namespace)
            if not item:
                return default
            else:
                return item['value']

    def set_config(self, key, value):
        """
        set config value
        
        Parameters:
        key (str): the key of config
        value (str): the value of config
        
        Returns:
        True: success
        False: fail
        """
        ret = True
        if self.local:
            self.LOCAL_CACHE[key] = value
        else:
            self._makesure_namespace_exists()

            # 如果key不存在 则创建
            if not self.client.get_item(appid=self.app_id, key=str(key), namespace_name=self.namespace):
                self.client.created_item(appid=self.app_id, key=key, value=value, create_by="apollo", namespace_name=self.namespace)
                result = self.client.releases(appid=self.app_id, release_title="test", release_comment="test", released_by="apollo", namespace_name=self.namespace)
                if isinstance(result, dict) and dict(result).get("appId") == self.app_id and dict(result).get("namespaceName") == self.namespace:
                    ret = True
                else:
                    ret = False
            # 如果key存在 则更新
            elif self.client.update_item(appid=self.app_id, key=key, value=value, create_by="apollo", namespace_name=self.namespace):
                result = self.client.releases(appid=self.app_id, release_title="test", release_comment="test", released_by="apollo", namespace_name=self.namespace)
                if isinstance(result, dict) and dict(result).get("appId") == self.app_id and dict(result).get("namespaceName") == self.namespace:
                    ret = True
                else:
                    ret = False
            else:
                ret = False
        return ret

    def _makesure_namespace_exists(self):
        if not self.client.get_namespace(appid=self.app_id, namespace_name=self.namespace):
            self.client.create_namespace(appid=self.app_id, namespace_name=self.namespace, create_by="apollo", is_public=False)
            self.client.releases(appid=self.app_id, release_title="test", release_comment="test", released_by="apollo", namespace_name=self.namespace)

class ApiClient(object):
    """
    Python Apollo OpenApi Client
    """

    def __new__(cls, *args, **kwargs):
        """
        singleton model
        """
        kwargs = {x: kwargs[x] for x in sorted(kwargs)}
        key = repr((args, sorted(kwargs)))
        if hasattr(cls, "_instance"):
            if key not in cls._instance:
                cls._instance[key] = super().__new__(cls)
        else:
            cls._instance = {key: super().__new__(cls)}
        return cls._instance[key]

    def __init__(self, host: str, token: str, timeout: int = 3):
        """
        init method
        :param host: with the format 'http://localhost:8070'
        :param env: environment, default value is 'DEV'
        :param timeout: http request timeout seconds, default value is 30 seconds
        """
        self.host = host if host else "http://localhost:8070"
        self.token = token
        self.timeout = timeout

    def _http_get(self, api: str, params: Dict = None) -> requests.Response:
        """
        handle http request with get method
        :param url:
        :param params:
        :return:
        """
        url = f"{self.host}/{api}"
        try:
            return requests.get(
                url=url,
                params=params,
                timeout=self.timeout,
                headers={"Authorization": self.token, "Content-Type": "application/json;charset=UTF-8"},
            )
        except requests.exceptions.ReadTimeout as e:
            logging.error("request url: %s, error:%s" % (url, str(e)))
            return False
        except Exception as e:
            logging.error("request url: %s, error:%s" % (url, str(e)))
            return False

    def _http_post(self, api: str, data: Dict = None) -> requests.Response:
        """
        handle http request with get method
        :param url:
        :param params:
        :return:
        """
        url = f"{self.host}/{api}"
        try:
            return requests.post(
                url=f"{self.host}/{api}",
                json=data,
                timeout=self.timeout,
                headers={"Authorization": self.token, "Content-Type": "application/json;charset=UTF-8"},
            )
        except requests.exceptions.ReadTimeout as e:
            logging.error("request url: %s, error:%s" % (url, str(e)))
            return False
        except Exception as e:
            logging.error("request url: %s, error:%s" % (url, str(e)))
            return False

    def _http_put(self, api: str, data: Dict = None) -> requests.Response:
        """
        handle http request with get method
        :param url:
        :param params:
        :return:
        """
        url = f"{self.host}/{api}"
        try:
            return requests.put(
                url=f"{self.host}/{api}",
                json=data,
                timeout=self.timeout,
                headers={"Authorization": self.token, "Content-Type": "application/json;charset=UTF-8"},
            )
        except requests.exceptions.ReadTimeout as e:
            logging.error("request url: %s, error:%s" % (url, str(e)))
            return False
        except Exception as e:
            logging.error("request url: %s, error:%s" % (url, str(e)))
            return False

    def _http_delete(self, api: str) -> requests.Response:
        """
        handle http request with get method
        :param url:
        :param params:
        :return:
        """
        url = f"{self.host}/{api}"
        try:
            return requests.delete(
                url=f"{self.host}/{api}",
                timeout=self.timeout,
                headers={"Authorization": self.token, "Content-Type": "application/json;charset=UTF-8"},
            )
        except requests.exceptions.ReadTimeout as e:
            logging.error("request url: %s, error:%s" % (url, str(e)))
            return False
        except Exception as e:
            logging.error("request url: %s, error:%s" % (url, str(e)))
            return False

    def get_envclusters(self, appid: str):
        """
        获取环境列表、集群列表
        :param appid:
        :return:
        """
        api = f"openapi/v1/apps/{appid}/envclusters"
        resp = self._http_get(api)
        if resp and resp.status_code == 200:
            return resp.json()
        return False

    def get_apps(self):
        """
        获取APP列表
        :return:
        """
        api = "openapi/v1/apps"
        resp = self._http_get(api)
        if resp and resp.status_code == 200:
            return resp.json()
        return False

    def get_cluster(self, appid, env="dev", cluster_name="default"):
        """
        获取单个集群信息
        :param appid:
        :param env:
        :param cluster_name:
        :return:
        """
        api = f"openapi/v1/envs/{env}/apps/{appid}/clusters/{cluster_name}"
        resp = self._http_get(api)
        if resp and resp.status_code == 200:
            return resp.json()
        return False

    def create_cluster(self, appid, env, cluster_name, create_by):
        """
        创建集群
        :param appid:
        :param env:
        :param cluster_name:
        :param create_by:
        :return:
        """
        api = f"openapi/v1/envs/{env}/apps/{appid}/clusters"
        data = {
            "name": cluster_name,
            "appId": appid,
            "dataChangeCreatedBy": create_by
        }
        resp = self._http_post(api, data)
        if resp and resp.status_code == 200:
            return resp.json()
        return False

    def get_namespaces(self, appid, env="dev", cluster_name="default"):
        """
        获取集群下所有Namespace列表
        :param appid:
        :param env:
        :param cluster_name:
        :return:
        """
        api = f"openapi/v1/envs/{env}/apps/{appid}/clusters/{cluster_name}/namespaces"
        resp = self._http_get(api)
        if resp and resp.status_code == 200:
            return resp.json()
        return False

    def get_namespace(self, appid, env="dev", cluster_name="default", namespace_name="application"):
        """
        获取某个Namespace信息
        :param appid:
        :param env:
        :param cluster_name:
        :param namespace_name:
        :return:
        """
        api = f"openapi/v1/envs/{env}/apps/{appid}/clusters/{cluster_name}/namespaces/{namespace_name}"
        resp = self._http_get(api)
        if resp and resp.status_code == 200:
            return resp.json()
        return False

    def create_namespace(self, appid, namespace_name, create_by, format="properties", is_public=False, comment=""):
        """
        创建Namespace
        :param appid:
        :param namespace_name:
        :param create_by:
        :param format:
        :param is_public:
        :param comment:
        :return:
        """
        api = f"openapi/v1/apps/{appid}/appnamespaces"
        data = {
            "name": namespace_name,
            "appId": appid,
            "format": format,
            "isPublic": is_public,
            "comment": comment,
            "dataChangeCreatedBy": create_by
        }
        resp = self._http_post(api, data)
        if resp and resp.status_code == 200:
            return resp.json()
        return False

    def get_namespace_locked_by(self, appid, env="dev", cluster_name="default", namespace_name="application"):
        """
        获取某个Namespace当前编辑人接口
        :param appid:
        :param env:
        :param cluster_name:
        :param namespace_name:
        :return:
        """
        api = f"openapi/v1/envs/{env}/apps/{appid}/clusters/{cluster_name}/namespaces/{namespace_name}/lock"
        resp = self._http_get(api)
        if resp and resp.status_code == 200:
            return resp.json()
        return False

    def get_item(self, appid, key, env="dev", cluster_name="default", namespace_name="application"):
        """
         读取指定key的配置值 (注意：这个接口读取到的是最新的值，可能是未发布的配置)
        :param appid:
        :param key:
        :param env:
        :param cluster_name:
        :param namespace_name:
        :return:
        """
        api = f"openapi/v1/envs/{env}/apps/{appid}/clusters/{cluster_name}/namespaces/{namespace_name}/items/{key}"
        resp = self._http_get(api)
        if resp and resp.status_code == 200:
            return resp.json()
        return False

    def created_item(self, appid, key, value, create_by, env="dev", cluster_name="default", namespace_name="application", comment=""):
        """
        新增配置
        :param appid:
        :param key:
        :param value:
        :param create_by:
        :param env:
        :param cluster_name:
        :param namespace_name:
        :param comment:
        :return:
        """
        api = f"openapi/v1/envs/{env}/apps/{appid}/clusters/{cluster_name}/namespaces/{namespace_name}/items"
        data = {
            "key": key,
            "value": value,
            "comment": comment,
            "dataChangeCreatedBy": create_by
        }
        resp = self._http_post(api, data)
        if resp and resp.status_code == 200:
            return resp.json()
        return False

    def update_item(self, appid, key, value, create_by, env="dev", cluster_name="default", namespace_name="application", comment=""):
        """
        修改配置
        :param appid:
        :param key:
        :param value:
        :param create_by:
        :param env:
        :param cluster_name:
        :param namespace_name:
        :param comment:
        :return:
        """
        api = f"openapi/v1/envs/{env}/apps/{appid}/clusters/{cluster_name}/namespaces/{namespace_name}/items/{key}"
        data = {
            "key": key,
            "value": value,
            "comment": comment,
            "dataChangeLastModifiedBy": create_by,
            "dataChangeCreatedBy": create_by
        }
        resp = self._http_put(api, data)
        if resp and resp.status_code == 200:
            return True
        return False

    def delete_item(self, appid, key, operator, env="dev", cluster_name="default", namespace_name="application"):
        """
        删除配置
        :param appid:
        :param key:
        :param operator:
        :param env:
        :param cluster_name:
        :param namespace_name:
        :return:
        """
        api = f"openapi/v1/envs/{env}/apps/{appid}/clusters/{cluster_name}/namespaces/{namespace_name}/items/{key}?operator={operator}"
        resp = self._http_delete(api)
        if resp and resp.status_code == 200:
            return True
        return False

    def releases(self, appid, release_title, release_comment, released_by, env="dev", cluster_name="default", namespace_name="application"):
        """
        发布配置
        :param appid:
        :param release_title:
        :param release_comment:
        :param released_by:
        :param env:
        :param cluster_name:
        :param namespace_name:
        :return:
        """
        api = f"openapi/v1/envs/{env}/apps/{appid}/clusters/{cluster_name}/namespaces/{namespace_name}/releases"
        data = {
            "releaseTitle": release_title,
            "releaseComment": release_comment,
            "releasedBy": released_by
        }
        resp = self._http_post(api, data)
        if resp and resp.status_code == 200:
            return resp.json()
        return False

    def get_latest_releases(self, appid, env="dev", cluster_name="default", namespace_name="application"):
        """
        获取某个Namespace当前生效的已发布配置
        :param appid:
        :param env:
        :param cluster_name:
        :param namespace_name:
        :return:
        """
        api = f"openapi/v1/envs/{env}/apps/{appid}/clusters/{cluster_name}/namespaces/{namespace_name}/releases/latest"
        resp = self._http_get(api)
        if resp and resp.status_code == 200:
            return resp.json()
        return False

    def rollback(self, release_id, operator, env="dev"):
        """
        回滚到指定版本
        :param release_id:
        :param operator:
        :param env:
        :return:
        """
        api = f"openapi/v1/envs/{env}/releases/{release_id}/rollback?operator={operator}"
        resp = self._http_put(api)
        print(resp.status_code, resp.text)
        if resp and resp.status_code == 200:
            return True
        return False

    def get_latest_releases_by_page(self, appid, page, size, env="dev", cluster_name="default", namespace_name="application"):
        """
        分页获取配置项
        :param appid:
        :param page:
        :param size:
        :param env:
        :param cluster_name:
        :param namespace_name:
        :return:
        """
        api = f"openapi/v1/envs/{env}/apps/{appid}/clusters/{cluster_name}/namespaces/{namespace_name}/items?page={page}&size={size}"
        resp = self._http_get(api)
        print(resp.text)
        if resp and resp.status_code == 200:
            return resp.json()
        return False
