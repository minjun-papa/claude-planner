#!/usr/bin/env python3
"""
스페이스바 기능 실제 테스트
"""

import sys
sys.path.insert(0, '/Users/sun/Document/01_project/todo-cli')

from todo import TodoManager, TodoTree, TodoListScreen
from textual.app import App
from textual.pilot import Pilot

def test_space_key_directly():
    """toggle_check 직접 호출 테스트"""
    print("스페이스바 기능 직접 테스트")
    print("="*50)
    
    manager = TodoManager()
    
    # 테스트용 Todo 추가
    todo = manager.add_todo("스페이스바 테스트", type="task")
    todo_id = todo.id
    
    print(f"1. 초기 상태: {todo.status}")
    assert todo.status == "todo", "초기 상태가 todo가 아님"
    
    # toggle_check 호출 (스페이스바가 하는 일)
    result = manager.toggle_check(todo_id)
    todo = next(t for t in manager.todos if t.id == todo_id)
    print(f"2. toggle_check 1회 후: {todo.status}")
    assert todo.status == "done", f"done이어야 함: {todo.status}"
    
    # 다시 toggle_check 호출
    result = manager.toggle_check(todo_id)
    todo = next(t for t in manager.todos if t.id == todo_id)
    print(f"3. toggle_check 2회 후: {todo.status}")
    assert todo.status == "todo", f"todo이어야 함: {todo.status}"
    
    print("\n✅ 스페이스바 기능 정상 작동!")
    return True

def test_tree_action_toggle():
    """TodoTree의 action_toggle_todo 테스트"""
    print("\nTodoTree action_toggle_todo 테스트")
    print("="*50)
    
    # TodoTree 생성
    tree = TodoTree("Test Tree")
    
    # action_toggle_todo 메서드 존재 확인
    if hasattr(tree, 'action_toggle_todo'):
        print("✅ TodoTree.action_toggle_todo 메서드 존재")
    else:
        print("❌ TodoTree.action_toggle_todo 메서드 없음")
        return False
    
    # BINDINGS에 space가 있는지 확인
    has_space = any(b.key == "space" for b in tree.BINDINGS)
    if has_space:
        print("✅ TodoTree BINDINGS에 space 키 있음")
    else:
        print("❌ TodoTree BINDINGS에 space 키 없음")
        return False
    
    return True

def main():
    print("="*50)
    print("스페이스바 기능 종합 테스트")
    print("="*50)
    
    success = True
    
    if not test_space_key_directly():
        success = False
    
    if not test_tree_action_toggle():
        success = False
    
    print("\n" + "="*50)
    if success:
        print("✅ 모든 스페이스바 테스트 통과")
        print("\n이제 앱에서 스페이스바를 누르면:")
        print("  ⬜ (todo) → ✅ (done)")
        print("  ✅ (done) → ⬜ (todo)")
    else:
        print("❌ 일부 테스트 실패")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
