import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

function App() {
  const [tasks, setTasks] = useState([]);
  const [file, setFile] = useState(null);
  const [queueStatus, setQueueStatus] = useState({ active_tasks: 0, queued_tasks: 0 });

  useEffect(() => {
    const interval = setInterval(() => {
      updateTaskStatuses();
      fetchQueueStatus();
    }, 30000); // 30 seconds interval (2 times per minute)
    return () => clearInterval(interval);
  }, []);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Please select a file first!');
      return;
    }
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await axios.post(`${API_URL}/api/upload`, formData);
      setTasks(prevTasks => [...prevTasks, response.data]);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Please try again.');
    }
  };

  const updateTaskStatuses = async () => {
    const updatedTasks = await Promise.all(
      tasks.map(async (task) => {
        if (task.status === 'processing' || task.status === 'queued') {
          try {
            const response = await axios.get(`${API_URL}/api/task/${task.task_id}`);
            return { ...task, ...response.data };
          } catch (error) {
            console.error('Failed to update task status:', error);
            return task;
          }
        }
        return task;
      })
    );
    setTasks(updatedTasks);
  };

  const fetchQueueStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/queue_status`);
      setQueueStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch queue status:', error);
    }
  };

  return (
    <div className="App">
      <h1>Unittest Generator</h1>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload</button>
      <h2>Tasks</h2>
      <ul>
        {tasks.map(task => (
          <li key={task.task_id}>
            Task ID: {task.task_id} - Status: {task.status}
            {task.status === 'completed' && (
              <a href={`${API_URL}/api/download/${task.task_id}`} download> Download</a>
            )}
          </li>
        ))}
      </ul>
      <div>
        <h3>Queue Status</h3>
        <p>Active Tasks: {queueStatus.active_tasks}</p>
        <p>Queued Tasks: {queueStatus.queued_tasks}</p>
      </div>
    </div>
  );
}

export default App;