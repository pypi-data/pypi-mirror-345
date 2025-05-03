import re
import os
import json
import operator
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, TypeVar

from civitai_dl.utils.config import CONFIG_DIR  # 添加CONFIG_DIR的导入
from civitai_dl.utils.logger import get_logger  # 使用统一的日志记录器

# 使用项目的日志系统
logger = get_logger(__name__)

# Type variable for flexible return types
T = TypeVar('T')

# Operator mappings as module constants
OPERATORS = {
    "eq": operator.eq,            # Equal
    "ne": operator.ne,            # Not equal
    "lt": operator.lt,            # Less than
    "le": operator.le,            # Less than or equal
    "gt": operator.gt,            # Greater than
    "ge": operator.ge,            # Greater than or equal
    "in": lambda x, y: x in y,    # In collection
    "nin": lambda x, y: x not in y,  # Not in collection
    "contains": lambda x, y: y in x if isinstance(x, str) else False,  # String contains
    "startswith": lambda x, y: x.startswith(y) if isinstance(x, str) else False,  # String starts with
    "endswith": lambda x, y: x.endswith(y) if isinstance(x, str) else False,     # String ends with
    "regex": lambda x, y: bool(re.search(y, x)) if isinstance(x, str) else False,  # Regex match
}

# Logic operators set
LOGIC_OPS = {"and", "or", "not"}


class FilterCondition:
    """Represents a filter condition expression that can be evaluated against data items."""

    def __init__(self, condition: Dict[str, Any]):
        """Initialize and validate a filter condition.

        Args:
            condition: Condition dictionary defining filter rules
        """
        self.condition = condition
        self._validate_condition(condition)

    def _validate_condition(self, condition: Dict[str, Any]) -> None:
        """Validate condition format and structure.

        Args:
            condition: Condition dictionary to validate

        Raises:
            ValueError: When condition format is invalid
        """
        # Check for logic operators
        if any(op in condition for op in LOGIC_OPS):
            # Logic condition
            logic_ops = [op for op in LOGIC_OPS if op in condition]
            if len(logic_ops) != 1:
                raise ValueError(f"Only one logic operator allowed: {condition}")

            logic_op = logic_ops[0]
            if logic_op == "not":
                if not isinstance(condition["not"], dict):
                    raise ValueError(f"'not' operator requires a condition dictionary: {condition}")
            else:  # and, or
                if not isinstance(condition[logic_op], list) or len(condition[logic_op]) < 1:
                    raise ValueError(f"'{logic_op}' operator requires a list of conditions: {condition}")
        else:
            # Simple condition
            if "field" not in condition or "op" not in condition or "value" not in condition:
                raise ValueError(f"Simple condition requires 'field', 'op', and 'value' keys: {condition}")

            if condition["op"] not in OPERATORS:
                raise ValueError(f"Unsupported operator: {condition['op']}")

    def match(self, item: Dict[str, Any]) -> bool:
        """Check if an item matches the condition.

        Args:
            item: Data item to match against the condition

        Returns:
            True if the item matches, False otherwise
        """
        return self._evaluate(self.condition, item)

    def _evaluate(self, condition: Dict[str, Any], item: Dict[str, Any]) -> bool:
        """Recursively evaluate condition against an item.

        Args:
            condition: Condition dictionary or sub-condition
            item: Data item to match

        Returns:
            True if the item matches the condition, False otherwise
        """
        # Handle logic operators
        if "and" in condition:
            return all(self._evaluate(subcond, item) for subcond in condition["and"])

        if "or" in condition:
            return any(self._evaluate(subcond, item) for subcond in condition["or"])

        if "not" in condition:
            return not self._evaluate(condition["not"], item)

        # Handle simple condition
        field = condition["field"]
        op = condition["op"]
        value = condition["value"]

        # Handle nested fields (e.g., "creator.username")
        field_value = item
        for part in field.split('.'):
            if isinstance(field_value, dict) and part in field_value:
                field_value = field_value[part]
            else:
                # If field doesn't exist, consider not a match
                return False

        # Handle type conversion for numerical comparisons
        if isinstance(value, str) and isinstance(field_value, (int, float)):
            try:
                value = type(field_value)(value)
            except (ValueError, TypeError):
                return False

        # Apply operator
        try:
            return OPERATORS[op](field_value, value)
        except Exception as e:
            logger.debug(f"Filter condition evaluation error: {op}({field_value}, {value}): {str(e)}")
            return False


class FilterParser:
    """Filter condition parser for parsing and converting different formats of filter conditions."""

    @staticmethod
    def parse_query_string(query: str) -> Dict[str, Any]:
        """Parse a simple query string into a condition dictionary.

        Args:
            query: Query string (e.g., "type:LORA rating:>4.5")

        Returns:
            Condition dictionary
        """
        if not query.strip():
            return {}

        parts = re.findall(r'([a-zA-Z0-9_.]+)(:([<>]?=?|~|!)?([\w.-]+|\".+?\")|\s+|$)', query)
        conditions = []

        for field, _, op_str, value in parts:
            if not field or not value:
                continue

            # Handle quotes
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]

            # Map operators
            op = "eq"  # Default to equal
            if op_str:
                if op_str == '>':
                    op = "gt"
                elif op_str == '>=':
                    op = "ge"
                elif op_str == '<':
                    op = "lt"
                elif op_str == '<=':
                    op = "le"
                elif op_str == '~':
                    op = "contains"
                elif op_str == '!':
                    op = "ne"

            conditions.append({
                "field": field,
                "op": op,
                "value": value
            })

        # Combine multiple conditions with AND
        if len(conditions) > 1:
            return {"and": conditions}
        elif len(conditions) == 1:
            return conditions[0]
        else:
            return {}

    @staticmethod
    def parse_json(json_str: str) -> Dict[str, Any]:
        """Parse JSON formatted filter condition.

        Args:
            json_str: JSON string

        Returns:
            Condition dictionary

        Raises:
            ValueError: When JSON format is invalid
        """
        try:
            condition = json.loads(json_str)
            # Validate structure
            FilterCondition(condition)
            return condition
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")

    @staticmethod
    def parse_cli_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert CLI parameters to filter condition.

        Args:
            params: CLI parameter dictionary

        Returns:
            Condition dictionary
        """
        conditions = []

        # Map CLI parameters to filter conditions
        mapping = {
            "query": {"field": "name", "op": "contains"},
            "type": {"field": "type", "op": "eq"},
            "creator": {"field": "creator.username", "op": "eq"},
            "tag": {"field": "tags", "op": "in"},
            "base_model": {"field": "modelVersions.baseModel", "op": "eq"},
            "min_rating": {"field": "stats.rating", "op": "ge"},
            "max_rating": {"field": "stats.rating", "op": "le"},
            "min_downloads": {"field": "stats.downloadCount", "op": "ge"},
            "max_downloads": {"field": "stats.downloadCount", "op": "le"},
        }

        for param, value in params.items():
            if param in mapping and value is not None:
                field_map = mapping[param]
                conditions.append({
                    "field": field_map["field"],
                    "op": field_map["op"],
                    "value": value
                })

        # Combine multiple conditions with AND
        if len(conditions) > 1:
            return {"and": conditions}
        elif len(conditions) == 1:
            return conditions[0]
        else:
            return {}

    @staticmethod
    def to_api_params(condition: Dict[str, Any]) -> Dict[str, Any]:
        """Convert filter condition to API parameters.

        Args:
            condition: Filter condition

        Returns:
            API parameter dictionary
        """
        # Handle empty condition
        if not condition:
            return {}

        # Directly map simple condition
        if "field" in condition and "op" in condition and "value" in condition:
            return FilterParser._map_condition_to_param(condition)

        # Handle compound conditions (AND/OR)
        if "and" in condition:
            params = {}
            for subcond in condition["and"]:
                params.update(FilterParser.to_api_params(subcond))
            return params

        if "or" in condition:
            # CivitAI API does not directly support OR, convert only the first condition
            # Remaining conditions need to be filtered on the client side
            if condition["or"]:
                return FilterParser.to_api_params(condition["or"][0])
            return {}

        if "not" in condition:
            # CivitAI API does not directly support NOT, ignore this condition
            # Needs to be filtered on the client side
            return {}

        # Unknown condition type
        return {}

    @staticmethod
    def _map_condition_to_param(condition: Dict[str, Any]) -> Dict[str, Any]:
        """Map a single condition to API parameters.

        Args:
            condition: Single filter condition

        Returns:
            API parameter dictionary
        """
        field = condition["field"]
        op = condition["op"]
        value = condition["value"]

        # Field mapping to API parameters
        field_mapping = {
            "name": "query",
            "types": "types",
            "tag": "tag",
            "sort": "sort",
            "limit": "limit",
            "nsfw": "nsfw",
            "creator.username": "username",
            "modelVersions.baseModel": "baseModel",
            # 其余API参数可按需补充
        }

        # Operator mapping
        op_mapping = {
            "eq": "",     # Directly use value
            "in": "",     # For tags, directly use value
            "contains": "",  # For name, it's the query parameter
        }

        # If field can be mapped to API parameters
        if field in field_mapping:
            param_name = field_mapping[field]

            # If operator supports direct mapping
            if op in op_mapping:
                return {param_name: value}

        # For conditions that cannot be directly mapped, return an empty dictionary
        # These conditions need to be filtered on the client side
        return {}


class FilterManager:
    """筛选条件管理器，用于保存和加载筛选模板和历史记录"""

    def __init__(self, templates_file: Optional[str] = None, history_file: Optional[str] = None):
        """初始化筛选条件管理器

        Args:
            templates_file: 模板文件路径，如果不提供则使用默认路径
            history_file: 历史记录文件路径，如果不提供则使用默认路径
        """
        self.templates_file = templates_file or os.path.join(CONFIG_DIR, "filter_templates.json")
        self.history_file = history_file or os.path.join(CONFIG_DIR, "filter_history.json")
        self.templates = self._load_templates()
        self.history = self._load_history()

    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """加载筛选模板"""
        try:
            if os.path.exists(self.templates_file):
                with open(self.templates_file, "r", encoding="utf-8") as f:
                    templates = json.load(f)
                return templates
            return DEFAULT_TEMPLATES.copy()
        except Exception as e:
            logger.error(f"加载筛选模板失败: {str(e)}")
            return DEFAULT_TEMPLATES.copy()

    def _save_templates(self) -> bool:
        """保存筛选模板"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.templates_file), exist_ok=True)

            with open(self.templates_file, "w", encoding="utf-8") as f:
                json.dump(self.templates, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"保存筛选模板失败: {str(e)}")
            return False

    def _load_history(self) -> List[Dict[str, Any]]:
        """加载筛选历史记录"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
                return history
            return []
        except Exception as e:
            logger.error(f"加载筛选历史记录失败: {str(e)}")
            return []

    def _save_history(self) -> bool:
        """保存筛选历史记录"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)

            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"保存筛选历史记录失败: {str(e)}")
            return False

    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """获取筛选模板

        Args:
            name: 模板名称

        Returns:
            筛选模板字典，如果不存在则返回None
        """
        return self.templates.get(name)

    def get_all_templates(self) -> Dict[str, Dict[str, Any]]:
        """获取所有筛选模板

        Returns:
            所有筛选模板的字典
        """
        return self.templates

    def add_template(self, name: str, condition: Dict[str, Any]) -> bool:
        """添加或更新筛选模板

        Args:
            name: 模板名称
            condition: 筛选条件

        Returns:
            是否成功添加或更新
        """
        self.templates[name] = condition
        return self._save_templates()

    def remove_template(self, name: str) -> bool:
        """删除筛选模板

        Args:
            name: 模板名称

        Returns:
            是否成功删除
        """
        if name in self.templates:
            del self.templates[name]
            return self._save_templates()
        return False

    def add_to_history(self, condition: Dict[str, Any]) -> bool:
        """添加筛选条件到历史记录

        Args:
            condition: 筛选条件

        Returns:
            是否成功添加
        """
        # 添加时间戳
        record = {
            "timestamp": datetime.now().isoformat(),
            "condition": condition
        }

        # 添加到历史记录前面
        self.history.insert(0, record)

        # 限制历史记录数量
        if len(self.history) > 50:
            self.history = self.history[:50]

        return self._save_history()

    def get_history(self) -> List[Dict[str, Any]]:
        """获取筛选历史记录

        Returns:
            筛选历史记录列表
        """
        return self.history

    def clear_history(self) -> bool:
        """清空筛选历史记录

        Returns:
            是否成功清空
        """
        self.history = []
        return self._save_history()

    def list_templates(self) -> Dict[str, Dict[str, Any]]:
        """获取所有模板的列表

        这是get_all_templates的别名，提供更直观的方法名

        Returns:
            模板字典，键为模板名称，值为筛选条件
        """
        return self.get_all_templates()


def apply_filter(items: List[Dict[str, Any]], condition: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply filter condition to a list of items.

    Args:
        items: List of items
        condition: Filter condition

    Returns:
        Filtered list of items
    """
    if not condition:
        return items

    try:
        filter_condition = FilterCondition(condition)
        return [item for item in items if filter_condition.match(item)]
    except Exception as e:
        logger.error(f"Failed to apply filter condition: {str(e)}")
        return items


def sort_results(items: List[Dict[str, Any]], sort_by: str, ascending: bool = False) -> List[Dict[str, Any]]:
    """Sort results.

    Args:
        items: List of items
        sort_by: Sort field
        ascending: Whether to sort in ascending order

    Returns:
        Sorted list of items
    """
    if not sort_by:
        return items

    def get_value(item, field):
        """Safely get the value of a nested field."""
        value = item
        for part in field.split('.'):
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        return value

    try:
        sorted_items = sorted(
            items,
            key=lambda x: (get_value(x, sort_by) is None, get_value(x, sort_by)),
            reverse=not ascending
        )
        return sorted_items
    except Exception as e:
        logger.error(f"Failed to sort: {str(e)}")
        return items


# Sample filter templates
DEFAULT_TEMPLATES = {
    "High Quality LORA": {
        "and": [
            {"field": "type", "op": "eq", "value": "LORA"},
            {"field": "stats.rating", "op": "ge", "value": 4.5},
            {"field": "stats.downloadCount", "op": "ge", "value": 1000}
        ]
    },
    "New Popular Checkpoint": {
        "and": [
            {"field": "type", "op": "eq", "value": "Checkpoint"},
            {"field": "stats.downloadCount", "op": "ge", "value": 500},
            {"field": "publishedAt", "op": "ge", "value": (datetime.now() - timedelta(days=30)).isoformat()}
        ]
    }
}


class FilterBuilder:
    """构建用于API请求的筛选参数"""

    def __init__(self):
        """初始化筛选参数构建器"""

    def build_params(self, condition: Dict[str, Any]) -> Dict[str, Any]:
        """将筛选条件转换为API请求参数

        Args:
            condition: 筛选条件字典

        Returns:
            API请求参数字典
        """
        return FilterParser.to_api_params(condition)


def parse_filter_condition(condition_str: str) -> Dict[str, Any]:
    """解析筛选条件字符串

    支持多种格式：JSON、简单查询字符串等

    Args:
        condition_str: 筛选条件字符串

    Returns:
        解析后的筛选条件字典

    Raises:
        ValueError: 解析失败时
    """
    # 尝试解析为JSON
    if condition_str.strip().startswith("{"):
        try:
            return FilterParser.parse_json(condition_str)
        except ValueError:
            pass

    # 尝试解析为简单查询字符串
    return FilterParser.parse_query_string(condition_str)
