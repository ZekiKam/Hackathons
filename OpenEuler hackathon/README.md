# Run instructions
Currently, you must execute frontend and backend spearately as I have failed to use Docker or `launcher.py` to bundle them :(

1. Run backend, then front end (you'll need one terminal for each, so open two terminal windows)
2. When both frontend and backend are running, open [http://localhost:5173/](http://localhost:5173/) to view UI
3. To stop running, CTRL + C in both running terminals

## Backend
1. If first time running: `pip install -r requirements.txt`
2. `cd backend`
3. `python3 metrics.py`

Backend runs in localhost:5173

When it runs, metrics.csv and metrics.jsonl will appear in Explorer, they will update in real-time.
`rm metric.csv metric.jsonl` to start from row one again the next time running it

## Frontend
1. Might need to install node.js and vite
1. `cd frontend`
2. `npm run dev`

Frintend runs in localhost:8000


