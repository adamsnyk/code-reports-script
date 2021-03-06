import os, json
from datetime import datetime
import requests

API_TOKEN = os.environ.get('API_TOKEN')
ORG_ID = os.environ.get('ORG_ID')

# Get the Projects
projects = []
response = requests.get(
    'https://snyk.io/api/v1/org/{}/projects'.format(ORG_ID), 
    headers={"Authorization": "Token {}".format(API_TOKEN)}
)
for project in json.loads(response.content)['projects']:
    projects.append({'id': project['id'], 'name': project['name']})

projects_with_code_issues = []
for project in projects:
    code_issues = []
    response = requests.get(
        'https://api.snyk.io/v3/orgs/{}/issues?project_id={}&version=2021-08-20~experimental'.format(ORG_ID, project['id']), 
        headers={"Authorization": "Token {}".format(API_TOKEN)}
    )
    for issue in json.loads(response.content)['data']:
        code_issues.append({
            "project": project['name'],
            "title": issue['attributes']['title'],
            "severity": issue['attributes']['severity'],
            "ignored": issue['attributes']['ignored'],
        })
        if len(code_issues) > 0:
            projects_with_code_issues.append(code_issues)

for project_with_code_issues in projects_with_code_issues:
    project = project_with_code_issues[0]['project']

    html_results = [
        """
        <div style="border: 1px solid grey;border-radius: 3px;padding: 20px;">
            <div>Project: {}</div>
            <div>Title: {}</div>
            <div>Severity: {}</div>
            <div>Ignored: {}</div>
        </div>\n
        """.format(
            issue['project'],
            issue['title'],
            issue['severity'],
            issue['ignored'],
        ) for issue in project_with_code_issues
    ]
    html_results = "<div>{}</div>".format(project) + " ".join(html_results)

    html = """
            <html>
                <div style="background-color: #4b45a9;padding: 20px;display: flex;flex-direction: column;justify-content: space-around;">
                    <svg width="68px" height="35px" viewBox="0 0 68 35" version="1.1" xmlns="http://www.w3.org/2000/svg" role="img">
                        <title>Snyk - Open Source Security</title>
                            <g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
                                <g fill="#fff">
                                    <path
                                        d="M5.732,27.278 C3.445,27.278 1.589,26.885 0,26.124 L0.483,22.472 C2.163,23.296 4.056,23.689 5.643,23.689 C6.801,23.689 7.563,23.295 7.563,22.599 C7.563,20.594 0.333,21.076 0.333,15.839 C0.333,12.491 3.407,10.729 7.259,10.729 C9.179,10.729 11.161,11.249 12.444,11.704 L11.924,15.294 C10.577,14.774 8.747,14.291 7.222,14.291 C6.282,14.291 5.518,14.621 5.518,15.231 C5.518,17.208 12.903,16.815 12.903,21.925 C12.903,25.325 9.877,27.277 5.733,27.277 L5.732,27.278 Z M25.726,26.936 L25.726,17.894 C25.726,15.827 24.811,14.85 23.069,14.85 C22.219,14.85 21.329,15.09 20.719,15.46 L20.719,26.936 L15.352,26.936 L15.352,11.262 L20.602,10.83 L20.474,13.392 L20.652,13.392 C21.784,11.87 23.702,10.716 25.992,10.716 C28.736,10.716 31.112,12.416 31.112,16.436 L31.112,26.936 L25.724,26.936 L25.726,26.936 Z M61.175,26.936 L56.879,19.479 L56.446,19.479 L56.446,26.935 L51.082,26.935 L51.082,8.37 L56.447,0 L56.447,17.323 C57.515,16.017 61.112,11.059 61.112,11.059 L67.732,11.059 L61.454,17.689 L67.949,26.95 L61.175,26.95 L61.175,26.938 L61.175,26.936 Z M44.13,11.11 L41.93,18.262 C41.5,19.606 41.08,22.079 41.08,22.079 C41.08,22.079 40.75,19.516 40.292,18.172 L37.94,11.108 L31.928,11.108 L38.462,26.935 C37.572,29.04 36.199,30.815 34.369,30.815 C34.039,30.815 33.709,30.802 33.389,30.765 L31.255,34.061 C31.928,34.441 33.212,34.835 34.737,34.835 C38.703,34.835 41.359,31.627 43.215,26.885 L49.443,11.108 L44.132,11.108 L44.13,11.11 Z"
                                    ></path>
                                </g>
                            </g>
                    </svg>
                    <h2 style="color: white;">Snyk Code Test Report</h2>
                    <h3>Project: {}</h3>
                    <h3>Date + Time: {}</h3>
                </div>
                <body style="background-color: lightgray;font-family: Arial, Helvetica, sans-serif;">
                    <div style="height: 24px;" />
                    <h3>Results:</h3>
                    {}
                </body>
            </html>
        """.format(project, datetime.now(), html_results)
    
    file_name = project.split('/')[len(project.split('/')) - 1]
    with open('{}.html'.format(file_name), 'w') as f:
        f.write(html)