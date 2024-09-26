import React from 'react';
import { Button, CircularProgress, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const Input = styled('input')({
  display: 'none',
});

const FileUpload = ({ file, isUploading, handleFileChange, handleUpload }) => {
  return (
    <div>
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
    </div>
  );
};

export default FileUpload;