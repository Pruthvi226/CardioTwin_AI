# Migration Note

CardioTwin AI was upgraded from an earlier PPG research repository that contained many one-off audit files, logs, generated reports, and experimental scripts.

This repository now keeps the clean, demo-ready implementation path:

1. `scripts/generate_demo_data.py`
2. `scripts/run_full_pipeline.py`
3. `src/preprocessing/`
4. `src/features/`
5. `src/models/`
6. `src/training/`
7. `src/evaluation/`
8. `src/nlp/`
9. `app/streamlit_app.py`
10. `src/api/main.py`

The older research dump was intentionally removed from the GitHub-ready structure so recruiters and collaborators can evaluate the project quickly.

