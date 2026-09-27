# Day 12 - 连接别人的MCP服务器

## 今天学了什么？

今天我们学了**怎么连接别人写好的MCP服务器**！不用自己写工具，直接用别人写好的！

---

## 什么是别人的MCP服务器？

就是别人已经写好的MCP服务器，我们只要连接上去就能用！

比如：
- 文件系统MCP：能读写本地文件
- GitHub MCP：能操作GitHub
- 浏览器自动化MCP：能自动操作浏览器

---

## 今天我们用了什么？

我们用了**文件系统MCP**（官方的，最简单，不需要API Key）。

它能：
- 读文件
- 写文件
- 列目录
- 搜索文件
- ...

---

## 怎么连接别人的MCP服务器？

跟连接自己的MCP服务器差不多，就是command和args不一样！

### 之前（连接自己的MCP）：
```python
server_params = StdioServerParameters(
    command="python",
    args=["mcp_server.py"]
)
```

### 现在（连接别人的MCP）：
```python
server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "D:\\AGENTMAKER\\ai-learning"]
)
```

---

## 什么是Node.js？

**Node.js = JavaScript运行环境**

就是让JavaScript能在电脑上运行的东西。

很多别人写的MCP服务器是用JavaScript写的，要用Node.js来运行。

---

## 什么是npx？

**npx = Node Package Execute**

就是用Node.js运行别人写好的包。

就像外卖平台，帮你把别人做好的饭拿过来。

---

## 什么是SDK？

**SDK = Software Development Kit = 软件开发工具包**

就是别人写好的一堆工具，帮你快速开发。

比如：
- MCP SDK：帮你快速写MCP服务器
- OpenAI SDK：帮你快速调用大模型

---

## 为什么第一次连接慢？

因为第一次要下载别人的MCP服务器包！

| 第几次 | 为什么 |
|--------|--------|
| 第一次 | 要下载包，很慢 |
| 第二次 | 已经下载好了，很快 |

---

## 下载的包存在哪里？

存在npm的缓存文件夹里：
```
C:\Users\你的用户名\AppData\Local\npm-cache\_npx
```

里面的乱码文件夹就是npx下载的包！

---

## 为什么大模型会搞错目录？

因为**大模型不知道我们连接的是哪个文件夹**！

它只知道有读文件、列目录的工具，但不知道"当前文件夹"是哪里，所以它是猜的！

---

## npx和npm install -g的区别：

| 方式 | 是什么 | 会被清理吗 |
|------|--------|-----------|
| npx | 临时下载 | 可能会被清理 |
| npm install -g | 全局安装 | 一直在 |

---

## 大白话总结：

| 东西 | 是什么 |
|------|--------|
| 自己写MCP服务器 | 自己做饭 |
| 连接别人的MCP服务器 | 点外卖 |
| Node.js | 能做西餐的厨房 |
| npx | 外卖平台 |
| SDK | 做菜的工具包 |
| npm缓存 | 冰箱，放外卖的 |

---

## 学到的知识点

| 知识点 | 说明 |
|--------|------|
| 怎么连接别人的MCP服务器 | 用npx运行别人的包 |
| Node.js是什么 | JavaScript运行环境 |
| npx是什么 | 用Node.js运行别人的包 |
| SDK是什么 | 软件开发工具包 |
| 第一次连接为什么慢 | 要下载包 |
| 下载的包在哪里 | npm缓存文件夹里 |

---

## Day 12总结

今天我们学了连接别人的MCP服务器，这是一个非常重要的能力：

1. ✅ 知道了怎么连接别人的MCP服务器
2. ✅ 知道了Node.js和npx是什么
3. ✅ 知道了SDK是什么
4. ✅ 知道了为什么第一次连接慢
5. ✅ 知道了下载的包存在哪里
6. ✅ 简历上能写"会使用MCP生态"

---

## 下一步可以做什么？

- 试试连接更多别人的MCP服务器（GitHub MCP、浏览器自动化MCP）
- 把多个MCP服务器连在一起
- 做一个完整的Agent项目
