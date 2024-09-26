import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Typography, 
  Button, 
  List, 
  ListItem, 
  ListItemText, 
  Paper, 
  Box,
  CircularProgress,
  Snackbar,
  Alert,
  Chip
} from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { uploadFile, getTaskStatus, getQueueStatus, downloadFile } from '../services/api';

const Input = styled('input')({
  display: 'none',
});

// Define task status constants
const TASK_QUEUED = "0";
const TASK_RUN = "1";
const TASK_SUCC = "2";
const TASK_FAIL = "3";

function getStatusText(status) {
  switch (status) {
    case TASK_QUEUED:
      return 'Queued';
    case TASK_RUN:
      return 'Running';
    case TASK_SUCC:
      return 'Completed';
    case TASK_FAIL:
      return 'Failed';
    default:
      return 'Unknown';
  }
}

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
        <Input
          accept=".java,.py,.js,.ts"
          id="contained-button-file"
          type="file"
          onChange={handleFileChange}
        />
        <label htmlFor="contained-button-file">
          <Button
            variant="contained"
            component="span"
            startIcon={<CloudUploadIcon />}
            sx={{ mr: 2 }}
          >
            Select File
          </Button>
        </label>
        <Button
          onClick={handleUpload}
          variant="contained"
          color="primary"
          disabled={!file || isUploading}
        >
          {isUploading ? <CircularProgress size={24} /> : 'Upload'}
        </Button>
        {file && <Typography variant="body2" sx={{ mt: 2 }}>Selected file: {file.name}</Typography>}
      </Paper>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Tasks
        </Typography>
        <List>
          {Array.isArray(tasks) && tasks.map(task => (
            <ListItem key={task.task_id}>
              <ListItemText
                primary={`Task ID: ${task.task_id}`}
                secondary={`Status: ${getStatusText(task.status)}, Filename: ${task.filename}`}
              />
              {task.status === TASK_SUCC && (
                <Button 
                  variant="outlined" 
                  onClick={() => handleDownload(task.task_id)}
                >
                  Download
                </Button>
              )}
            </ListItem>
          ))}
        </List>
      </Paper>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Queue Status
        </Typography>
        <Typography variant="body1">Total Tasks: {queueStatus.total_tasks}</Typography>
        <Typography variant="body1">Active Tasks: {queueStatus.active_tasks}</Typography>
        <Typography variant="body1">Queued Tasks: {queueStatus.queued_tasks}</Typography>
        <Typography variant="body1">Completed Tasks: {queueStatus.completed_tasks}</Typography>
        <Typography variant="body1">Failed Tasks: {queueStatus.failed_tasks}</Typography>
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