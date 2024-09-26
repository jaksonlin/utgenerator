export const TASK_QUEUED = "0";
export const TASK_RUN = "1";
export const TASK_SUCC = "2";
export const TASK_FAIL = "3";

export const getStatusText = (status) => {
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
};