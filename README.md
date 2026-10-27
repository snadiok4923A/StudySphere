# StudySphere — Study Planner & Progress Tracker

A Python command-line app for planning subjects, tracking assignments, logging study sessions, and reviewing progress.

## Features
- Subjects with weekly study-hour targets
- Tasks with due dates and priorities
- Mark tasks as complete
- Record study sessions with duration, date, and notes
- Progress summaries by subject and week
- Overdue-task detection
- Local JSON persistence and automated tests

## Requirements
Python 3.9+. No third-party packages.

## Run
```bash
python studysphere.py
```
To choose another data file:
```bash
python studysphere.py --data ./my_study_data.json
```

## Tests
```bash
python -m unittest discover -s tests -v
```

## Structure
```text
StudySphere-Study-Planner/
├── studysphere.py
├── tests/test_studysphere.py
├── README.md
├── LICENSE
└── .gitignore
```

## Privacy
Your records are stored locally in `studysphere_data.json`. Avoid committing personal study notes to a public repository.

## License
MIT. See `LICENSE`.
