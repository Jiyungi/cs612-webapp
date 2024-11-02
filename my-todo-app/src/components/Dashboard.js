import React, { useState, useEffect } from 'react';
import axiosInstance from '../axiosInstance';

function Dashboard() {
  const [todoLists, setTodoLists] = useState([]);

  useEffect(() => {
    axiosInstance.get('/dashboard')
      .then(response => {
        setTodoLists(response.data.todo_lists);
      })
      .catch(error => {
        console.error('Error fetching todo lists:', error);
      });
  }, []);

  return (
    <div>
      <h1>Your Todo Lists</h1>
      <ul>
        {todoLists.map(list => (
          <li key={list.id}>{list.name}</li>
        ))}
      </ul>
    </div>
  );
}

export default Dashboard; 