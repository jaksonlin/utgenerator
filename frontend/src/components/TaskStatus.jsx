import React, { useState, useEffect } from 'react';
import { List, ListItem, ListItemText, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Pagination, Typography } from '@mui/material';
import axios from 'axios';

const TASK_SUCC = "2";

const getStatusText = (status) => {
  switch (status) {
    case "0":
      return 'Queued';
    case "1":
      return 'Running';
    case "2":
      return 'Completed';
    case "3":
      return 'Failed';
    default:
      return 'Unknown';
  }
};

const TaskStatus = ({ tasks, handleDownload }) => {
  const [historicalTasks, setHistoricalTasks] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchHistoricalTasks(page);
  }, [page]);

  const fetchHistoricalTasks = async (page) => {
    try {
      const response = await axios.get(`/tasks?page=${page}&per_page=10`);
      
      setHistoricalTasks(response.data.tasks || []);
      setTotalPages(response.data.total_pages || 1);
    } catch (error) {
      console.error('Failed to fetch historical tasks:', error);
      setHistoricalTasks([]);
      setTotalPages(1);
    }
  };

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  return (
    <div>
      <Typography variant="h6" component="h2" gutterBottom>
        Current Tasks
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

      <Typography variant="h6" component="h2" gutterBottom>
        Historical Tasks
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Task ID</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Filename</TableCell>
              <TableCell>Timestamp</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {historicalTasks.map((task) => (
              <TableRow key={task.task_id}>
                <TableCell>{task.task_id}</TableCell>
                <TableCell>{getStatusText(task.status)}</TableCell>
                <TableCell>{task.filename}</TableCell>
                <TableCell>{new Date(task.timestamp * 1000).toLocaleString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Pagination count={totalPages} page={page} onChange={handlePageChange} />
    </div>
  );
};

export default TaskStatus;