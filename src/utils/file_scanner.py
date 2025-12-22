import os
from concurrent.futures import ThreadPoolExecutor
from typing import List
from src.models.birds import DataRegistry, PhotoIndex

class FileScanner:
    def __init__(self, registry: DataRegistry):
        self.registry = registry
        self.supported_extensions = ('.jpg', '.jpeg', '.png', '.raw', '.arw', '.cr2', '.nef')       # 支持的图片扩展名

    def scan_directory(self, root_path: str) -> tuple[int, int]:
        """递归扫描目录，将符合条件的文件路径注册到 DataRegistry
        
        返回值：
            tuple[int, int]: (扫描的文件数量, 匹配的文件数量)
        """
        # info 级别，上线 prd 前记得注释掉 print
        print(f"Scanning directory: {root_path}")
        
        scanned_count = 0
        matched_count = 0
        
        try:
            for entry in os.scandir(root_path):
                if entry.is_dir():
                    # 递归扫描子目录
                    sub_scanned, sub_matched = self.scan_directory(entry.path)
                    scanned_count += sub_scanned
                    matched_count += sub_matched
                elif entry.is_file():
                    if entry.name.lower().endswith(self.supported_extensions):
                        scanned_count += 1
                        # 注册到 DataRegistry
                        if any(ext in entry.name.lower() for ext in self.supported_extensions):
                            self._process_file(entry.name, entry.path)
                            matched_count += 1
        except FileNotFoundError:
            print(f"Directory not found: {root_path}")
        
        return scanned_count, matched_count
                    
    def _process_file(self, file_name: str, full_path: str) -> None:
        """执行匹配并注册文件路径"""
        species_id = self.registry.match_file(file_name)
        if species_id:
            photo = PhotoIndex(
                file_name = file_name,
                absolute_path = full_path,
                matched_species_id = species_id
            )

            self.registry.add_photo(photo)