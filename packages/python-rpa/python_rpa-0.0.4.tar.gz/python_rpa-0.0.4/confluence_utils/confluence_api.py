"""Confluence API functions."""

import json
import requests
from requests.auth import HTTPBasicAuth


from open_ai_utils.translation import translate

DEFAULT_TIMEOUT_SECONDS = 30

def get_page_info(page_id, base_url, username, password, access_token):
    """Get the page information with the given page_id."""
    return _get_page_info(page_id, base_url, username=username, password=, access_token)


def _get_page_info(page_id, base_url, **kwargs):
    if "access_token" in kwargs:
        return _get_page_info_by_access_token(page_id, base_url, kwargs["access_token"])
    elif "username" in kwargs and "password" in kwargs:
        response = requests.get(
            f"{base_url}/rest/api/content/{page_id}",
            auth=HTTPBasicAuth(kwargs["username"], kwargs["password"]),
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
    else:
        raise ValueError("Either access_token or username and password must be provided.")
    
    assert response.status_code == 200, response.text

    return response.json()

def _get_page_info(page_id, base_url, username, password):
    """Get the page information with the given page_id."""
    response = requests.get(
        f"{base_url}/rest/api/content/{page_id}",
        auth=HTTPBasicAuth(username, password),
        timeout=DEFAULT_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200, response.text

    return response.json()


def _get_page_info_by_access_token(page_id, base_url, access_token):
    """Get the page information with the given page_id."""
    response = requests.get(
        f"{base_url}/rest/api/content/{page_id}",
        headers={
          "Authorization": f"Bearer {access_token}"
        },
        timeout=DEFAULT_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200, response.text

    return response.json()


def get_page_content(page_id, base_url, username, password):
    """Get the page content with the given page_id."""
    response = requests.get(
      f"{base_url}/rest/api/content/{page_id}",
        auth=HTTPBasicAuth(username, password),
        params={
          "expand": "body.storage"
        },
        timeout=DEFAULT_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200, response.text

    return response.json()['body']['storage']['value']


def get_next_version(page_id, base_url, username, password):
    """Get the next version of the page with the given page_id."""
    page_info = get_page_info(page_id, base_url, username, password)

    return page_info['version']['number'] + 1


def get_page_labels(page_id, base_url, username, password):
    """Get the labels of the page with the given page_id."""
    response = requests.get(
      f"{base_url}/rest/api/content/{page_id}/label",
      auth=HTTPBasicAuth(username, password),
      timeout=DEFAULT_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200, response.text

    return response.json()['results']


def add_label_to_page(page_id, label_name, base_url, username, password, prefix="global"):
    """Add the label to the page with the given page_id."""

    data = {
      "prefix": f"{prefix}",
      "name": f"{label_name}"
    }

    response = requests.post(
      f"{base_url}/rest/api/content/{page_id}/label",
      headers={
        "Content-Type": "application/json"
      },
      auth=HTTPBasicAuth(username, password),
      data=json.dumps(data),
      timeout=DEFAULT_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200, response.text


def delete_label_from_page(page_id, label_name, base_url, username, password):
    """Delete the label from the page with the given page_id."""

    response = requests.delete(
      f"{base_url}/rest/api/content/{page_id}/label?name={label_name}",
      auth=HTTPBasicAuth(username, password),
      timeout=DEFAULT_TIMEOUT_SECONDS,
    )

    assert response.status_code == 204, response.text    


def get_child_page_ids(page_id, base_url, username, password, start=0, limit=25):
    """Get the child page ids of the page with the given page_id."""
    page_type = "page"
    cql = f"parent={page_id} AND type IN('{page_type}')"

    entities = search_entities_by_cql(
      cql=cql,
      base_url=base_url,
      username=username,
      password=password,
      start=start,
      limit=limit
    )

    return [page['content']['id'] for page in entities]


def search_entities_by_cql(cql, base_url, username, password, start=0, limit=25):
    """Search entities by the CQL query."""
    response = requests.get(
      f"{base_url}/rest/api/search",
      auth=HTTPBasicAuth(username, password),
      params={
        "cql": cql,
        "start": start,
        "limit": limit
      },
      timeout=DEFAULT_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200, response.text

    return response.json()['results']


def generate_ui_tab(title, content):
    """Generate a UI tab with the given title and content."""
    return f"""<ac:structured-macro ac:macro-id="e09c953f-58cf-42e7-b59c-2089efc9e511" ac:name="ui-tab" ac:schema-version="1">
  <ac:parameter ac:name="title">{title}</ac:parameter>
  <ac:rich-text-body>
{_add_spaces_to_lines(content, 4)}
  </ac:rich-text-body>
</ac:structured-macro>
"""


def generate_ui_tabs(ui_tabs):
    """Generate UI tabs with the given UI tabs."""
    return f"""<ac:structured-macro ac:macro-id="5ddf9f72-bc9f-4bb5-979d-ffc206d10463" ac:name="ui-tabs" ac:schema-version="1">
  <ac:rich-text-body>
{_add_spaces_to_lines('\n'.join(ui_tabs), 4)}
  </ac:rich-text-body>
</ac:structured-macro>
"""


def _add_spaces_to_lines(input_string, n):
    # 입력 문자열을 줄 단위로 분리
    lines = input_string.splitlines()

    # 각 줄에 n개의 탭을 추가
    indented_lines = [' ' * n + line for line in lines]

    # 다시 줄을 합쳐서 하나의 문자열로 반환
    return '\n'.join(indented_lines)


def update_page(page_id, content, base_url, username, password):
    """Update the page with the given page_id and content."""
    page_info = get_page_info(page_id, base_url, username, password)
    page_next_version = page_info['version']['number'] + 1
    page_title = page_info['title']
    space_key = page_info['space']['key']

    data = {
      "id": f"{page_id}",
      "type": "page",
      "title": f"{page_title}",
      "space": { "key": f"{space_key}" },
      "body": {
        "storage": {
          "value": f"{content}",
          "representation": "storage"
        }
      },
      "version": { "number": page_next_version }
    }

    response = requests.put(
        f"{base_url}/rest/api/content/{page_id}",
        headers={
          "Content-Type": "application/json"
        },
        auth=HTTPBasicAuth(username, password),
        data=json.dumps(data),
        timeout=DEFAULT_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200, response.text

    return response.json()
