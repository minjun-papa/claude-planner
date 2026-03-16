#!/usr/bin/env python3
"""
Jira API Client for Todo App
Handles all Jira REST API interactions
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    print("requests 라이브러리가 필요합니다.")
    print("설치: pip install requests")
    exit(1)


@dataclass
class JiraConfig:
    """Jira 설정 데이터 클래스"""
    enabled: bool = False
    base_url: str = ""
    email: str = ""
    api_token: str = ""
    project_key: str = ""

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "base_url": self.base_url,
            "email": self.email,
            "api_token": self.api_token,
            "project_key": self.project_key
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'JiraConfig':
        return cls(
            enabled=data.get("enabled", False),
            base_url=data.get("base_url", ""),
            email=data.get("email", ""),
            api_token=data.get("api_token", ""),
            project_key=data.get("project_key", "")
        )

    def is_valid(self) -> bool:
        """필수 설정값이 모두 있는지 확인"""
        return all([
            self.base_url,
            self.email,
            self.api_token,
            self.project_key
        ])


class JiraClient:
    """Jira REST API 클라이언트"""

    # Todo 상태 -> Jira 상태 매핑
    STATUS_MAP = {
        "todo": "To Do",
        "in_progress": "In Progress",
        "done": "Done"
    }

    # Jira 상태 -> Todo 상태 매핑 (역매핑)
    STATUS_MAP_REVERSE = {
        "to do": "todo",
        "in progress": "in_progress",
        "done": "done"
    }

    # Todo 타입 -> Jira 이슈 타입 매핑
    TYPE_MAP = {
        "epic": "Epic",
        "story": "Story",
        "task": "Task"
    }

    # Jira 이슈 타입 -> Todo 타입 매핑 (역매핑)
    TYPE_MAP_REVERSE = {
        "epic": "epic",
        "story": "story",
        "task": "task",
        "sub-task": "task",
        "bug": "task"
    }

    def __init__(self, config: JiraConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.auth = HTTPBasicAuth(config.email, config.api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self._transition_cache: Dict[str, List[dict]] = {}

    def _get_url(self, endpoint: str) -> str:
        """API URL 생성"""
        return f"{self.base_url}/rest/api/3/{endpoint}"

    def _handle_response(self, response: requests.Response) -> dict:
        """응답 처리"""
        if response.status_code >= 400:
            error_msg = f"Jira API Error: {response.status_code}"
            try:
                error_data = response.json()
                if "errorMessages" in error_data:
                    error_msg += f" - {', '.join(error_data['errorMessages'])}"
                elif "errors" in error_data:
                    error_msg += f" - {error_data['errors']}"
            except:
                error_msg += f" - {response.text}"
            raise Exception(error_msg)
        return response.json()

    def test_connection(self) -> tuple[bool, str]:
        """
        Jira 연결 테스트
        Returns: (success, message)
        """
        try:
            # 내 정보 조회로 연결 테스트
            response = requests.get(
                self._get_url("myself"),
                headers=self.headers,
                auth=self.auth
            )

            if response.status_code == 200:
                data = response.json()
                return True, f"연결 성공: {data.get('displayName', data.get('emailAddress', 'Unknown'))}"

            return False, f"연결 실패: {response.status_code} - {response.text}"

        except requests.exceptions.ConnectionError:
            return False, "연결 실패: 네트워크 오류 (URL 확인)"
        except requests.exceptions.Timeout:
            return False, "연결 실패: 타임아웃"
        except Exception as e:
            return False, f"연결 실패: {str(e)}"

    def test_project(self) -> tuple[bool, str]:
        """
        프로젝트 접근 테스트
        Returns: (success, message)
        """
        try:
            response = requests.get(
                self._get_url(f"project/{self.config.project_key}"),
                headers=self.headers,
                auth=self.auth
            )

            if response.status_code == 200:
                data = response.json()
                return True, f"프로젝트: {data.get('name', self.config.project_key)}"

            return False, f"프로젝트 접근 실패: {response.status_code}"

        except Exception as e:
            return False, f"프로젝트 접근 실패: {str(e)}"

    def create_issue(self, todo_data: dict) -> dict:
        """
        Jira 이슈 생성
        Args:
            todo_data: {
                "content": str,        # summary
                "type": str,           # issuetype (epic/story/task)
                "priority": str,       # priority
                "due_date": str,       # duedate (YYYY-MM-DD)
                "parent_key": str,     # parent issue key (Epic Link)
                "description": str     # description (optional)
            }
        Returns:
            {"key": "PROJ-123", "id": "10001"}
        """
        issue_type = self.TYPE_MAP.get(todo_data.get("type", "task"), "Task")

        fields = {
            "project": {
                "key": self.config.project_key
            },
            "summary": todo_data.get("content", ""),
            "issuetype": {
                "name": issue_type
            }
        }

        # 우선순위 설정
        priority = todo_data.get("priority", "medium")
        priority_map = {"high": "High", "medium": "Medium", "low": "Low"}
        if priority in priority_map:
            fields["priority"] = {"name": priority_map[priority]}

        # 마감일 설정
        due_date = todo_data.get("due_date")
        if due_date:
            fields["duedate"] = due_date

        # 설명 설정
        description = todo_data.get("description")
        if description:
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ]
                    }
                ]
            }

        # Epic Link 설정 (Story/Task가 Epic 하위인 경우)
        parent_key = todo_data.get("parent_key")
        if parent_key and issue_type in ["Story", "Task"]:
            # Epic Link 필드는 커스텀 필드 ID가 필요할 수 있음
            # 일반적으로는 parent 필드 사용
            fields["parent"] = {"key": parent_key}

        payload = {"fields": fields}

        response = requests.post(
            self._get_url("issue"),
            headers=self.headers,
            auth=self.auth,
            json=payload
        )

        result = self._handle_response(response)
        return {
            "key": result.get("key"),
            "id": result.get("id")
        }

    def update_issue(self, issue_key: str, todo_data: dict) -> bool:
        """
        Jira 이슈 업데이트
        Args:
            issue_key: Jira 이슈 키 (예: PROJ-123)
            todo_data: 업데이트할 필드들
        Returns:
            True if successful
        """
        fields = {}

        if "content" in todo_data:
            fields["summary"] = todo_data["content"]

        if "priority" in todo_data:
            priority_map = {"high": "High", "medium": "Medium", "low": "Low"}
            if todo_data["priority"] in priority_map:
                fields["priority"] = {"name": priority_map[todo_data["priority"]]}

        if "due_date" in todo_data:
            fields["duedate"] = todo_data["due_date"]

        if not fields:
            return True  # 업데이트할 필드 없음

        payload = {"fields": fields}

        response = requests.put(
            self._get_url(f"issue/{issue_key}"),
            headers=self.headers,
            auth=self.auth,
            json=payload
        )

        # 204 No Content is success
        if response.status_code == 204:
            return True

        self._handle_response(response)
        return True

    def get_issue(self, issue_key: str) -> dict:
        """
        단일 Jira 이슈 조회
        Returns:
            {
                "key": "PROJ-123",
                "id": "10001",
                "summary": "이슈 제목",
                "status": "To Do",
                "type": "Task",
                "priority": "Medium",
                "due_date": "2024-01-01",
                "parent_key": "PROJ-100",
                "created": "2024-01-01T00:00:00.000+0000",
                "updated": "2024-01-01T00:00:00.000+0000"
            }
        """
        response = requests.get(
            self._get_url(f"issue/{issue_key}"),
            headers=self.headers,
            auth=self.auth,
            params={"fields": "summary,status,issuetype,priority,duedate,parent,created,updated"}
        )

        result = self._handle_response(response)
        fields = result.get("fields", {})

        return {
            "key": result.get("key"),
            "id": result.get("id"),
            "summary": fields.get("summary", ""),
            "status": fields.get("status", {}).get("name", ""),
            "type": fields.get("issuetype", {}).get("name", "Task"),
            "priority": fields.get("priority", {}).get("name", "Medium") if fields.get("priority") else "Medium",
            "due_date": fields.get("duedate"),
            "parent_key": fields.get("parent", {}).get("key") if fields.get("parent") else None,
            "created": fields.get("created"),
            "updated": fields.get("updated")
        }

    def get_issues(self, jql: Optional[str] = None, max_results: int = 100) -> List[dict]:
        """
        Jira 이슈 목록 조회
        Args:
            jql: JQL 쿼리 (기본: 프로젝트의 모든 이슈)
            max_results: 최대 결과 수
        Returns:
            이슈 목록
        """
        if jql is None:
            jql = f"project = {self.config.project_key} ORDER BY created DESC"

        response = requests.get(
            self._get_url("search"),
            headers=self.headers,
            auth=self.auth,
            params={
                "jql": jql,
                "maxResults": max_results,
                "fields": "summary,status,issuetype,priority,duedate,parent,created,updated"
            }
        )

        result = self._handle_response(response)
        issues = []

        for issue in result.get("issues", []):
            fields = issue.get("fields", {})
            issues.append({
                "key": issue.get("key"),
                "id": issue.get("id"),
                "summary": fields.get("summary", ""),
                "status": fields.get("status", {}).get("name", ""),
                "type": fields.get("issuetype", {}).get("name", "Task"),
                "priority": fields.get("priority", {}).get("name", "Medium") if fields.get("priority") else "Medium",
                "due_date": fields.get("duedate"),
                "parent_key": fields.get("parent", {}).get("key") if fields.get("parent") else None,
                "created": fields.get("created"),
                "updated": fields.get("updated")
            })

        return issues

    def get_transitions(self, issue_key: str) -> List[dict]:
        """
        이슈의 가능한 상태 전환 목록 조회
        Returns:
            [{"id": "11", "name": "To Do"}, {"id": "21", "name": "In Progress"}, ...]
        """
        if issue_key in self._transition_cache:
            return self._transition_cache[issue_key]

        response = requests.get(
            self._get_url(f"issue/{issue_key}/transitions"),
            headers=self.headers,
            auth=self.auth
        )

        result = self._handle_response(response)
        transitions = [
            {"id": t.get("id"), "name": t.get("to", {}).get("name")}
            for t in result.get("transitions", [])
        ]

        self._transition_cache[issue_key] = transitions
        return transitions

    def transition_issue(self, issue_key: str, target_status: str) -> bool:
        """
        이슈 상태 변경
        Args:
            issue_key: Jira 이슈 키
            target_status: 목표 상태 (todo/in_progress/done)
        Returns:
            True if successful
        """
        # Todo 상태를 Jira 상태명으로 변환
        jira_status = self.STATUS_MAP.get(target_status, target_status)

        # 가능한 전환 목록 조회
        transitions = self.get_transitions(issue_key)

        # 목표 상태에 해당하는 전환 ID 찾기
        transition_id = None
        for t in transitions:
            if t["name"].lower() == jira_status.lower():
                transition_id = t["id"]
                break

        if not transition_id:
            # 정확히 일치하지 않으면 유사한 이름 검색
            for t in transitions:
                if jira_status.lower() in t["name"].lower():
                    transition_id = t["id"]
                    break

        if not transition_id:
            raise Exception(f"전환을 찾을 수 없음: {jira_status}")

        payload = {
            "transition": {
                "id": transition_id
            }
        }

        response = requests.post(
            self._get_url(f"issue/{issue_key}/transitions"),
            headers=self.headers,
            auth=self.auth,
            json=payload
        )

        # 204 No Content is success
        if response.status_code == 204:
            # 캐시 무효화
            if issue_key in self._transition_cache:
                del self._transition_cache[issue_key]
            return True

        self._handle_response(response)
        return True

    def delete_issue(self, issue_key: str) -> bool:
        """
        이슈 삭제
        Note: 일반적으로 Jira에서는 이슈 삭제가 제한됨
        Returns:
            True if successful
        """
        response = requests.delete(
            self._get_url(f"issue/{issue_key}"),
            headers=self.headers,
            auth=self.auth
        )

        # 204 No Content is success
        if response.status_code == 204:
            return True

        self._handle_response(response)
        return True

    def convert_jira_to_todo(self, jira_issue: dict) -> dict:
        """
        Jira 이슈를 Todo 데이터로 변환
        Args:
            jira_issue: get_issue() 또는 get_issues()의 결과
        Returns:
            TodoItem 생성에 사용할 수 있는 dict
        """
        # 상태 변환
        status = jira_issue.get("status", "").lower()
        todo_status = self.STATUS_MAP_REVERSE.get(status, "todo")

        # 타입 변환
        issue_type = jira_issue.get("type", "Task").lower()
        todo_type = self.TYPE_MAP_REVERSE.get(issue_type, "task")

        # 우선순위 변환
        priority = jira_issue.get("priority", "Medium").lower()
        priority_map = {"high": "high", "highest": "high", "medium": "medium", "low": "low", "lowest": "low"}
        todo_priority = priority_map.get(priority, "medium")

        return {
            "content": jira_issue.get("summary", ""),
            "type": todo_type,
            "status": todo_status,
            "priority": todo_priority,
            "due_date": jira_issue.get("due_date"),
            "jira_key": jira_issue.get("key"),
            "jira_id": jira_issue.get("id"),
            "parent_key": jira_issue.get("parent_key"),
            "created_at": jira_issue.get("created", "")[:10] if jira_issue.get("created") else None
        }


def create_jira_client_from_config(config_path: str) -> Optional[JiraClient]:
    """
    설정 파일에서 JiraClient 생성
    Args:
        config_path: config.json 경로
    Returns:
        JiraClient 인스턴스 또는 None (Jira가 비활성화된 경우)
    """
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        jira_config = config.get("jira", {})
        if not jira_config.get("enabled", False):
            return None

        jira_config_obj = JiraConfig.from_dict(jira_config)
        if not jira_config_obj.is_valid():
            return None

        return JiraClient(jira_config_obj)

    except Exception as e:
        print(f"Jira 설정 로드 실패: {e}")
        return None
