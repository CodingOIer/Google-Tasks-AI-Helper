deepseekApiUrl = 'https://api.deepseek.com'
deepseekApiKey = ''

with open('./deepseek.key', 'r', encoding='utf-8') as f:
    deepseekApiKey = f.read()

import datetime
import gtasks
import openai

prompt = '''
你是一个 AI 助手，请跟据用户的指令，完成以下任务：
1. 根据用户的任务清单回答用户的问题
2. 如果用户没有任务，可以和他闲聊
你可以使用下面的指令，当你的回答中包含命令时，系统将会解析你的命令，并将结果给你，接着在用户操作之前继续询问你。
当你的回答中不包含命令时，系统不会解析你的命令，并且会结束时对你的询问。
在你使用命令或工具时必须包含命令格式。
1. 获取任务列表：|<TOOL=GET_TASKS>|
2. 添加任务：|<TOOL=ADD_TASKS<|>任务标题<|>任务细节>|
2. 修改任务：|<TOOL=CHANGE_TASKS<|>任务ID<|>新任务标题<|>新任务细节>|
3. 标记完成任务：|<TOOL=FINISH_TASKS<|>任务ID>|
4. 删除任务：|<TOOL=REMOVE_TASKS<|>任务ID>|
其中，删除任务操作请在用户放弃任务的情况下使用，任务细节建议按照以下规则填写方便你自己理解：
---
时间：yyyy-mm-dd hh:mm 前完成/开始
描述：任务描述
附加信息：xxx
---
当你使用命令或工具时，请等待系统做出回复，你可以告诉用户你正在处理任务，并等待系统回复。
请记住，你每次只能使用一个命令，如果你需要接连使用多个命令，请每次只回答一个命令，系统处理后你再继续。
'''

recent = []
recent.append({'role': 'system', 'content': prompt})


def requestsDeepseek(recent: list = []):
    client = openai.OpenAI(api_key=deepseekApiKey, base_url=deepseekApiUrl)
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=recent,
        max_tokens=1024,
        temperature=0.7,
        stream=True,  # Enable streaming
    )
    return response


def appendStr(origin: str = '', new: str = ''):
    if new[-1] == '\n':
        return origin + new
    return origin + new + '\n'


def getTasksInfo():
    res = '已有任务清单：\n'
    tasks = gtasks.getTasks()
    cnt = 0
    for task in tasks:
        if task['status'] != 'completed':
            cnt += 1
            res = appendStr(res, f'任务标题: {task["title"]}')
            res = appendStr(res, f'任务 ID: {task["id"]}')
            try:
                res = appendStr(res, f'任务细节: {task["notes"]}')
            except:
                pass
            res = appendStr(res, f'---')
    res = appendStr(res, f'共 {cnt} 个任务。')
    return res


def processMessage(message: str):
    global recent
    recent.append(
        {
            'role': 'system',
            'content': f'现在的时间是：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}',
        }
    )
    recent.append({'role': 'user', 'content': message})
    while True:
        response_stream = requestsDeepseek(recent)
        full_response = ''

        for chunk in response_stream:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end='')
                full_response += chunk.choices[0].delta.content
        print()

        # Command parsing based on the full message
        if '|<TOOL=' in full_response:
            content = full_response.split('|<')[1].split('>|')[0].split('<|>')
            if content[0] == 'TOOL=GET_TASKS':
                recent.append({'role': 'assistant', 'content': full_response})
                recent.append({'role': 'system', 'content': getTasksInfo()})
            elif content[0] == 'TOOL=ADD_TASKS':
                recent.append({'role': 'assistant', 'content': full_response})
                gtasks.addTask(content[1], content[2])
                recent.append({'role': 'system', 'content': '任务添加成功'})
            elif content[0] == 'TOOL=CHANGE_TASKS':
                recent.append({'role': 'assistant', 'content': full_response})
                gtasks.changeTask(content[1], content[2], content[3])
                recent.append({'role': 'system', 'content': '任务修改成功'})
            elif content[0] == 'TOOL=FINISH_TASKS':
                recent.append({'role': 'assistant', 'content': full_response})
                gtasks.finishTask(content[1])
                recent.append({'role': 'system', 'content': '任务标记为完成'})
            elif content[0] == 'TOOL=REMOVE_TASKS':
                recent.append({'role': 'assistant', 'content': full_response})
                gtasks.removeTask(content[1])
                recent.append({'role': 'system', 'content': '任务删除成功'})
            else:
                recent.append({'role': 'assistant', 'content': full_response})
                recent.append({'role': 'system', 'content': '未知命令'})
        else:
            break


while True:
    msg = input('>>>')
    if msg == '@clear':
        recent = []
        recent.append({'role': 'system', 'content': prompt})
        print('已清空历史记录')
        continue
    response = processMessage(msg)
