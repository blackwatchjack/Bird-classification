from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class BirdSpecies:
    """权威物种元数据类 (基于 IOC 15.1)"""
    id: str                                 # 建议使用学名作为唯一键
    order: str                              # 目
    family: str                             # 科
    genus: str                              # 属 (由学名首词提取)
    scientific_name: str                    # 拉丁学名
    chinese_name: str                       # 中文名
    # 预生成的匹配键，包含中文和学名，统一转小写以防不规范命名
    search_keys: List[str] = field(default_factory=list) 

@dataclass
class PhotoIndex:
    """物理文件索引类 (零文件操作原则)"""
    file_name: str                          # 原始文件名
    absolute_path: str                      # 物理路径，用于一键定位
    matched_species_id: Optional[str] = None  # 关联的 BirdSpecies.id
    root_dir: str = ""                      # 所属扫描根目录

@dataclass
class TaxonNode:
    """分类树节点类 (用于 UI 渲染)"""
    rank: str                               # 'Order', 'Family', 'Genus', or 'Species'
    name: str                               # 节点显示名称
    children: Dict[str, 'TaxonNode'] = field(default_factory=dict)
    photo_indices: List[PhotoIndex] = field(default_factory=list)  # 该节点直接关联的照片
    
    @property
    def total_photos(self) -> int:
        """递归计算当前节点及所有子节点的照片总数"""
        count = len(self.photo_indices)
        for child in self.children.values():
            count += child.total_photos
        return count


class DataRegistry:
    def __init__(self):
        # 核心数据：ID -> 物种对象
        self.species_map: Dict[str, BirdSpecies] = {}
        
        # 快速检索：中文/学名 -> 物种ID
        self.match_lookup: Dict[str, str] = {}
        
        # 所有的照片索引列表
        self.all_photos: List[PhotoIndex] = []
        
        # 虚拟分类树根节点
        self.tree_root = TaxonNode(rank="Root", name="World Birds")

    def add_species(self, species: BirdSpecies):
        """注册 IOC 权威物种并建立匹配索引"""
        self.species_map[species.id] = species
        for key in species.search_keys:
            self.match_lookup[key.lower()] = species.id

    def match_file(self, file_name: str) -> Optional[str]:
        """根据文件名返回匹配的物种 ID"""
        # 简单示例：检查文件名中是否包含任何已知的中文名或学名
        # 实际开发中可以使用更高效的 Aho-Corasick 算法进行批量字符串匹配
        fn_lower = file_name.lower()
        for key, species_id in self.match_lookup.items():
            if key in fn_lower:
                return species_id
        return None