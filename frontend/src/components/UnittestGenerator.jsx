import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Typography, Paper, Box, Snackbar, Alert } from '@mui/material';
import { uploadFile, getTaskStatus, getQueueStatus, downloadFile } from '../services/api';
import FileUpload from './FileUpload';
import TaskStatus from './TaskStatus';
import QueueStatus from './QueueStatus';
import { TASK_QUEUED, TASK_RUN, TASK_SUCC, TASK_FAIL , getStatusText} from './taskConstants';

function UnittestGenerator() {
  const [tasks, setTasks] = useState([]);
  const tasksRef = useRef(tasks);
  const [file, setFile] = useState(null);
  const [queueStatus, setQueueStatus] = useState({
      'total_tasks': 0,
      'active_tasks': 0,
      'queued_tasks': 0,
      'completed_tasks': 0,
      'failed_tasks': 0,
  });
  const [isUploading, setIsUploading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  useEffect(() => {
    tasksRef.current = tasks;
  }, [tasks]);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setSnackbar({ open: true, message: 'Please select a file first!', severity: 'warning' });
      return;
    }
    setIsUploading(true);
    try {
      const response = await uploadFile(file);
      setTasks(prevTasks => {
        const newTasks = [...prevTasks, response];
        tasksRef.current = newTasks; // Update the ref
        return newTasks;
      });
      setSnackbar({ open: true, message: 'File uploaded successfully!', severity: 'success' });
    } catch (error) {
      console.error('Upload failed:', error);
      setSnackbar({ open: true, message: 'Upload failed. Please try again.', severity: 'error' });
    } finally {
      setIsUploading(false);
    }
  };

  const updateTaskStatuses = useCallback(async () => {
    const currentTasks = tasksRef.current;
    const updatedTasks = await Promise.all(
      currentTasks.map(async (task) => {
        if (task.status === TASK_QUEUED || task.status === TASK_RUN) {
          try {
            const response = await getTaskStatus(task.task_id);
            return { ...task, ...response };
          } catch (error) {
            console.error(`Failed to update status for task ${task.task_id}:`, error);
            return task;
          }
        }
        return task;
      })
    );

    setTasks(updatedTasks);
    tasksRef.current = updatedTasks; // Update the ref
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      updateTaskStatuses();
      fetchQueueStatus();
    }, 3000);
    return () => clearInterval(interval);
  }, [updateTaskStatuses]);

  const fetchQueueStatus = async () => {
    try {
      const response = await getQueueStatus();
      setQueueStatus(response);
    } catch (error) {
      console.error('Failed to fetch queue status:', error);
      setQueueStatus(prevStatus => ({
        ...prevStatus,
        status: 'error',
        message: 'Failed to fetch queue status'
      }));
    }
  };

  const handleDownload = async (taskId) => {
    try {
      const url = await downloadFile(taskId);
      window.open(url, '_blank');
    } catch (error) {
      console.error('Download failed:', error);
      setSnackbar({ open: true, message: 'Download failed. Please try again.', severity: 'error' });
    }
  };

  return (
    <Box sx={{ my: 4 }}>
      <Typography variant="h2" component="h1" gutterBottom>
        Unittest Generator
      </Typography>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <FileUpload 
          file={file} 
          isUploading={isUploading} 
          handleFileChange={handleFileChange} 
          handleUpload={handleUpload} 
        />
      </Paper>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Tasks
        </Typography>
        <TaskStatus tasks={tasks} handleDownload={handleDownload} />
      </Paper>
      <Paper elevation={3} sx={{ p: 3 }}>
        <QueueStatus queueStatus={queueStatus} />
      </Paper>
      <Snackbar 
        open={snackbar.open} 
        autoHideDuration={6000} 
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default UnittestGenerator;