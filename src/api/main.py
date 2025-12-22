from atexit import register
from fastapi import FastAPI, BackgroundTasks, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_converter import DataConverter
from models.birds import DataRegistry
from data.IOC_dataloader import IOCDataLoader
from utils.file_scanner import FileScanner

app = FastAPI(title="Bird Photo Indexer API")

# --- 配置 CORS，允许 Element Plus 跨域访问 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局单例
registry = DataRegistry()
# 加载分类数据
loader = IOCDataLoader(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'Multiling IOC 15.1_d.xlsx'))
loader.load_to_registry(registry)

# 扫描状态记录
scan_status = {
    "status": "idle",
    "scanned": 0,
    "matched": 0
}

# --- 数据模型 ---
class ScanRequest(BaseModel):
    paths: List[str] 

# --- 核心接口 ---
@app.post("/api/scan", status_code=status.HTTP_202_ACCEPTED)
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """启动扫描任务"""
    global scan_status
    scan_status["status"] = "scanning"
    
    scnner = FileScanner(registry)
    
    def run_scan():
        """实际的扫描任务"""
        total_scanned, total_matched = 0, 0
        for path in request.paths:
            scanned, matched = scnner.scan_directory(path)
            total_scanned += scanned
            total_matched += matched

        # 更新状态
        scan_status["scanned"] = total_scanned
        scan_status["matched"] = total_matched
        scan_status["status"] = "idle"

    background_tasks.add_task(run_scan)
    return {"message": "Scan started", "status": scan_status}

@app.get("/api/status")
async def get_scan_status():
    """获取当前扫描状态"""
    return scan_status

@app.get("/api/tree")
async def get_tree():
    """获取分类树结构, 已适配el-tree的格式"""
    return DataConverter.to_el_tree_json(registry.tree_root)

@app.get("/api/image-proxy")
# 图片预览接口
async def image_proxy(path: str = Query(...)):
    """ 因浏览器无法使用file:// 协议, 此接口用于代理图片请求 """
    from fastapi.responses import FileResponse
    if os.path.exists(path):
        return FileResponse(path)
    return {"error": "File not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)