import gthelp
import flask
import queue
import sys
import threading
import flask_cors

app = flask.Flask('gt help server')
flask_cors.CORS(app)  # 启用CORS支持
output_queue = queue.Queue()


# 重定向标准输出
class OutputRedirect:
    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        self.queue.put(text)

    def flush(self):
        pass


sys.stdout = OutputRedirect(output_queue)


@app.route('/sendMessage', methods=['POST'])
def sendMessage():
    content = flask.request.json.get('content')
    print(content)
    threading.Thread(target=gthelp.processMessage, args=(content,)).start()
    return '', 200


@app.route('/response', methods=['GET'])
def getResponse():
    response = []
    while not output_queue.empty():
        response.append(output_queue.get())
    return ''.join(response), 200


@app.route('/test', methods=['GET'])
def test():
    print('TEST')
    return '', 200


if __name__ == '__main__':
    print('>>> ', end='')
    app.run(debug=True, port=8000)  # 将端口号从8080改为8081
