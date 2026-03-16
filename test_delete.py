#!/usr/bin/env python3
"""
삭제 기능 테스트
"""

import sys
sys.path.insert(0, '/Users/sun/Document/01_project/todo-cli')

from todo import TodoManager
import json
from pathlib import Path

def test_delete_single_item():
    """마지막 하나 남은 항목 삭제 테스트"""
    print("="*50)
    print("마지막 항목 삭제 테스트")
    print("="*50)
    
    manager = TodoManager()
    
    # 기존 todos 개수
    initial_count = len(manager.todos)
    print(f"초기 todos 개수: {initial_count}")
    
    # 새 항목 추가
    todo = manager.add_todo("삭제 테스트", type="task")
    todo_id = todo.id
    print(f"추가된 todo ID: {todo_id}")
    print(f"추가 후 개수: {len(manager.todos)}")
    
    # 삭제 실행
    result = manager.delete_todo(todo_id)
    print(f"삭제 결과: {result}")
    print(f"삭제 후 개수: {len(manager.todos)}")
    
    # 삭제 확인
    remaining = [t for t in manager.todos if t.id == todo_id]
    if len(remaining) == 0:
        print("✅ 삭제 성공!")
        return True
    else:
        print("❌ 삭제 실패 - 항목이 여전히 존재함")
        return False


def test_delete_multiple_items():
    """여러 항목 중 하나 삭제 테스트"""
    print("\n" + "="*50)
    print("여러 항목 삭제 테스트")
    print("="*50)
    
    manager = TodoManager()
    
    # 여러 항목 추가
    todo1 = manager.add_todo("항목 1", type="task")
    todo2 = manager.add_todo("항목 2", type="task")
    todo3 = manager.add_todo("항목 3", type="task")
    
    print(f"추가된 항목 IDs: {todo1.id}, {todo2.id}, {todo3.id}")
    print(f"추가 후 개수: {len(manager.todos)}")
    
    # 중간 항목 삭제
    manager.delete_todo(todo2.id)
    print(f"삭제 후 개수: {len(manager.todos)}")
    
    remaining_ids = [t.id for t in manager.todos]
    if todo2.id not in remaining_ids and todo1.id in remaining_ids and todo3.id in remaining_ids:
        print("✅ 중간 항목 삭제 성공!")
        return True
    else:
        print("❌ 삭제 실패")
        return False


def test_delete_with_children():
    """하위 항목이 있는 경우 삭제 테스트"""
    print("\n" + "="*50)
    print("하위 항목 포함 삭제 테스트")
    print("="*50)
    
    manager = TodoManager()
    
    # Epic 추가
    epic = manager.add_todo("Epic", type="epic")
    # Story 추가 (Epic 하위)
    story = manager.add_todo("Story", type="story", parent_id=epic.id)
    # Task 추가 (Story 하위)
    task = manager.add_todo("Task", type="task", parent_id=story.id)
    
    print(f"Epic ID: {epic.id}, Story ID: {story.id}, Task ID: {task.id}")
    print(f"추가 후 개수: {len(manager.todos)}")
    
    # Epic 삭제 (하위 항목도 함께 삭제되어야 함)
    manager.delete_todo(epic.id)
    print(f"Epic 삭제 후 개수: {len(manager.todos)}")
    
    remaining_ids = [t.id for t in manager.todos]
    if epic.id not in remaining_ids and story.id not in remaining_ids and task.id not in remaining_ids:
        print("✅ 하위 항목 포함 삭제 성공!")
        return True
    else:
        print("❌ 삭제 실패 - 하위 항목이 남아있음")
        print(f"남은 IDs: {remaining_ids}")
        return False


def test_delete_last_item_after_others_deleted():
    """다른 항목들 삭제 후 마지막 항목 삭제 테스트"""
    print("\n" + "="*50)
    print("순차적 삭제 후 마지막 항목 삭제 테스트")
    print("="*50)
    
    manager = TodoManager()
    initial_count = len(manager.todos)
    
    # 3개 항목 추가
    todo1 = manager.add_todo("항목 A", type="task")
    todo2 = manager.add_todo("항목 B", type="task")
    todo3 = manager.add_todo("항목 C", type="task")
    
    print(f"추가 후 개수: {len(manager.todos)}")
    
    # 순차적으로 삭제
    manager.delete_todo(todo1.id)
    print(f"항목 A 삭제 후: {len(manager.todos)}개")
    
    manager.delete_todo(todo2.id)
    print(f"항목 B 삭제 후: {len(manager.todos)}개")
    
    # 마지막 항목 삭제
    manager.delete_todo(todo3.id)
    print(f"항목 C 삭제 후: {len(manager.todos)}개")
    
    # 원래 상태로 돌아왔는지 확인
    if len(manager.todos) == initial_count:
        print("✅ 마지막 항목 삭제 성공!")
        return True
    else:
        print(f"❌ 삭제 실패 - 예상: {initial_count}개, 실제: {len(manager.todos)}개")
        return False


def test_save_and_load():
    """삭제 후 저장/로드 테스트"""
    print("\n" + "="*50)
    print("삭제 후 저장/로드 테스트")
    print("="*50)
    
    # 새 매니저 생성
    manager1 = TodoManager()
    
    # 항목 추가
    todo = manager1.add_todo("저장 테스트", type="task")
    todo_id = todo.id
    print(f"추가된 ID: {todo_id}")
    
    # 삭제
    manager1.delete_todo(todo_id)
    print(f"삭제 후 개수: {len(manager1.todos)}")
    
    # 새 매니저 생성해서 다시 로드
    manager2 = TodoManager()
    print(f"새 매니저 로드 후 개수: {len(manager2.todos)}")
    
    # 삭제된 항목이 여전히 있는지 확인
    remaining = [t for t in manager2.todos if t.id == todo_id]
    if len(remaining) == 0:
        print("✅ 저장/로드 후에도 삭제 상태 유지됨!")
        return True
    else:
        print("❌ 저장/로드 후 삭제된 항목이 복원됨")
        return False


def main():
    print("\n" + "="*50)
    print("삭제 기능 종합 테스트")
    print("="*50 + "\n")
    
    results = []
    
    results.append(("단일 항목 삭제", test_delete_single_item()))
    results.append(("여러 항목 중 삭제", test_delete_multiple_items()))
    results.append(("하위 항목 포함 삭제", test_delete_with_children()))
    results.append(("순차적 삭제", test_delete_last_item_after_others_deleted()))
    results.append(("저장/로드", test_save_and_load()))
    
    print("\n" + "="*50)
    print("테스트 결과 요약")
    print("="*50)
    
    passed = 0
    failed = 0
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n총 {passed}/{len(results)} 통과")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
