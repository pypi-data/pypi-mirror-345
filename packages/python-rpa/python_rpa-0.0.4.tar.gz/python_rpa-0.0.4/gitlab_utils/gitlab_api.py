"""Gitlab API utilities"""

import requests
import json

DEFAULT_TIMEOUT_SECONDS = 30

class GitlabApiClient:
    """Gitlab API client"""
    def __init__(self, gitlab_url, access_token):
        self.gitlab_url = gitlab_url.strip('/')
        self.access_token = access_token


    def get_subgroup_ids(self, group_id):
        """Get the subgroups of the given group_id."""
        return [group['id'] for group in self.get_subgroups(group_id)]


    def get_subgroups(self, group_id):
        """Get the subgroups of the given group_id."""
        response = requests.get(
            f'{self.gitlab_url}/api/v4/groups/{group_id}/subgroups',
            headers={
                'Authorization': f'Bearer {self.access_token}'
            },
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )

        assert response.status_code == 200, response.text

        return response.json()


    def get_project_ids(self, group_id):
        """Get the projects of the given group_id."""
        return [project['id'] for project in self.get_projects(group_id)]


    def get_project_fields(self, group_id, fields=[]):
        """Get specific fields from projects of the given group_id."""
        projects = self.get_projects(group_id)

        if not fields:
            return projects

        return [{field: project[field] for field in fields if field in project}
                for project in projects]


    def get_projects(self, group_id):
        """Get the projects of the given group_id."""
        response = requests.get(
            f'{self.gitlab_url}/api/v4/groups/{group_id}/projects',
            headers={
                'Authorization': f'Bearer {self.access_token}'
            },
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )

        assert response.status_code == 200, response.text

        return response.json()


    def get_merge_request_urls_by_project_id(self, project_id, state=None):
        """Get the merge request urls of the given project_id."""
        return self.get_merge_request_fields_by_project_id(project_id, state=state, fields=["web_url"])


    def get_merge_request_fields_by_project_id(self, project_id, state=None, fields=[]):
        """Get specific fields from merge requests of the given project_id."""
        merge_requests = self.get_merge_requests_by_project_id(project_id, state=state)

        # print(json.dumps(merge_requests, ensure_ascii=False, indent=2))

        if not fields:
            return merge_requests

        return [{field: merge_request[field] for field in fields if field in merge_request}
                for merge_request in merge_requests]


    def get_merge_requests_by_project_id(self, project_id, state=None):
        """Get the merge requests of the given project_id."""
        params = {}
        if state:
            params['state'] = state

        response = requests.get(
            f'{self.gitlab_url}/api/v4/projects/{project_id}/merge_requests', 
            headers={
                'Authorization': f'Bearer {self.access_token}'
            },
            params=params,
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f'Error fetching merge requests: {response.status_code} - {response.text}')
            return []


    def get_merge_request_urls_by_group_id(self, group_id, state=None):
        """Get all merge request urls in the subgroups of the given parent_group_id."""
        return [merge_request['web_url'] for merge_request in self.get_merge_request_fields_by_group_id(group_id, state=state, fields=["web_url"])]


    def get_merge_request_fields_by_group_id(self, group_id, state=None, fields=[]):
        """Get all merge requests fields in the subgroups of the given parent_group_id."""
        merge_requests = []

        subgroup_ids = self.get_subgroup_ids(group_id)
        subgroup_ids.append(group_id)
        for subgroup_id in subgroup_ids:
            projects = self.get_project_fields(subgroup_id, ["id", "name", "web_url"])

            for project in projects:
                project_id = project['id']
                project_name = project['name']
                project_web_url = project['web_url']

                merge_requests.append({
                    "project_id": project_id,
                    "project_name": project_name,
                    "project_web_url": project_web_url,
                    "merge_requests": self.get_merge_request_fields_by_project_id(project_id, state=state, fields=fields)
                })

        return merge_requests


    def get_merge_requests_by_group_id(self, group_id, state=None):
        """Get all merge requests in the subgroups of the given parent_group_id."""
        merge_requests = []

        subgroup_ids = self.get_subgroup_ids(group_id)
        subgroup_ids.append(group_id)
        for subgroup_id in subgroup_ids:
            projects = self.get_project_fields(subgroup_id, ["id", "name", "web_url"])

            for project in projects:
                project_id = project['id']
                project_name = project['name']
                project_web_url = project['web_url']

                merge_requests.append({
                    "project_id": project_id,
                    "project_name": project_name,
                    "project_web_url": project_web_url,
                    "merge_requests": self.get_merge_requests_by_project_id(project_id, state=state)
                })

        return merge_requests
