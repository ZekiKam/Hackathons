# Team Vertex - Track 2 'Euler's Eye'

### Project description:

A concise & easy-to-use monitoring system for the OpenEuler OS that tracks system vitals in real-time, ranging from CPU to Network I/O.

This is paired with a predictive AI model to determine the rate of cache misses, aiming to provide a smoother user experience.

We adopt a *learning based method* for cache replacement, aiming to improve the miss rate of traditional cache replacement policies. 

The strategy is modeled as MDP problem, allowing us to apply Deep Reinforcement learning for decision making. In particular, we use valued based Deep Q Network to learn and optimize the cache replacement strategies.

### Members:
  - Aarav Parin
  - Rory Condict
  - Shashwat Bhatnagar
  - Zeki Kam
  - Zarif Ahmed


### Usage:

**Generating the Miss Rate Predictions**
1. In order to run this program, you need to check vailiabilty of data in csv format.
2. Then we perform preprocessing of the data to reduce the number of features.
3. Run the run_openeuler_filesys.py.

**Running the Backend + Web UI**

Method 1: Using Python Launcher
1. Open the main repository in a terminal (track2_vertex directory)
2. `cd build`
3. `python3 launcher.py`
4. Follow menu instructions (Must select 1 and 2)
5. Open `https://localhost:5173` (try `https://localhost:5174` if 5173 is in use)
6. Startup should be complete, and live metrics should start being displayed!

Method 2: Manual (Development) Setup:
1. Some packages may be missing - if prompted to, make sure to install any missing dependencies
2. Open the main repository in a terminal (track2_vertex directory)
3. Run `cd frontend`
4. Run `npm run dev` to start the frontend
5. Open `https://localhost:5173` (try `https://localhost:5174` if 5173 is in use)
6. The UI should display `System Information: Loading...` - now the backend needs initialising
7. In a separate terminal, run `cd backend` from the main directory
8. Run `python3 metrics.py`
9. The frontend should now connect to and listen to the backend automatically - if not, refresh the webpage
10. Startup should be complete, and live metrics should start being displayed!

