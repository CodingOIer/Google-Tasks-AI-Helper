import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# 设置权限作用域
SCOPES = ['https://www.googleapis.com/auth/tasks']


def getAuth():
    creds = None
    # 检查是否有已保存的凭据
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # 如果凭据无效或不存在，重新获取
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # 保存凭据供下次使用
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('tasks', 'v1', credentials=creds)


# 获取任务列表
def getTasks(tasklist_id='@default'):
    service = getAuth()
    results = service.tasks().list(tasklist=tasklist_id).execute()
    return results.get('items', [])


# 添加新任务
def addTask(title, notes=None, due=None, tasklist_id='@default'):
    service = getAuth()
    task = {
        'title': title,
        'notes': notes,
        'due': due,  # RFC3339 格式，例如 '2023-12-31T00:00:00Z'
    }
    return service.tasks().insert(tasklist=tasklist_id, body=task).execute()


# 更新任务
def changeTask(
    task_id, new_title=None, new_notes=None, new_status=None, tasklist_id='@default'
):
    if new_status == 'N':
        new_status = 'needsAction'
    if new_status == 'C':
        new_status = 'completed'
    if new_title == '':
        new_title = None
    if new_notes == '':
        new_notes = None
    if new_status == '':
        new_status = None
    service = getAuth()
    task = service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
    if new_title:
        task['title'] = new_title
    if new_notes:
        task['notes'] = new_notes
    if new_status in ['needsAction', 'completed']:
        task['status'] = new_status
    return (
        service.tasks().update(tasklist=tasklist_id, task=task_id, body=task).execute()
    )


# 删除任务
def removeTask(task_id, tasklist_id='@default'):
    service = getAuth()
    return service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()


# 使用示例
if __name__ == '__main__':
    # 获取所有任务
    tasks = getTasks()
    print("当前任务:", [task['title'] for task in tasks])

    # 添加新任务
    new_task = addTask('Buy milk', 'Organic whole milk')
    print("已添加任务:", new_task['title'])

    # 更新任务状态为完成
    updated_task = changeTask(new_task['id'], new_status='completed')
    print("更新后的状态:", updated_task['status'])

    # 删除任务
    removeTask(new_task['id'])
    print("任务已删除")
