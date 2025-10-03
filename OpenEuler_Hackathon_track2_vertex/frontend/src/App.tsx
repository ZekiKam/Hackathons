import Dashboard from './components/Dashboard';

function App() {
    return (
        <div className="min-h-screen flex flex-col bg-gray-900 text-white">
            <header className="bg-gray-800 p-4 text-center shadow-md">
                <div className="flex items-center justify-left space-x-2">
 
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-15 h-15 text-white-500">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                    </svg>

                    <h1 className="text-x3">Euler's Eye</h1>
                    <div style={{ marginLeft: "10px" }}></div>
                    <div className="text-xl h-14 content-end">A real-time monitoring application</div>
                </div>
            </header>
            
            <hr />
            
            <main className="flex-grow p-4 text-center text-2x w-full">
                <Dashboard />
            </main>

            <hr />

            <footer className="bg-gray-800 p-2 text-left text-lg text-gray-400">
                &copy; {new Date().getFullYear()} Team Vertex - <a href="https://github.com/compsoc-oe-week/track2_vertex" className="text-blue-500">GitHub</a> - Built for the openEuler OS Hackathon
            </footer>
        </div>
    );
}

export default App;