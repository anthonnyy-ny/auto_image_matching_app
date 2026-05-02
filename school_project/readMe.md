1-打開壓縮檔，點擊school_project文件夾，解壓縮進自己的電腦。
2-用python解釋器，比如spyder，pycharm，vscode等打開main.py檔。
3-選擇main.py,點擊執行

开启后端/前端prompt
---
可以。你现在这个 Web 版有 后端 和 前端 两个服务，所以开启/关闭都要管两个。

开启
---
开第一个 PowerShell，启动后端：

cd D:\dev\auto_image_matching_app
python -m uvicorn web_app.backend.main:app --host 127.0.0.1 --port 8000
看到类似这样就是成功：

Uvicorn running on http://127.0.0.1:8000
再开第二个 PowerShell，启动前端：

cd D:\dev\auto_image_matching_app\web_app\frontend
npm run dev -- --port 5173
看到类似这样就是成功：

Local: http://127.0.0.1:5173/
然后浏览器打开：

http://127.0.0.1:5173
关闭
---
如果是你手动开的两个 PowerShell：

切到后端 PowerShell，按：
Ctrl + C
切到前端 PowerShell，也按：
Ctrl + C
如果它问：

Terminate batch job (Y/N)?
输入：

Y
再按 Enter。
---
如果你忘了哪个窗口在跑

可以用 PowerShell 查看端口：

netstat -ano | findstr :8000
netstat -ano | findstr :5173
会看到类似：

TCP    127.0.0.1:8000    ...    LISTENING    12345
最后那个数字是 PID。关闭它：

taskkill /PID 12345 /F
前端 5173 也一样。
