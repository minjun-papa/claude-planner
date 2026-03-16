#!/usr/bin/env python3
"""
종합 E2E 테스트 - 실제 사용 시나리오 테스트
"""

import sys
sys.path.insert(0, '/Users/sun/Document/01_project/todo-cli')

from todo import TodoManager, SeasonManager, TodoItem
from pathlib import Path

def test_subtask_toggle():
    """하위 태스크 체크/언체크 테스트"""
    print("="*50)
    print("하위 태스크 체크/언체크 테스트")
    print("="*50)
    
    manager = TodoManager()
    
    # Epic 생성
    epic = manager.add_todo("Epic 테스트", type="epic")
    print(f"Epic 생성: ID={epic.id}")
    
    # Story 생성 (Epic 하위)
    story = manager.add_todo("Story 테스트", type="story", parent_id=epic.id)
    print(f"Story 생성: ID={story.id}, parent_id={story.parent_id}")
    
    # Task 생성 (Story 하위)
    task = manager.add_todo("Task 테스트", type="task", parent_id=story.id)
    print(f"Task 생성: ID={task.id}, parent_id={task.parent_id}")
    
    # Task 체크
    result = manager.toggle_check(task.id)
    task = next(t for t in manager.todos if t.id == task.id)
    print(f"Task 체크 후 상태: {task.status}")
    assert task.status == "done", "Task가 done이 아님"
    
    # Task 언체크
    result = manager.toggle_check(task.id)
    task = next(t for t in manager.todos if t.id == task.id)
    print(f"Task 언체크 후 상태: {task.status}")
    assert task.status == "todo", "Task가 todo가 아님"
    
    # 모든 항목이 여전히 존재하는지 확인
    all_ids = [t.id for t in manager.todos]
    assert epic.id in all_ids, "Epic이 사라짐"
    assert story.id in all_ids, "Story가 사라짐"
    assert task.id in all_ids, "Task가 사라짐"
    
    print("✅ 하위 태스크 체크/언체크 테스트 통과")
    return True


def test_delete_epic_with_children():
    """Epic 삭제 시 하위 항목도 함께 삭제되는지 테스트"""
    print("\n" + "="*50)
    print("Epic 삭제 테스트 (하위 항목 포함)")
    print("="*50)
    
    manager = TodoManager()
    initial_count = len(manager.todos)
    
    # Epic 생성
    epic = manager.add_todo("삭제용 Epic", type="epic")
    
    # Story 생성 (Epic 하위)
    story1 = manager.add_todo("Story 1", type="story", parent_id=epic.id)
    story2 = manager.add_todo("Story 2", type="story", parent_id=epic.id)
    
    # Task 생성 (Story 하위)
    task1 = manager.add_todo("Task 1", type="task", parent_id=story1.id)
    task2 = manager.add_todo("Task 2", type="task", parent_id=story2.id)
    
    print(f"생성된 항목: Epic={epic.id}, Stories={story1.id},{story2.id}, Tasks={task1.id},{task2.id}")
    print(f"생성 후 개수: {len(manager.todos)}")
    
    # Epic 삭제
    manager.delete_todo(epic.id)
    print(f"삭제 후 개수: {len(manager.todos)}")
    
    # 모든 항목이 삭제되었는지 확인
    all_ids = [t.id for t in manager.todos]
    assert epic.id not in all_ids, f"Epic이 삭제되지 않음: {epic.id}"
    assert story1.id not in all_ids, f"Story1이 삭제되지 않음: {story1.id}"
    assert story2.id not in all_ids, f"Story2이 삭제되지 않음: {story2.id}"
    assert task1.id not in all_ids, f"Task1이 삭제되지 않음: {task1.id}"
    assert task2.id not in all_ids, f"Task2이 삭제되지 않음: {task2.id}"
    
    assert len(manager.todos) == initial_count, f"개수가 맞지 않음: 예상={initial_count}, 실제={len(manager.todos)}"
    
    print("✅ Epic 삭제 테스트 통과")
    return True


def test_delete_middle_item():
    """중간 항목(Story) 삭제 테스트"""
    print("\n" + "="*50)
    print("Story 삭제 테스트")
    print("="*50)
    
    manager = TodoManager()
    
    # Epic 생성
    epic = manager.add_todo("Epic", type="epic")
    
    # Story 2개 생성
    story1 = manager.add_todo("Story 1", type="story", parent_id=epic.id)
    story2 = manager.add_todo("Story 2", type="story", parent_id=epic.id)
    
    # Task 생성
    task1 = manager.add_todo("Task 1", type="task", parent_id=story1.id)
    task2 = manager.add_todo("Task 2", type="task", parent_id=story2.id)
    
    initial_count = len(manager.todos)
    print(f"생성 후 개수: {initial_count}")
    
    # Story1 삭제 (Task1도 함께 삭제되어야 함)
    manager.delete_todo(story1.id)
    print(f"Story1 삭제 후 개수: {len(manager.todos)}")
    
    all_ids = [t.id for t in manager.todos]
    assert epic.id in all_ids, "Epic이 삭제됨"
    assert story1.id not in all_ids, "Story1이 삭제되지 않음"
    assert task1.id not in all_ids, "Task1이 삭제되지 않음"
    assert story2.id in all_ids, "Story2이 삭제됨"
    assert task2.id in all_ids, "Task2이 삭제됨"
    
    print("✅ Story 삭제 테스트 통과")
    return True


def test_delete_single_task():
    """단일 Task 삭제 테스트"""
    print("\n" + "="*50)
    print("단일 Task 삭제 테스트")
    print("="*50)
    
    manager = TodoManager()
    initial_count = len(manager.todos)
    
    # Epic, Story, Task 생성
    epic = manager.add_todo("Epic", type="epic")
    story = manager.add_todo("Story", type="story", parent_id=epic.id)
    task = manager.add_todo("Task", type="task", parent_id=story.id)
    
    print(f"생성 후 개수: {len(manager.todos)}")
    
    # Task만 삭제
    manager.delete_todo(task.id)
    print(f"Task 삭제 후 개수: {len(manager.todos)}")
    
    all_ids = [t.id for t in manager.todos]
    assert epic.id in all_ids, "Epic이 삭제됨"
    assert story.id in all_ids, "Story가 삭제됨"
    assert task.id not in all_ids, "Task가 삭제되지 않음"
    
    assert len(manager.todos) == initial_count + 2, f"개수가 맞지 않음: 예상={initial_count + 2}, 실제={len(manager.todos)}"
    
    print("✅ 단일 Task 삭제 테스트 통과")
    return True


def test_hierarchical_structure():
    """계층 구조 테스트"""
    print("\n" + "="*50)
    print("계층 구조 테스트")
    print("="*50)
    
    manager = TodoManager()
    
    # Epic
    epic = manager.add_todo("Epic", type="epic")
    
    # Story under Epic
    story = manager.add_todo("Story", type="story", parent_id=epic.id)
    
    # Task under Story
    task = manager.add_todo("Task", type="task", parent_id=story.id)
    
    # 계층 확인
    root_items = manager.get_root_items()
    print(f"Root 항목 수: {len(root_items)}")
    assert len(root_items) > 0, "Root 항목이 없음"
    
    epic_children = manager.get_children(epic.id)
    print(f"Epic 하위 항목: {[t.content for t in epic_children]}")
    assert len(epic_children) == 1, "Epic 하위에 Story가 1개가 아님"
    
    story_children = manager.get_children(story.id)
    print(f"Story 하위 항목: {[t.content for t in story_children]}")
    assert len(story_children) == 1, "Story 하위에 Task가 1개가 아님"
    
    print("✅ 계층 구조 테스트 통과")
    return True


def test_selected_todo_id_tracking():
    """선택된 Todo ID 추적 테스트"""
    print("\n" + "="*50)
    print("선택된 Todo ID 추적 테스트")
    print("="*50)
    
    manager = TodoManager()
    
    # 항목 생성
    epic = manager.add_todo("Epic", type="epic")
    task = manager.add_todo("Task", type="task", parent_id=epic.id)
    
    # Task 체크/언체크 후에도 ID가 유효한지 확인
    selected_id = task.id
    manager.toggle_check(selected_id)
    
    # 해당 ID의 todo 찾기
    found = next((t for t in manager.todos if t.id == selected_id), None)
    assert found is not None, "체크 후 todo를 찾을 수 없음"
    assert found.status == "done", "상태가 done이 아님"
    
    # 언체크
    manager.toggle_check(selected_id)
    found = next((t for t in manager.todos if t.id == selected_id), None)
    assert found is not None, "언체크 후 todo를 찾을 수 없음"
    assert found.status == "todo", "상태가 todo가 아님"
    
    print("✅ 선택된 Todo ID 추적 테스트 통과")
    return True


def main():
    print("\n" + "="*50)
    print("종합 E2E 테스트")
    print("="*50 + "\n")
    
    results = []
    
    results.append(("하위 태스크 체크/언체크", test_subtask_toggle()))
    results.append(("Epic 삭제 (하위 포함)", test_delete_epic_with_children()))
    results.append(("Story 삭제", test_delete_middle_item()))
    results.append(("단일 Task 삭제", test_delete_single_task()))
    results.append(("계층 구조", test_hierarchical_structure()))
    results.append(("선택 ID 추적", test_selected_todo_id_tracking()))
    
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
