"""StudySphere: study planner and progress tracker; standard library only."""
import argparse, json
from datetime import date, datetime, timedelta
from pathlib import Path

DEFAULT_DATA = Path(__file__).resolve().parent / "studysphere_data.json"

def empty_data():
    return {"subjects": [], "tasks": [], "sessions": []}

def load_data(path=DEFAULT_DATA):
    p = Path(path)
    if not p.exists(): return empty_data()
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict): raise ValueError("Invalid data file.")
    for key in ("subjects", "tasks", "sessions"): data.setdefault(key, [])
    return data

def save_data(data, path=DEFAULT_DATA):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def next_id(items):
    return max((x.get("id", 0) for x in items), default=0) + 1

def add_subject(data, name, target_hours=5):
    name = name.strip()
    if not name: raise ValueError("Subject name is required.")
    if any(s["name"].casefold() == name.casefold() for s in data["subjects"]): raise ValueError("Subject already exists.")
    if target_hours <= 0: raise ValueError("Target hours must be positive.")
    item = {"id": next_id(data["subjects"]), "name": name, "target_hours": float(target_hours)}
    data["subjects"].append(item); return item

def add_task(data, title, subject_id, due_date=None, priority="medium"):
    if not title.strip(): raise ValueError("Task title is required.")
    if not any(s["id"] == subject_id for s in data["subjects"]): raise ValueError("Subject not found.")
    if due_date: date.fromisoformat(due_date)
    priority = priority.lower()
    if priority not in {"low", "medium", "high"}: raise ValueError("Priority must be low, medium, or high.")
    item = {"id": next_id(data["tasks"]), "title": title.strip(), "subject_id": subject_id,
            "due_date": due_date or None, "priority": priority, "completed": False,
            "created_at": datetime.now().isoformat(timespec="seconds"), "completed_at": None}
    data["tasks"].append(item); return item

def complete_task(data, task_id):
    for task in data["tasks"]:
        if task["id"] == task_id and not task["completed"]:
            task["completed"] = True; task["completed_at"] = datetime.now().isoformat(timespec="seconds")
            return True
    return False

def add_session(data, subject_id, minutes, session_date=None, note=""):
    if not any(s["id"] == subject_id for s in data["subjects"]): raise ValueError("Subject not found.")
    if not 1 <= minutes <= 1440: raise ValueError("Minutes must be from 1 to 1440.")
    day = date.fromisoformat(session_date or date.today().isoformat()).isoformat()
    item = {"id": next_id(data["sessions"]), "subject_id": subject_id, "minutes": int(minutes), "date": day, "note": note.strip()}
    data["sessions"].append(item); return item

def progress_report(data, today=None):
    today = date.fromisoformat(today) if isinstance(today, str) else (today or date.today())
    subjects = []
    week_start = today - timedelta(days=today.weekday())
    for s in data["subjects"]:
        sessions = [x for x in data["sessions"] if x["subject_id"] == s["id"]]
        total = sum(x["minutes"] for x in sessions)
        weekly = sum(x["minutes"] for x in sessions if week_start <= date.fromisoformat(x["date"]) <= today)
        target = s["target_hours"] * 60
        subjects.append({"name": s["name"], "target_hours": s["target_hours"],
            "total_hours": round(total / 60, 2), "weekly_minutes": weekly,
            "progress_percent": round(min(100, total / target * 100), 1), "session_count": len(sessions)})
    tasks = data["tasks"]
    overdue = [t for t in tasks if not t["completed"] and t["due_date"] and date.fromisoformat(t["due_date"]) < today]
    return {"date": today.isoformat(), "subjects": subjects, "total_tasks": len(tasks),
        "completed_tasks": sum(t["completed"] for t in tasks), "pending_tasks": sum(not t["completed"] for t in tasks),
        "overdue_tasks": len(overdue), "overdue": overdue,
        "total_study_hours": round(sum(x["minutes"] for x in data["sessions"]) / 60, 2)}

def show_report(data):
    r = progress_report(data)
    print("\n========== STUDYSPHERE PROGRESS ==========")
    print(f"Date: {r['date']} | Subjects: {len(r['subjects'])} | Tasks: {r['total_tasks']}")
    print(f"Completed: {r['completed_tasks']} | Pending: {r['pending_tasks']} | Overdue: {r['overdue_tasks']}")
    print(f"Total study time: {r['total_study_hours']} hours")
    print("\nSubject progress:")
    for s in r["subjects"]:
        filled = round(s["progress_percent"] / 5)
        print(f"  {s['name']}: {s['total_hours']}h / {s['target_hours']}h [{'#'*filled}{'-'*(20-filled)}] {s['progress_percent']}%")
        print(f"    This week: {s['weekly_minutes']} minutes across {s['session_count']} sessions")
    for t in r["overdue"]: print(f"OVERDUE: #{t['id']} {t['title']} (due {t['due_date']})")

def menu(path):
    data = load_data(path)
    while True:
        print("\n=== STUDYSPHERE ===\n1 Add subject\n2 Add task\n3 List tasks\n4 Complete task\n5 Log study session\n6 Progress report\n0 Save and exit")
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                raw = input("Weekly target hours [5]: ").strip()
                item = add_subject(data, input("Subject name: "), float(raw) if raw else 5)
                save_data(data, path); print("Added subject #", item["id"])
            elif choice == "2":
                if not data["subjects"]: print("Add a subject first."); continue
                for s in data["subjects"]: print(f"#{s['id']} {s['name']}")
                sid = int(input("Subject ID: ")); title = input("Task title: ")
                due = input("Due date YYYY-MM-DD (blank for none): ").strip() or None
                priority = input("Priority low/medium/high [medium]: ").strip() or "medium"
                item = add_task(data, title, sid, due, priority); save_data(data, path); print("Added task #", item["id"])
            elif choice == "3":
                for t in sorted(data["tasks"], key=lambda x: (x["completed"], x["due_date"] or "9999")):
                    subject = next((s["name"] for s in data["subjects"] if s["id"] == t["subject_id"]), "?")
                    print(f"#{t['id']} [{'DONE' if t['completed'] else 'PENDING'}] [{t['priority']}] {t['title']} — {subject} — {t['due_date'] or 'no due date'}")
                if not data["tasks"]: print("No tasks yet.")
            elif choice == "4":
                print("Completed." if complete_task(data, int(input("Task ID: "))) else "Pending task not found.")
                save_data(data, path)
            elif choice == "5":
                if not data["subjects"]: print("Add a subject first."); continue
                for s in data["subjects"]: print(f"#{s['id']} {s['name']}")
                sid = int(input("Subject ID: ")); minutes = int(input("Minutes studied: "))
                day = input("Date YYYY-MM-DD (blank for today): ").strip() or None
                note = input("Study notes (optional): ")
                add_session(data, sid, minutes, day, note); save_data(data, path); print("Session recorded.")
            elif choice == "6": show_report(data)
            elif choice == "0": save_data(data, path); print("Saved. Keep learning!"); break
            else: print("Choose a valid option.")
        except (ValueError, OSError, KeyError) as e: print("Error:", e)

def main():
    parser = argparse.ArgumentParser(description="StudySphere study planner")
    parser.add_argument("--data", default=str(DEFAULT_DATA), help="JSON data file location")
    menu(parser.parse_args().data)

if __name__ == "__main__": main()
