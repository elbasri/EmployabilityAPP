// @mui material components
import { Card, Grid, MenuItem, Select, TextField, Button } from "@mui/material";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import React, { useState } from 'react';

function PredictForm() {
  const [studyLevel, setStudyLevel] = useState('');
  const [experience, setExperience] = useState('');
  const [skills, setSkills] = useState('');
  const [predictionResult, setPredictionResult] = useState(null);

  const handlePredict = async () => {
    const inputData = {
      study_level: studyLevel,
      experience_required: experience,
      skills: skills
    };

    try {
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(inputData)
      });

      const data = await response.json();
      setPredictionResult(data.prediction);
    } catch (error) {
      console.error('Error sending prediction request:', error);
    }
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox mt={4} mb={3}>
        <Card>
          <MDBox p={3} textAlign="center">
            <MDTypography variant="h4" fontWeight="medium">Submit Prediction Data</MDTypography>
            <MDBox mt={2}>
              <Select
                fullWidth
                value={studyLevel}
                onChange={(e) => setStudyLevel(e.target.value)}
                displayEmpty
              >
                <MenuItem value="" disabled>Select Study Level</MenuItem>
                <MenuItem value="Bac">Bac</MenuItem>
                <MenuItem value="Bac +2">Bac +2</MenuItem>
                <MenuItem value="Bac +3">Bac +3</MenuItem>
                <MenuItem value="Bac +4">Bac +4</MenuItem>
                <MenuItem value="Bac +5">Bac +5</MenuItem>
                <MenuItem value="Doctorate">Doctorate</MenuItem>
              </Select>
            </MDBox>
            <MDBox mt={2}>
              <TextField
                fullWidth
                label="Experience (years)"
                type="number"
                value={experience}
                onChange={(e) => setExperience(e.target.value)}
              />
            </MDBox>
            <MDBox mt={2}>
              <TextField
                fullWidth
                label="Skills"
                value={skills}
                onChange={(e) => setSkills(e.target.value)}
              />
            </MDBox>
            <MDBox mt={3}>
              <Button variant="contained" color="primary" onClick={handlePredict}>
                Predict
              </Button>
            </MDBox>
            {predictionResult !== null && (
              <MDBox mt={2}>
                <MDTypography variant="h5">
                  Prediction Result: {predictionResult}
                </MDTypography>
              </MDBox>
            )}
          </MDBox>
        </Card>
      </MDBox>
    </DashboardLayout>
  );
}

export default PredictForm;
