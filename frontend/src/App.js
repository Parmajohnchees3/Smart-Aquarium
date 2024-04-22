import React, { useState } from 'react';
import axios from 'axios';
import { CircularProgress, Button, Typography, Container, Box } from '@mui/material';

function ImageUpload() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [imageUrl, setImageUrl] = useState('');
  const [predictionResult, setPredictionResult] = useState({ prediction: null, common_name: null, can_live: null });
  const [tankReadings, setTankReadings] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setPredictionResult({ prediction: null, common_name: null, can_live: null });
    setImageUrl(URL.createObjectURL(event.target.files[0])); // Create a URL for the uploaded file
    setTankReadings([]); // Reset tank readings
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      alert('Please select a file to upload.');
      return;
    }

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post('https://pleasejustwork-lgf46eidkq-ue.a.run.app', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setPredictionResult(response.data);
      setTankReadings(response.data.readings); // Set tank readings from response
    } catch (error) {
      console.error('Error uploading image:', error);
    } finally {
      setIsLoading(false);
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
          {isLoading && <Box sx={{ display: 'flex', justifyContent: 'center', width: '100%', mt: 2 }}><CircularProgress /></Box>}
          {!isLoading && predictionResult.prediction && (
            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <img src={imageUrl} alt="Uploaded Fish" style={{ maxWidth: '100%', height: 'auto' }} />
              <Typography variant="h6">Recognition and Analysis Complete</Typography>
              <Typography>Your fish is a: {predictionResult.prediction} {predictionResult.common_name && `or commonly known as ${predictionResult.common_name}`}</Typography>
              <Typography>This fish {predictionResult.can_live ? "can" : "cannot"} live in the current tank conditions.</Typography>
              {tankReadings.length > 0 && (
                <Typography>Tank Readings: Temp - {tankReadings[0]}°C, pH - {tankReadings[1]}</Typography>
              )}
            </Box>
          )}
        </Box>
      </Box>
    </Container>
  );
}

export default ImageUpload;
