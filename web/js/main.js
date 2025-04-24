document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const messageInput = document.getElementById('message-input');

    // 获取并显示聊天记录
    async function fetchMessages() {
        try {
            const response = await fetch('http://127.0.0.1:8000/response');
            let text = await response.text();
            text = text.replace(/\n/g, '<br>');  // 修改：使用正则表达式全局替换所有换行符
            chatBox.innerHTML += text;
            chatBox.scrollTop = chatBox.scrollHeight; // 自动滚动到底部
        } catch (error) {
            console.error('获取消息失败:', error);
        }
    }

    // 发送消息
    async function sendMessage(content) {
        try {
            await fetch('http://127.0.0.1:8000/sendMessage', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ content })
            });
        } catch (error) {
            console.error('发送消息失败:', error);
        }
    }

    // 输入框事件监听
    messageInput.addEventListener('keypress', async (e) => {
        if (e.key === 'Enter' && messageInput.value.trim()) {
            await sendMessage(messageInput.value.trim());
            messageInput.value = '';
            await fetchMessages(); // 发送后立即刷新消息
        }
    });

    // 每1秒刷新一次消息
    setInterval(fetchMessages, 200);
    // 初始加载
    fetchMessages();
});