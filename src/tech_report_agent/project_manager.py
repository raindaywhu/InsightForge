"""
项目管理模块
支持项目的保存、加载、分享和协作
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import uuid


class ProjectManager:
    """项目管理器，支持项目的本地存储和团队协作"""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        初始化项目管理器
        
        Args:
            storage_dir: 存储目录，默认为 output/projects
        """
        if storage_dir is None:
            storage_dir = Path(__file__).parent.parent.parent / "output" / "projects"
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 项目索引文件
        self.index_file = self.storage_dir / "projects_index.json"
        self._load_index()
    
    def _load_index(self):
        """加载项目索引"""
        if self.index_file.exists():
            with open(self.index_file, "r", encoding="utf-8") as f:
                self.index = json.load(f)
        else:
            self.index = {"projects": {}}
            self._save_index()
    
    def _save_index(self):
        """保存项目索引"""
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def create_project(
        self, 
        name: str, 
        topic: str, 
        owner: str = "default",
        template: str = "technical",
        description: str = ""
    ) -> dict:
        """
        创建新项目
        
        Args:
            name: 项目名称
            topic: 分析主题
            owner: 项目所有者
            template: 报告模板
            description: 项目描述
            
        Returns:
            项目信息字典
        """
        project_id = str(uuid.uuid4())[:8]
        created_at = datetime.now().isoformat()
        
        project = {
            "id": project_id,
            "name": name,
            "topic": topic,
            "owner": owner,
            "template": template,
            "description": description,
            "created_at": created_at,
            "updated_at": created_at,
            "status": "draft",
            "collaborators": [],
            "version": 1
        }
        
        # 保存到索引
        self.index["projects"][project_id] = project
        self._save_index()
        
        # 创建项目目录
        project_dir = self.storage_dir / project_id
        project_dir.mkdir(exist_ok=True)
        
        # 保存项目详情
        self._save_project(project_id, project)
        
        return project
    
    def _save_project(self, project_id: str, project_data: dict):
        """保存项目详情"""
        project_file = self.storage_dir / project_id / "project.json"
        with open(project_file, "w", encoding="utf-8") as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)
    
    def get_project(self, project_id: str) -> Optional[dict]:
        """获取项目信息"""
        if project_id in self.index["projects"]:
            project_file = self.storage_dir / project_id / "project.json"
            if project_file.exists():
                with open(project_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        return None
    
    def list_projects(self, owner: Optional[str] = None) -> list:
        """
        列出项目
        
        Args:
            owner: 过滤所有者，None 表示全部
            
        Returns:
            项目列表
        """
        projects = []
        for pid, pinfo in self.index["projects"].items():
            if owner is None or pinfo.get("owner") == owner:
                projects.append(pinfo)
        
        # 按更新时间排序
        projects.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return projects
    
    def update_project(self, project_id: str, updates: dict) -> Optional[dict]:
        """
        更新项目
        
        Args:
            project_id: 项目ID
            updates: 更新内容
            
        Returns:
            更新后的项目信息
        """
        project = self.get_project(project_id)
        if project is None:
            return None
        
        # 更新字段
        for key, value in updates.items():
            if key not in ["id", "created_at"]:
                project[key] = value
        
        project["updated_at"] = datetime.now().isoformat()
        project["version"] = project.get("version", 1) + 1
        
        # 保存
        self.index["projects"][project_id] = project
        self._save_index()
        self._save_project(project_id, project)
        
        return project
    
    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        if project_id not in self.index["projects"]:
            return False
        
        # 从索引删除
        del self.index["projects"][project_id]
        self._save_index()
        
        # 删除项目目录
        import shutil
        project_dir = self.storage_dir / project_id
        if project_dir.exists():
            shutil.rmtree(project_dir)
        
        return True
    
    def save_report(self, project_id: str, report_content: str) -> bool:
        """保存报告内容"""
        project = self.get_project(project_id)
        if project is None:
            return False
        
        report_file = self.storage_dir / project_id / "report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        # 更新状态
        self.update_project(project_id, {"status": "completed"})
        return True
    
    def load_report(self, project_id: str) -> Optional[str]:
        """加载报告内容"""
        report_file = self.storage_dir / project_id / "report.md"
        if report_file.exists():
            with open(report_file, "r", encoding="utf-8") as f:
                return f.read()
        return None
    
    def add_collaborator(self, project_id: str, user_id: str, role: str = "viewer") -> bool:
        """
        添加协作者
        
        Args:
            project_id: 项目ID
            user_id: 用户ID
            role: 角色 (owner/editor/viewer)
        """
        project = self.get_project(project_id)
        if project is None:
            return False
        
        collaborators = project.get("collaborators", [])
        
        # 检查是否已存在
        for collab in collaborators:
            if collab.get("user_id") == user_id:
                collab["role"] = role
                break
        else:
            collaborators.append({
                "user_id": user_id,
                "role": role,
                "added_at": datetime.now().isoformat()
            })
        
        self.update_project(project_id, {"collaborators": collaborators})
        return True
    
    def export_project(self, project_id: str) -> Optional[dict]:
        """
        导出项目（用于分享）
        
        Returns:
            包含完整项目数据的字典
        """
        project = self.get_project(project_id)
        if project is None:
            return None
        
        export_data = {
            "format_version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "project": project,
            "report": self.load_report(project_id)
        }
        
        return export_data
    
    def import_project(self, export_data: dict, owner: str = "default") -> Optional[dict]:
        """
        导入项目
        
        Args:
            export_data: 导出数据
            owner: 新所有者
            
        Returns:
            新项目信息
        """
        if export_data.get("format_version") != "1.0":
            return None
        
        project = export_data.get("project", {})
        
        # 创建新项目
        new_project = self.create_project(
            name=project.get("name", "Imported Project"),
            topic=project.get("topic", ""),
            owner=owner,
            template=project.get("template", "technical"),
            description=project.get("description", "")
        )
        
        # 保存报告
        if export_data.get("report"):
            self.save_report(new_project["id"], export_data["report"])
        
        return new_project


# 全局项目管理器实例
_project_manager = None

def get_project_manager() -> ProjectManager:
    """获取全局项目管理器实例"""
    global _project_manager
    if _project_manager is None:
        _project_manager = ProjectManager()
    return _project_manager