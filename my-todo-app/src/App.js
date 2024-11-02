import React, { useState, useEffect } from 'react';
import './App.css';
import Login from './components/Login';
import { Link } from 'react-router-dom';
import axiosInstance from './axiosInstance';

function App() {
  const [tasks, setTasks] = useState([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      axiosInstance.get('/tasks')
        .then(response => {
          console.log('Fetched tasks:', response.data);
          setTasks(response.data);
        })
        .catch(error => {
          console.error('Error fetching tasks:', error);
        });
    }
  }, [isAuthenticated]);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  return (
    <div>
      <h1>Todo List</h1>
      {!isAuthenticated ? (
        <div>
          <Login onLogin={handleLogin} />
          <p>Don't have an account? <Link to="/register">Register here</Link></p>
        </div>
      ) : (
        <ul>
          {tasks.map(task => (
            <li key={task.id}>
              <h2>{task.title}</h2>
              <p>Status: {task.is_completed ? 'Completed' : 'Incomplete'}</p>
              {task.subtasks.length > 0 && (
                <ul>
                  {task.subtasks.map(subtask => (
                    <li key={subtask.id}>
                      {subtask.title} - {subtask.is_completed ? 'Completed' : 'Incomplete'}
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;