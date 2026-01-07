const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pyBackend = null;

/**
 * 启动 Python 后端进程
 */
function startBackend() {
  // 1. 确定 backend.exe 的位置
  // 打包后：backend.exe 会被 electron-builder 放在 resources 目录下
  // 开发模式：直接运行 python 脚本
  let backendPath;
  
  if (app.isPackaged) {
    // 这里的 path.join(process.resourcesPath, 'backend.exe') 对应 package.json 中的 extraResources 配置
    backendPath = path.join(process.resourcesPath, 'backend.exe');
  } else {
    // 开发模式下指向你的 Python 入口
    backendPath = path.join(__dirname, 'src', 'api', 'main.py');
  }

  console.log(`正在尝试启动后端: ${backendPath}`);

  if (app.isPackaged) {
    // 运行打包后的 EXE
    pyBackend = spawn(backendPath, [], {
      windowsHide: true, // 隐藏黑窗口
      stdio: 'ignore'
    });
  } else {
    // 开发环境：使用 python 命令启动
    pyBackend = spawn('python', [backendPath], {
      stdio: 'inherit' // 在控制台输出 python 的日志
    });
  }

  pyBackend.on('error', (err) => {
    console.error('无法启动后端进程:', err);
  });
}

/**
 * 创建 Electron 浏览器窗口
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1300,
    height: 900,
    title: "Bird Photo Indexer",
    webPreferences: {
      // 这里的安全配置取决于你是否需要直接在前端使用 Node 接口
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  // 2. 加载前端入口文件
  // 路径指向 UI 文件夹下编译出来的 dist/index.html
  const indexPath = path.join(__dirname, 'bird-indexer-ui', 'dist', 'index.html');
  
  if (app.isPackaged) {
    mainWindow.loadFile(indexPath);
  } else {
    // 开发模式下，如果 Vite 正在运行，也可以直接 loadURL
    // mainWindow.loadURL('http://localhost:5173'); 
    mainWindow.loadFile(indexPath);
  }

  // 窗口关闭时清理资源
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Electron 完成初始化后执行
app.whenReady().then(() => {
  startBackend();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

/**
 * 所有窗口关闭时，杀死 Python 后端进程并退出
 */
app.on('window-all-closed', () => {
  if (pyBackend) {
    console.log('正在关闭后端进程...');
    // Windows 环境下可能需要用 taskkill 强制清理，但简单 kill 通常足够
    pyBackend.kill();
  }
  if (process.platform !== 'darwin') app.quit();
});

// 退出前的最后清理
app.on('will-quit', () => {
  if (pyBackend) pyBackend.kill();
});