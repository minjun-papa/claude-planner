#!/usr/bin/env python3
"""
UI 시뮬레이션 테스트
"""

import sys
sys.path.insert(0, '/Users/sun/Document/01_project/todo-cli')

from todo import TodoTree, TodoListScreen, TodoManager, TodoApp
from textual.app import App
from textual.pilot import Pilot
import asyncio

def test_tree_bindings():
    """TodoTree 바인딩 확인"""
    print("="*50)
    print("TodoTree 바인딩 확인")
    print("="*50)
    
    tree = TodoTree("Test")
    
    # 바인딩 확인
    bindings = {b.key: b.action for b in tree.BINDINGS}
    print(f"바인딩: {bindings}")
    
    # 액션 메서드 존재 확인
    actions = ['toggle_todo', 'delete_todo', 'add_todo']
    for action in actions:
        method_name = f'action_{action}'
        if hasattr(tree, method_name):
            print(f"✅ {method_name} 존재")
        else:
            print(f"❌ {method_name} 없음")
            return False
    
    return True


def test_message_posting():
    """메시지 전송 테스트"""
    print("\n" + "="*50)
    print("TodoSelected 메시지 테스트")
    print("="*50)
    
    # TodoSelected 메시지 생성 테스트
    tree = TodoTree("Test")
    msg = TodoTree.TodoSelected(123, "task")
    
    print(f"메시지 todo_id: {msg.todo_id}")
    print(f"메시지 todo_type: {msg.todo_type}")
    
    assert msg.todo_id == 123, "todo_id가 다름"
    assert msg.todo_type == "task", "todo_type이 다름"
    
    print("✅ TodoSelected 메시지 생성 성공")
    return True


def test_selected_todo_state():
    """선택된 Todo 상태 테스트"""
    print("\n" + "="*50)
    print("selected_todo_id 상태 테스트")
    print("="*50)
    
    screen = TodoListScreen()
    
    # reactive 속성 확인
    print(f"selected_todo_id 초기값: {screen.selected_todo_id}")
    
    # 메시지 핸들러 직접 호출
    msg = TodoTree.TodoSelected(999, "epic")
    screen.on_todo_tree_todo_selected(msg)
    
    print(f"메시지 처리 후 selected_todo_id: {screen.selected_todo_id}")
    
    assert screen.selected_todo_id == 999, "selected_todo_id가 업데이트되지 않음"
    assert screen.selected_todo_type == "epic", "selected_todo_type이 업데이트되지 않음"
    
    print("✅ selected_todo_id 상태 테스트 통과")
    return True


def test_action_methods():
    """액션 메서드 테스트"""
    print("\n" + "="*50)
    print("액션 메서드 테스트")
    print("="*50)
    
    screen = TodoListScreen()
    
    # action_toggle 존재 확인
    if hasattr(screen, 'action_toggle'):
        print("✅ action_toggle 존재")
    else:
        print("❌ action_toggle 없음")
        return False
    
    # action_delete 존재 확인
    if hasattr(screen, 'action_delete'):
        print("✅ action_delete 존재")
    else:
        print("❌ action_delete 없음")
        return False
    
    return True


def test_refresh_tree_methods():
    """트리 새로고침 메서드 테스트"""
    print("\n" + "="*50)
    print("트리 새로고침 메서드 테스트")
    print("="*50)
    
    screen = TodoListScreen()
    
    # _get_expanded_nodes 존재 확인
    if hasattr(screen, '_get_expanded_nodes'):
        print("✅ _get_expanded_nodes 존재")
    else:
        print("❌ _get_expanded_nodes 없음")
        return False
    
    # _restore_expanded_nodes 존재 확인
    if hasattr(screen, '_restore_expanded_nodes'):
        print("✅ _restore_expanded_nodes 존재")
    else:
        print("❌ _restore_expanded_nodes 없음")
        return False
    
    return True


def main():
    print("\n" + "="*50)
    print("UI 시뮬레이션 테스트")
    print("="*50 + "\n")
    
    results = []
    
    results.append(("Tree 바인딩", test_tree_bindings()))
    results.append(("메시지 전송", test_message_posting()))
    results.append(("selected_todo 상태", test_selected_todo_state()))
    results.append(("액션 메서드", test_action_methods()))
    results.append(("새로고침 메서드", test_refresh_tree_methods()))
    
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
