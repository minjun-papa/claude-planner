#!/usr/bin/env python3
"""
UI 키바인딩 테스트
"""

import sys
sys.path.insert(0, '/Users/sun/Document/01_project/todo-cli')

from todo import TodoListScreen, TodoApp, TodoManager, SeasonManager
from pathlib import Path

def test_keybindings():
    """TodoListScreen 키바인딩 테스트"""
    screen = TodoListScreen()
    
    # BINDINGS 확인
    bindings = screen.BINDINGS
    print("등록된 키바인딩:")
    for b in bindings:
        print(f"  - {b.key}: {b.action}")
    
    # space 키가 있는지 확인
    space_binding = None
    for b in bindings:
        if b.key == "space":
            space_binding = b
            break
    
    if space_binding:
        print(f"\n✅ space 키 발견: action={space_binding.action}")
    else:
        print("\n❌ space 키가 없음!")
        return False
    
    # action_toggle 메서드가 있는지 확인
    if hasattr(screen, 'action_toggle'):
        print("✅ action_toggle 메서드 존재")
    else:
        print("❌ action_toggle 메서드 없음!")
        return False
    
    return True


def test_todo_tree_bindings():
    """TodoTree 키바인딩 테스트 - Tree가 space를 가로채는지 확인"""
    from todo import TodoTree
    
    tree = TodoTree("Test")
    print("\nTodoTree 키바인딩:")
    for b in tree.BINDINGS:
        print(f"  - {b.key}: {b.action}")
    
    # TodoTree에 space 바인딩이 있는지 확인
    has_space = any(b.key == "space" for b in tree.BINDINGS)
    if has_space:
        print("⚠️ TodoTree가 space 키를 사용 중 - 충돌 가능성")
    else:
        print("✅ TodoTree는 space 키를 사용하지 않음")
    
    return True


def test_app_screens():
    """TodoApp에 모든 화면이 등록되어 있는지 확인"""
    app = TodoApp()
    
    print("\n등록된 화면:")
    for name, screen_class in app.SCREENS.items():
        print(f"  - {name}: {screen_class.__name__}")
    
    required_screens = ["main", "add", "add_season", "select_season", "report"]
    for screen_name in required_screens:
        if screen_name not in app.SCREENS:
            print(f"❌ {screen_name} 화면이 없음!")
            return False
    
    print("✅ 모든 화면이 등록되어 있음")
    return True


def main():
    print("="*50)
    print("UI 키바인딩 테스트")
    print("="*50)
    
    all_pass = True
    
    print("\n[1] TodoListScreen 키바인딩")
    if not test_keybindings():
        all_pass = False
    
    print("\n[2] TodoTree 키바인딩")
    if not test_todo_tree_bindings():
        all_pass = False
    
    print("\n[3] TodoApp 화면")
    if not test_app_screens():
        all_pass = False
    
    print("\n" + "="*50)
    if all_pass:
        print("✅ 모든 UI 테스트 통과")
    else:
        print("❌ 일부 테스트 실패")
    
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
