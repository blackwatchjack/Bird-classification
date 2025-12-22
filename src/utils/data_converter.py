import json
from src.models.birds import TaxonNode

class DataConverter:
    @staticmethod
    def to_el_tree_json(node: TaxonNode):
        """递归将 TaxonNode 转换为 ElementTree 的数据结构"""
        # 1. 基础信息：ID 和 label
        count = node.total_photos
        label = f"{node.name} ({count})"

        # 构造当前节点的字典
        item = {
            "id": f"{node.rank}-{node.id}",
            "label": label,
            "rank": node.rank,
            "photocount": count
        }

        # 2. 如果到了种级别，附带文件路径方便前端查询
        if node.rank == "species":
            item["photo"] = [
                {"name":p.name, "path":p.absolute_path} for p in node.photo_indices
            ]

        if node.children:
            item["children"] = [
                DataConverter.to_el_tree_json(child) for child in node.children.values() if child.total_photos > 0
            ]
        
        return item