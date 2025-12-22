import pandas as pd
from typing import List
from models.birds import BirdSpecies, DataRegistry

class IOCDataLoader:
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        
    def load_to_registry(self, registry: DataRegistry):
        """从 Excel 读取并注册到 DataRegistry"""
        try:
            # 加载 Excel 文件
            df = pd.read_excel(
                self.excel_path,
                sheet_name="List",
                usecols=['Order', 'Family', 'IOC_15.1', 'Chinese']
            )

            # 遍历每一行，创建 BirdSpecies 对象并实例化
            for _, row in df.iterrows():
                # 跳过空行
                if pd.isna(row['IOC_15.1']) or pd.isna(row['Chinese']):
                    continue

                # 提取 genus 信息（IOC 15.1 中属名在第一词）
                latin = str(row['IOC_15.1'])
                genus = latin.split()[0]
                
                # 创建物种信息
                species = BirdSpecies(
                    id = latin,
                    order = str(row['Order']).strip(),
                    family = str(row['Family']).strip(),
                    genus = genus,
                    scientific_name = latin,
                    chinese_name = str(row['Chinese']).strip(),
                    search_keys = [str(row['Chinese']).strip(), latin.lower()]
                )
                
                # 注册到 DataRegistry
                registry.add_species(species)

            print(f"Successfully loaded {len(df)} species into registry.")
                
        except Exception as e:
            print(f"Error loading data: {e}")