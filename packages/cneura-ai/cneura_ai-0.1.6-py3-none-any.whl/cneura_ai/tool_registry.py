# tool_registry.py
from pymongo import MongoClient
from typing import Dict, List, Optional
from bson.objectid import ObjectId
import os


class ToolRegistry:
    def __init__(self, mongo_uri: str = "mongodb://localhost:27017", db_name: str = "tool_manager"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db["tools"]

    def register(self, tool_info: Dict) -> ObjectId:
        existing = self.collection.find_one({"container_name": tool_info["container_name"]})
        if existing:
            self.collection.update_one({"_id": existing["_id"]}, {"$set": tool_info})
            return existing["_id"]
        else:
            result = self.collection.insert_one(tool_info)
            return result.inserted_id
        
    def get_tool_by_id(self, tool_id: str) -> Optional[Dict]:
        try:
            object_id = ObjectId(tool_id)
            tool = self.collection.find_one({"_id": object_id}, {"_id": 0})
            return tool
        except Exception as e:
            print(f"[ERROR] Invalid tool ID or failed to fetch: {e}")
            return None

    def list_tools(self) -> List[Dict]:
        return list(self.collection.find({}, {"_id": 0}))

    def get_tool(self, container_name: str) -> Optional[Dict]:
        tool = self.collection.find_one({"container_name": container_name}, {"_id": 0})
        return tool

    def remove_tool(self, container_name: str):
        self.collection.delete_one({"container_name": container_name})
