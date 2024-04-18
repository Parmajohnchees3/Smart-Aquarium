import React, { useState } from 'react';
import axios from 'axios';
import { CircularProgress, Button, Typography, Container, Box } from '@mui/material'; // Assuming you're using Material-UI for UI components

function ImageUpload() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [predictionResult, setPredictionResult] = useState({ prediction: null, common_name: null, can_live: null });
  const [isLoading, setIsLoading] = useState(false); // New loading state

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setPredictionResult({ prediction: null, common_name: null, can_live: null });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      alert('Please select a file to upload.');
      return;
    }

    setIsLoading(true); // Start loading
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post('https://fishfinal-lgf46eidkq-ue.a.run.app', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setPredictionResult(response.data);
    } catch (error) {
      console.error('Error uploading image:', error);
    } finally {
      setIsLoading(false); // Stop loading regardless of request outcome
    }
  };

  return (
    <Container component="main" maxWidth="sm">
      <Box sx={{ mt: 4, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography component="h1" variant="h5">Please upload a picture of your fish</Typography>
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
          <Button variant="contained" component="label" sx={{ mt: 3, mb: 2 }}>
            Upload Image
            <input type="file" hidden onChange={handleFileChange} />
          </Button>
          <Button type="submit" variant="contained" disabled={isLoading} sx={{ mt: 3, mb: 2, ml: 2 }}>
            Analyze
          </Button>
          {isLoading && <CircularProgress />} {/* Display loading indicator when isLoading is true */}
          {!isLoading && predictionResult.prediction && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6">Recognition and Analysis Complete</Typography>
              <Typography>Your fish is a: {predictionResult.prediction} {predictionResult.common_name && `or commonly known as ${predictionResult.common_name}`}</Typography>
              <Typography>This fish {predictionResult.can_live ? "can" : "cannot"} live in the current tank conditions.</Typography>
            </Box>
          )}
        </Box>
      </Box>
    </Container>
  );
}

export default ImageUpload;
