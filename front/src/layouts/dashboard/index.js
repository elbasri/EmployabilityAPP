import React, { useEffect, useState } from 'react';
import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";
import Projects from "layouts/dashboard/components/Projects";

import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from "@mui/material";

function Dashboard() {
  const [predictions, setPredictions] = useState([]);
  const [statistics, setStatistics] = useState(null);

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/predictions');
        const data = await response.json();
        setPredictions(data);
      } catch (error) {
        console.error('Error fetching predictions:', error);
      }
    };
    fetchPredictions();
  }, []);

  useEffect(() => {
      const fetchData = async () => {
          try {
              const response = await fetch('http://localhost:5000/api/counts');
              if (!response.ok) {
                  throw new Error(`HTTP error! Status: ${response.status}`);
              }
              const data = await response.json();
              setStatistics(data);
          } catch (error) {
              console.error('Error fetching statistics:', error);
          }
      };

      fetchData();
  }, []);


  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox>
        {/* ... (existing code) */}
        {/* Display the data received from the server */}
        {dataFromServer && (
          <div>
            <h2>List des fichiers:</h2>
            {/*<pre>{JSON.stringify(dataFromServer, null, 2)}</pre>*/}
          </div>
        )}
        
      </MDBox>
      <MDBox py={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={4}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="dark"
                icon="person_add"
                title="Predictions"
                count={statistics ? ( <span>{statistics.stats_count}</span> ) : (  0 )}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={4}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="success"
                icon="leaderboard"
                title="Employable"
                count={statistics ? ( <span>{statistics.employable_count}</span> ) : (  0 )}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={4}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                icon="store"
                title="Non Employable"
                count={statistics ? ( <span>{statistics.non_employable_count}</span> ) : (  0 )}
              />
            </MDBox>
          </Grid>
        </Grid>
      </MDBox>
      <MDBox>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Bac</TableCell>
                <TableCell align="right">Bac +2</TableCell>
                <TableCell align="right">Bac +3</TableCell>
                <TableCell align="right">Bac +4</TableCell>
                <TableCell align="right">Bac +5</TableCell>
                <TableCell align="right">Doctorate</TableCell>
                <TableCell align="right">Experience Required</TableCell>
                <TableCell align="right">Prediction</TableCell>
                <TableCell align="right">Timestamp</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {predictions.map((row, index) => (
                <TableRow key={index}>
                  <TableCell component="th" scope="row">{row.Bac}</TableCell>
                  <TableCell align="right">{row['Bac +2']}</TableCell>
                  <TableCell align="right">{row['Bac +3']}</TableCell>
                  <TableCell align="right">{row['Bac +4']}</TableCell>
                  <TableCell align="right">{row['Bac +5']}</TableCell>
                  <TableCell align="right">{row.Doctorate}</TableCell>
                  <TableCell align="right">{row.experience_required}</TableCell>
                  <TableCell align="right">{row.prediction}</TableCell>
                  <TableCell align="right">{new Date(row.timestamp).toLocaleString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Dashboard;
