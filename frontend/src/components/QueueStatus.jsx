import React from 'react';
import { Typography } from '@mui/material';

const QueueStatus = ({ queueStatus }) => {
  return (
    <div>
      <Typography variant="h5" component="h2" gutterBottom>
        Queue Status
      </Typography>
      <Typography variant="body1">Total Tasks: {queueStatus.total_tasks}</Typography>
      <Typography variant="body1">Active Tasks: {queueStatus.active_tasks}</Typography>
      <Typography variant="body1">Queued Tasks: {queueStatus.queued_tasks}</Typography>
      <Typography variant="body1">Completed Tasks: {queueStatus.completed_tasks}</Typography>
      <Typography variant="body1">Failed Tasks: {queueStatus.failed_tasks}</Typography>
    </div>
  );
};

export default QueueStatus;