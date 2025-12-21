from src.birds import DataRegistry
from src.IOC_dataloader import IOCDataLoader
from src.file_scanner import FileScanner

def main():
    # 初始化全局数据注册表
    registry = DataRegistry()

    # 1. 加载数据库
    loader = IOCDataLoader("src/Multiling IOC 15.1_d.xlsx")
    loader.load_to_registry(registry)
    # print(f"Total indexed species: {registry.species_map}")


    # 2. 扫描文档路径
    scanner = FileScanner(registry)
    # 这里的路径暂时写死，需要根据实际情况修改
    scanner.scan_directory("src/photo")    


    # 3. 打印扫描结果
    registry.show_photos(registry.tree_root)

if __name__ == "__main__":
    main()