from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class BirdSpecies:
    """权威物种元数据类 (基于 IOC 15.1)
    
    成员变量:
        id: str                               # 唯一标识符，建议使用学名作为键
        order: str                            # 分类学上的目
        family: str                           # 分类学上的科
        genus: str                            # 分类学上的属 (由学名首词提取)
        scientific_name: str                  # 拉丁学名
        chinese_name: str                     # 中文名称
        search_keys: List[str]                # 预生成的匹配键列表，包含中文和学名，统一转小写
    """
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
    """物理文件索引类
    
    成员变量:
        file_name: str                          # 原始文件名
        absolute_path: str                      # 文件的绝对物理路径，用于一键定位
        matched_species_id: Optional[str]       # 关联的 BirdSpecies.id，未匹配时为 None
    """
    file_name: str                          # 原始文件名
    absolute_path: str                      # 物理路径，用于一键定位
    matched_species_id: Optional[str] = None  # 关联的 BirdSpecies.id
    # root_dir: str = ""                      # 所属扫描根目录

@dataclass
class TaxonNode:
    """分类树节点类 (用于 UI 渲染)
    
    成员变量:
        rank: str                               # 分类级别: 'Order', 'Family', 'Genus', 或 'Species'
        name: str                               # 节点显示名称
        children: Dict[str, 'TaxonNode']        # 子节点字典，键为子节点名称
        photo_indices: List[PhotoIndex]         # 该节点直接关联的照片列表
    
    属性:
        total_photos: int                       # 递归计算当前节点及所有子节点的照片总数
    """
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
    """数据注册中心类，管理所有鸟类数据和照片索引
    
    成员变量:
        species_map: Dict[str, BirdSpecies]     # 核心数据：ID -> 物种对象映射
        match_lookup: Dict[str, str]            # 快速检索：中文/学名 -> 物种ID映射
        all_photos: List[PhotoIndex]            # 所有照片索引列表
        tree_root: TaxonNode                    # 虚拟分类树的根节点
    
    方法:
        add_species(species)                    # 注册 IOC 权威物种并建立匹配索引
        match_file(file_name)                   # 根据文件名返回匹配的物种 ID
        add_photo(photo)                        # 注册照片索引
        _update_tree(photo)                     # 将照片挂载到分类树节点
        show_tree()                             # 递归打印分类树
        show_photos(node, indent)               # 递归打印节点照片
    """
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

    def add_photo(self, photo: PhotoIndex):
        """注册照片索引"""
        self.all_photos.append(photo)
        # 递归更新分类树节点
        self._update_tree(photo)

    def _update_tree(self, photo: PhotoIndex):
        """将照片挂载到分类树节点"""
        species = self.species_map[photo.matched_species_id]

        # 获取路径
        path = [
            ("Order", species.order),
            ("Family", species.family),
            ("Genus", species.genus),
        ]

        # 递归挂载到树节点
        node = self.tree_root
        for rank, name in path:
            if name not in node.children:
                node.children[name] = TaxonNode(rank=rank, name=name)
            node = node.children[name]
        # 此时已抵达最深处的 Genus 节点
        species_key = f"{species.chinese_name} {species.scientific_name}"
        # 如果发现该种还未挂载到 Genus 节点下，创建一个新节点
        if species_key not in node.children:
            node.children[species_key] = TaxonNode(rank="species", name=species_key)
        # 最后再移动到种节点
        node = node.children[species_key]


        # 挂载到最末端的 Genus 节点
        node.photo_indices.append(photo)

    def show_tree(self):
        """info级, 递归打印分类树"""
        def print_node(node: TaxonNode, indent: str = ""):
            print(f"{indent}{node.rank} {node.name} (Photos: {node.total_photos})")
            for child in node.children.values():
                print_node(child, indent + "  ")
        print_node(self.tree_root)

    def show_photos(self, node: TaxonNode, indent: str = ""):
        """info级, 递归打印节点照片"""
        print(f"{indent}{node.rank} {node.name} (Photos: {node.total_photos})")
        for photo in node.photo_indices:
            if photo.matched_species_id and photo.matched_species_id in self.species_map:
                species = self.species_map[photo.matched_species_id]
                print(f"{indent}  {photo.file_name} -> {species.chinese_name} ({species.scientific_name})")
            else:
                print(f"{indent}  {photo.file_name} -> {photo.matched_species_id}")
        for child in node.children.values():
            self.show_photos(child, indent + "  ")