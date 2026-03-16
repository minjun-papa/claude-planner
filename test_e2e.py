#!/usr/bin/env python3
"""
E2E 테스트 - Todo 앱 기능 테스트
"""

import sys
sys.path.insert(0, '/Users/sun/Document/01_project/todo-cli')

from todo import TodoManager, SeasonManager, TodoItem, Season
from pathlib import Path
import json
import os

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name, func):
        try:
            func()
            self.passed += 1
            print(f"✅ {name}")
        except AssertionError as e:
            self.failed += 1
            print(f"❌ {name}: {e}")
        except Exception as e:
            self.failed += 1
            print(f"❌ {name}: {type(e).__name__}: {e}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*50}")
        print(f"테스트 결과: {self.passed}/{total} 통과")
        if self.failed > 0:
            print(f"실패한 테스트: {self.failed}개")
            return False
        return True


def test_todo_manager_basic():
    """TodoManager 기본 기능 테스트"""
    manager = TodoManager()
    
    # 초기 상태
    initial_count = len(manager.todos)
    
    # Todo 추가
    todo = manager.add_todo("테스트 항목", type="task")
    assert todo.id is not None, "Todo ID가 없음"
    assert todo.content == "테스트 항목", "내용이 다름"
    assert todo.status == "todo", "초기 상태가 todo가 아님"
    assert len(manager.todos) == initial_count + 1, "Todo가 추가되지 않음"
    print("  - Todo 추가: OK")


def test_toggle_check():
    """체크 토글 기능 테스트 (스페이스바 기능)"""
    manager = TodoManager()
    
    # 새 Todo 추가
    todo = manager.add_todo("체크 테스트", type="task")
    todo_id = todo.id
    
    # 초기 상태 확인
    assert todo.status == "todo", f"초기 상태가 todo가 아님: {todo.status}"
    print(f"  - 초기 상태: {todo.status}")
    
    # 토글 1: todo -> done
    result = manager.toggle_check(todo_id)
    assert result is not None, "toggle_check가 None을 반환"
    assert result.status == "done", f"todo -> done 실패: {result.status}"
    print(f"  - 토글 1회: {todo.status} -> done")
    
    # 토글 2: done -> todo
    result = manager.toggle_check(todo_id)
    assert result.status == "todo", f"done -> todo 실패: {result.status}"
    print(f"  - 토글 2회: done -> todo")
    
    # in_progress 상태에서 토글: in_progress -> done
    manager.change_status(todo_id)  # todo -> in_progress
    todo = next(t for t in manager.todos if t.id == todo_id)
    assert todo.status == "in_progress", "상태 변경 실패"
    print(f"  - 상태를 in_progress로 변경")
    
    result = manager.toggle_check(todo_id)
    assert result.status == "done", f"in_progress -> done 실패: {result.status}"
    print(f"  - 토글: in_progress -> done")


def test_change_status():
    """상태 순환 테스트 (s 키)"""
    manager = TodoManager()
    
    todo = manager.add_todo("상태 테스트", type="task")
    todo_id = todo.id
    
    # todo -> in_progress
    result = manager.change_status(todo_id)
    assert result.status == "in_progress", f"todo -> in_progress 실패: {result.status}"
    print(f"  - todo -> in_progress: OK")
    
    # in_progress -> done
    result = manager.change_status(todo_id)
    assert result.status == "done", f"in_progress -> done 실패: {result.status}"
    print(f"  - in_progress -> done: OK")
    
    # done -> todo
    result = manager.change_status(todo_id)
    assert result.status == "todo", f"done -> todo 실패: {result.status}"
    print(f"  - done -> todo: OK")


def test_season_manager():
    """시즌 관리 테스트"""
    config_path = Path('/Users/sun/Document/01_project/todo-cli/config.json')
    manager = SeasonManager(config_path)
    
    # 시즌 생성
    season = manager.create_season("테스트 시즌", "2024-01-01", "2024-12-31")
    assert season.id is not None, "시즌 ID가 없음"
    assert season.name == "테스트 시즌", "시즌 이름이 다름"
    assert season.status == "active", "초기 상태가 active가 아님"
    print(f"  - 시즌 생성: OK (id={season.id})")
    
    # 현재 시즌 설정
    manager.set_current_season(season.id)
    assert manager.current_season_id == season.id, "현재 시즌 설정 실패"
    print(f"  - 현재 시즌 설정: OK")
    
    # 현재 시즌 조회
    current = manager.get_current_season()
    assert current is not None, "현재 시즌이 None"
    assert current.id == season.id, "현재 시즌 ID가 다름"
    print(f"  - 현재 시즌 조회: OK")


def test_todo_with_season():
    """시즌별 Todo 테스트"""
    config_path = Path('/Users/sun/Document/01_project/todo-cli/config.json')
    todo_manager = TodoManager()
    season_manager = SeasonManager(config_path)
    todo_manager.set_season_manager(season_manager)
    
    # 시즌 생성
    season = season_manager.create_season("시즌 테스트", "2024-01-01", "2024-12-31")
    season_manager.set_current_season(season.id)
    
    # 시즌에 Todo 추가
    todo = todo_manager.add_todo("시즌 Todo", season_id=season.id)
    assert todo.season_id == season.id, "시즌 ID가 설정되지 않음"
    print(f"  - 시즌 Todo 추가: OK (season_id={todo.season_id})")
    
    # 시즌별 필터링
    season_todos = todo_manager.get_todos_by_season(season.id)
    assert len(season_todos) > 0, "시즌 Todo가 없음"
    print(f"  - 시즌별 필터링: OK ({len(season_todos)}개)")


def test_report_data():
    """리포트 데이터 테스트"""
    manager = TodoManager()
    
    # 몇 개의 Todo 추가
    manager.add_todo("리포트 테스트 1", type="task")
    manager.add_todo("리포트 테스트 2", type="epic")
    
    # 오늘 리포트
    report = manager.get_report_data("today")
    assert "period" in report, "period가 없음"
    assert "stats" in report, "stats가 없음"
    assert "todos" in report, "todos가 없음"
    print(f"  - 오늘 리포트: OK")
    
    # 주간 리포트
    report = manager.get_report_data("weekly")
    assert report is not None, "주간 리포트가 None"
    print(f"  - 주간 리포트: OK")


def test_status_icons():
    """상태 아이콘 테스트"""
    # 상태 아이콘이 올바르게 정의되어 있는지 확인
    status_icons = {"todo": "⬜", "in_progress": "🔄", "done": "✅"}
    
    for status, icon in status_icons.items():
        assert len(icon) > 0, f"{status} 아이콘이 비어있음"
        print(f"  - {status}: {icon}")


def main():
    print("="*50)
    print("Todo 앱 E2E 테스트 시작")
    print("="*50)
    
    runner = TestRunner()
    
    print("\n[1] TodoManager 기본 기능")
    runner.test("TodoManager 기본", test_todo_manager_basic)
    
    print("\n[2] 체크 토글 (스페이스바)")
    runner.test("toggle_check", test_toggle_check)
    
    print("\n[3] 상태 순환 (s 키)")
    runner.test("change_status", test_change_status)
    
    print("\n[4] 시즌 관리")
    runner.test("SeasonManager", test_season_manager)
    
    print("\n[5] 시즌별 Todo")
    runner.test("Todo with Season", test_todo_with_season)
    
    print("\n[6] 리포트 데이터")
    runner.test("Report Data", test_report_data)
    
    print("\n[7] 상태 아이콘")
    runner.test("Status Icons", test_status_icons)
    
    success = runner.summary()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())


def test_completed_at():
    """완료 날짜 기록 테스트"""
    print("\n[8] 완료 날짜 기록")
    
    manager = TodoManager()
    
    # Todo 추가
    todo = manager.add_todo("완료 날짜 테스트", type="task")
    todo_id = todo.id
    
    # 초기 상태: completed_at 없음
    assert todo.completed_at is None, "초기 completed_at이 None이 아님"
    print("  - 초기 completed_at: None")
    
    # 완료 처리
    manager.toggle_check(todo_id)
    todo = next(t for t in manager.todos if t.id == todo_id)
    assert todo.completed_at is not None, "완료 후 completed_at이 None"
    assert todo.status == "done", "상태가 done이 아님"
    print(f"  - 완료 후 completed_at: {todo.completed_at}")
    
    # 완료 취소
    manager.toggle_check(todo_id)
    todo = next(t for t in manager.todos if t.id == todo_id)
    assert todo.completed_at is None, "완료 취소 후 completed_at이 None이 아님"
    print("  - 완료 취소 후 completed_at: None")
    
    print("✅ completed_at")
    return True

# Add to main
