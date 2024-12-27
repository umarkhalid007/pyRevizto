[pyRevizto.png](https://github.com/umarkhalid007/pyRevizto/blob/main/pyRevizto.png)
# pyRevizto

[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)

`pyRevizto` is a library designed specifically for Python developers who work with Revizto, a popular platform for BIM collaboration and issue tracking. By leveraging `pyRevizto`, developers can streamline their workflows and significantly enhance the capabilities of Revizto through automation.

## Features

- Manage licenses, projects, and users
- Handle issues and comments
- Generate reports
- Manage project sheets and stamps

## Installation

To install `pyRevizto`, use pip:

```sh
pip install pyRevizto
```

## Usage

Initialization
To use the pyRevizto library, you need to initialize the pyRevizto class with the required parameters:

```python
from pyrevizto import pyRevizto

region = "yourRegion"
revizto = pyRevizto(region, save_token=True)

```

## Authentication
To authenticate and get tokens, use the get_tokens method:

```python
tokens = revizto.get_tokens(access_code="your_access_code")
print(tokens)
```

## Example Usage

## Get Current User Licenses

```python
licenses = revizto.get_current_user_licenses()
print(licenses)
```

## Get Project Issues


```python
issues = revizto.get_project_issues(project_uuid="your_project_uuid")
print(issues)
```

## Invite Users to License

```python
invite_data = [
    {"email": "user1@example.com", "role": 2, "firstName": "userFirstName1", "lastName": "userLastName1", "company":"companyName"},
    {"email": "user2@example.com", "role": 2, "firstName": "userFirstName2", "lastName": "userLastName2", "company":"companyName"},

]
response = revizto.invite_users_to_license(
    license_uuid="your_license_uuid",
    invite_data=invite_data
)
print(response)
```

## Assign License Roles

```python
response = revizto.assign_license_roles(
    license_uuid="your_license_uuid",
    member_uuids=["member_uuid1", "member_uuid2"],
    role=2  # Role ID
)
print(response)
```

## Remove License Members

```python
response = revizto.remove_license_members(
    license_uuid="your_license_uuid",
    member_uuids=["member_uuid1", "member_uuid2"]
)
print(response)
```

## Get Project Members

```python
members = revizto.get_project_members(project_uuid="your_project_uuid")
print(members)
```

## Invite Users to Project


```python
response = revizto.invite_users_to_project(
    project_uuid="your_project_uuid",
    invitations=["user1@example.com", "user2@example.com"],
    role_id=111222  # Role ID
)
print(response)
```

## Get Project Roles

```python
roles = revizto.get_project_roles(license_uuid="your_license_uuid")
print(roles)
```

## Get Current User Info

```python
user_info = revizto.get_current_user_info()
print(user_info)
```

## Get Stamp Templates

```python
templates = revizto.get_stamp_templates(project_uuid="your_project_uuid")
print(templates)
```

## Get User Reports

```python
reports = revizto.get_user_reports(license_uuid="your_license_uuid")
print(reports)
```

## Get Project Sheets

```python
sheets = revizto.get_project_sheets(project_uuid="your_project_uuid")
print(sheets)
```

## Get Sheet History

```python
history = revizto.get_sheet_history(project_uuid="your_project_uuid", sheet_uuid="your_sheet_uuid")
print(history)
```

## Get Sheet Filter Options

```python
filter_options = revizto.get_sheet_filter_options(project_uuid="your_project_uuid")
print(filter_options)
```

## Get Deleted Issues

```python
deleted_issues = revizto.get_deleted_issues(project_uuid="your_project_uuid")
print(deleted_issues)
```
