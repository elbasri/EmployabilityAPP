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

  useEffect(() => {
    const heads = document.querySelectorAll('.css-tdxonj-MuiTableHead-root');
    heads.forEach(head => {
      head.classList.remove('css-tdxonj-MuiTableHead-root');
    });
  }, []);


  return (
    <DashboardLayout>
      <DashboardNavbar />
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
        <Table sx={{ minWidth: 800 }} size="small" aria-label="a dense table" style={{ tableLayout: 'fixed' }}>
          <TableHead>
            <TableRow>
              <TableCell sx={{ width: '5%' }}>Bac</TableCell>
              <TableCell align="left" sx={{ width: '5%' }}>Bac +2</TableCell>
              <TableCell align="left" sx={{ width: '5%' }}>Bac +3</TableCell>
              <TableCell align="left" sx={{ width: '5%' }}>Bac +4</TableCell>
              <TableCell align="left" sx={{ width: '5%' }}>Bac +5</TableCell>
              <TableCell align="left" sx={{ width: '5%' }}>Doctorate</TableCell>
              <TableCell align="left" sx={{ width: '15%' }}>Expérience requise</TableCell>
              <TableCell align="left" sx={{ width: '5%' }}>Prédiction</TableCell>
              <TableCell align="left" sx={{ width: '15%' }}>Timestamp</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {predictions.map((row, index) => (
              <TableRow key={index}>
                <TableCell component="td" scope="row">{row.Bac}</TableCell>
                <TableCell align="left">{row['Bac +2']}</TableCell>
                <TableCell align="left">{row['Bac +3']}</TableCell>
                <TableCell align="left">{row['Bac +4']}</TableCell>
                <TableCell align="left">{row['Bac +5']}</TableCell>
                <TableCell align="left">{row.Doctorate}</TableCell>
                <TableCell align="left">{row.experience_required}</TableCell>
                <TableCell align="left">{row.prediction}</TableCell>
                <TableCell align="left">{new Date(row.timestamp).toLocaleString()}</TableCell>
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
