#!/usr/bin/env python
import requests
import json

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser
import os

def load_jama_config_file(path=None):
    """
    Loads configuration from file with following content::

        [rest]
        url = <REST url endpoint>
        account = <username>
        password = <password>

    :param path: path to config file. If not specified, default locations of
    ``/etc/jama.cfg``, ``~/.jama``, and ``~/.jamarc`` are tried.
    """
    REQUIRED_KEYS = [
        'url', # WS api already uses url
        'account',
        'password',
    ]

    CONFIG_FILES = [
        '/etc/jama.cfg',
        '~/.jama',
        '~/.jamarc'
    ]
            
    config = ConfigParser()
    if path is None:
        config.read([os.path.expanduser(path) for path in CONFIG_FILES])
    else:
        config.read(path)

    if not config.has_section('rest'):
        return {}

    return dict(
        (key, val)
        for key, val in config.items('rest')
        if key in REQUIRED_KEYS
    )


class JamaAPI(object):
    """Main access point to the JAMA REST API"""
    
    def __init__(self, jama_config=None, default_project=""):
        super(JamaAPI, self).__init__()
        self.valid_queries=[]
        self.default_project=None
        if jama_config==None:
            self.jama_config=load_jama_config_file()
        else:
            self.jama_config=jama_config
        self.set_valid_queries()
        self.set_default_project()
    
    def rest_call(self,rest_resource="",params={}):
        result_dict = None
        if self.jama_config==None or self.jama_config=={}:
            raise ValueError("Empty jama_config")
        rest_result = requests.get(
            self.jama_config['url'] + rest_resource,
            params=params,
            auth=(self.jama_config['account'], self.jama_config['password'],)
        )
        result_dict = json.loads(rest_result.text) 
        return result_dict
    
    def set_default_project(self):
        self.default_project = [
                project for project in self.api_query(rest_resource="projects")['data']
                if project['projectKey'] == 'SKA1'
        ][0]
    
    def set_valid_queries(self):
        if self.valid_queries == None or self.valid_queries == []:
            result = self.rest_call(rest_resource="") # Empty query returns REST endpoints
            if result['meta']['status'] == "OK":
                self.valid_queries = list(result['data'])
            if len(self.valid_queries) != result['meta']['count']:
                raise ValueError("Number of results different from converted results")
    
    def api_query(self,rest_resource="",params={}):
        if (rest_resource != "") and (rest_resource not in self.valid_queries):
            raise ValueError("api_query: rest_resource can't be %s" % rest_resource)
        return self.rest_call(rest_resource=rest_resource, params=params)
    
    def raw_projects(self):
        projects_dict = self.api_query(rest_resource="projects")
        return projects_dict
    
    def projects(self):
        return self.raw_projects()['data']
        
    def raw_itemtypes(self):
        itemtypes_dict = self.api_query(rest_resource="itemtypes")
        return itemtypes_dict
    
    def itemtypes(self):
        return self.raw_itemtypes()['data']
    
    def raw_baselines(self, project_id=None):
        if project_id != None:
            baselines_dict = self.api_query(rest_resource="baselines", params={'project': project_id})
        else:
            baselines_dict = self.api_query(
                rest_resource="baselines", params={'project': self.default_project['id']}
            )
        return baselines_dict
    
    def latest_baselines(self):
        return self.raw_baselines()['data']
        
    def all_baselines(self):
        baselines = []
        return baselines
    


if __name__ == "__main__":
    from pprint import pprint 
    jama = JamaAPI()
    pprint(jama.projects())
    pprint(jama.itemtypes())
    pprint(jama.latest_baselines())