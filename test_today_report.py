#!/usr/bin/env python3
"""
오늘 리포트 E2E 테스트
"""

import sys
sys.path.insert(0, '/Users/sun/Document/01_project/todo-cli')

from todo import TodoManager, SeasonManager
from datetime import datetime
from pathlib import Path

def test_today_report():
    """오늘 리포트 생성 및 완료된 작업 표시 테스트"""
    print("="*50)
    print("오늘 리포트 E2E 테스트")
    print("="*50)
    
    manager = TodoManager()
    today = datetime.now().strftime("%Y-%m-%d")
    
    print(f"\n오늘 날짜: {today}")
    
    # 1. 오늘 생성한 작업
    print("\n[1] 오늘 생성한 작업 추가...")
    task1 = manager.add_todo("오늘 작업 1", type="task")
    task2 = manager.add_todo("오늘 작업 2", type="task")
    print(f"  - task1 ID: {task1.id}, created_at: {task1.created_at}")
    print(f"  - task2 ID: {task2.id}, created_at: {task2.created_at}")
    
    # 2. 어제 생성한 작업 (비교용)
    print("\n[2] 어제 생성한 작업 추가 (비교용)...")
    task_old = manager.add_todo("어제 작업", type="task")
    # created_at을 어제로 변경
    for t in manager.todos:
        if t.id == task_old.id:
            t.created_at = "2020-01-01"  # 확실히 과거 날짜
    manager._save_todos()
    print(f"  - task_old ID: {task_old.id}, created_at: 2020-01-01")
    
    # 3. 오늘 완료할 작업
    print("\n[3] 오늘 완료할 작업...")
    task_to_complete = manager.add_todo("완료할 작업", type="task")
    # 과거에 생성된 것으로 설정
    for t in manager.todos:
        if t.id == task_to_complete.id:
            t.created_at = "2020-01-01"
    manager._save_todos()
    
    # 완료 처리
    manager.toggle_check(task_to_complete.id)
    completed_task = next(t for t in manager.todos if t.id == task_to_complete.id)
    print(f"  - 완료된 작업 ID: {completed_task.id}")
    print(f"  - created_at: {completed_task.created_at}")
    print(f"  - completed_at: {completed_task.completed_at}")
    print(f"  - status: {completed_task.status}")
    
    # 4. 리포트 데이터 조회
    print("\n[4] 오늘 리포트 데이터 조회...")
    report = manager.get_report_data("today")
    
    print(f"  - period: {report['period']}")
    print(f"  - total: {report['stats']['total']}")
    print(f"  - created_today: {len(report['created_today']) if report['created_today'] else 0}개")
    print(f"  - completed_today: {len(report['completed_today']) if report['completed_today'] else 0}개")
    
    # 5. 검증
    print("\n[5] 검증...")
    
    # created_today 검증
    if report['created_today']:
        print(f"  ✅ created_today 존재: {len(report['created_today'])}개")
        for t in report['created_today']:
            print(f"     - {t.content} (created_at: {t.created_at})")
    else:
        print("  ❌ created_today가 None!")
        return False
    
    # completed_today 검증
    if report['completed_today']:
        print(f"  ✅ completed_today 존재: {len(report['completed_today'])}개")
        for t in report['completed_today']:
            print(f"     - {t.content} (completed_at: {t.completed_at})")
    else:
        print("  ❌ completed_today가 None!")
        return False
    
    # 오늘 생성된 작업이 포함되어 있는지 확인
    created_ids = [t.id for t in report['created_today']]
    if task1.id in created_ids and task2.id in created_ids:
        print(f"  ✅ 오늘 생성한 작업이 created_today에 포함됨")
    else:
        print(f"  ❌ 오늘 생성한 작업이 created_today에 없음")
        print(f"     created_ids: {created_ids}")
        return False
    
    # 오늘 완료된 작업이 포함되어 있는지 확인
    completed_ids = [t.id for t in report['completed_today']]
    if task_to_complete.id in completed_ids:
        print(f"  ✅ 오늘 완료한 작업이 completed_today에 포함됨")
    else:
        print(f"  ❌ 오늘 완료한 작업이 completed_today에 없음")
        print(f"     completed_ids: {completed_ids}")
        return False
    
    # 어제 작업은 포함되지 않아야 함
    if task_old.id not in created_ids and task_old.id not in completed_ids:
        print(f"  ✅ 어제 작업은 포함되지 않음")
    else:
        print(f"  ❌ 어제 작업이 잘못 포함됨")
        return False
    
    print("\n" + "="*50)
    print("✅ 오늘 리포트 테스트 통과!")
    return True


def test_report_data_structure():
    """리포트 데이터 구조 테스트"""
    print("\n" + "="*50)
    print("리포트 데이터 구조 테스트")
    print("="*50)
    
    manager = TodoManager()
    
    # 오늘 작업 추가 및 완료
    task = manager.add_todo("테스트", type="task")
    manager.toggle_check(task.id)
    
    report = manager.get_report_data("today")
    
    # 필수 키 확인
    required_keys = ['period', 'stats', 'todos', 'created_today', 'completed_today']
    for key in required_keys:
        if key in report:
            print(f"  ✅ {key} 존재")
        else:
            print(f"  ❌ {key} 없음!")
            return False
    
    # stats 구조 확인
    required_stats = ['total', 'todo', 'in_progress', 'done', 'completion_rate']
    for stat in required_stats:
        if stat in report['stats']:
            print(f"  ✅ stats.{stat} 존재: {report['stats'][stat]}")
        else:
            print(f"  ❌ stats.{stat} 없음!")
            return False
    
    print("\n✅ 리포트 데이터 구조 테스트 통과!")
    return True


def test_weekly_report_no_today_data():
    """주간 리포트는 created_today/completed_today가 None이어야 함"""
    print("\n" + "="*50)
    print("주간 리포트 데이터 테스트")
    print("="*50)
    
    manager = TodoManager()
    report = manager.get_report_data("weekly")
    
    if report['created_today'] is None and report['completed_today'] is None:
        print("  ✅ 주간 리포트는 created_today/completed_today가 None")
        return True
    else:
        print("  ❌ 주간 리포트에 created_today/completed_today가 있음")
        return False


def main():
    print("\n" + "="*50)
    print("오늘 리포트 E2E 테스트")
    print("="*50 + "\n")
    
    results = []
    
    results.append(("오늘 리포트", test_today_report()))
    results.append(("리포트 데이터 구조", test_report_data_structure()))
    results.append(("주간 리포트", test_weekly_report_no_today_data()))
    
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
