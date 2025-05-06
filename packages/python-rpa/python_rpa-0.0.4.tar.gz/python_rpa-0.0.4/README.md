# Get Started
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# How to Test (Pacakge, Module)
- [pytest documentation](https://docs.pytest.org/en/stable/)

![pytest-example](../docs/images/pytest-example.png)

```bash
source venv/bin/activate
cd python
pytest --password ${CONFLUENCE_PASSWORD} tests/confluence_utils

pytest --password ${CONFLUENCE_PASSWORD}
```

# How to Build
```bash
# DEPRECATED
# python setup.py sdist bdist_wheel

pip install build

python -m build
```

# How to Deploy
```bash
pip install twine

twine upload dist/*
```

# Confluence Utils
- [confluence-developer-documentation](https://developer.atlassian.com/cloud/)
- [confluence-rest-api](https://developer.atlassian.com/server/confluence/rest/v912/intro/#about)
- [confluence-rest-api-examples](https://developer.atlassian.com/server/confluence/confluence-rest-api-examples/)
- [confluence cql search](https://confluence.hmg-corp.io/plugins/servlet/scriptrunner/enhancedsearch/)
- [confluence cql quide](https://docs.adaptavist.com/sr4c/8.34.0/get-started/cql-guide)

```python
from confluence_utils import confluence_api


base_url = "https://confluence.hmg-corp.io"
username = "Confluence ID"      # 사번
password = "Confluence 비밀번호"

page_info = confluence_api.get_page_info(page_id="931614920", 
                                         base_url=base_url, 
                                         usernamme=username, 
                                         password=password)

confluence_api.update_page(page_id="931614920", 
                           content="", 
                           base_url=base_url, 
                           usernamme=username, 
                           password=password)
```

# Selenium Utils
```python
from selenium_utils import crawler


element = crawler.get_element_by_xpath(url="url", xpath="xpath")
elements = crawler.get_elements_by_xpath(url="url", xpath="xpath")
```
