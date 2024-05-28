import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import Card from "@mui/material/Card";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

import CoverLayout from "layouts/authentication/components/CoverLayout";
import bgImage from "assets/images/bg-up-cover.jpeg";

function Results() {
  const { resultId } = useParams();
  const [resultData, setResultData] = useState(null);

  useEffect(() => {
    const fetchResultData = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/prediction/${resultId}/`);
        setResultData(response.data);
        console.log(response)
      } catch (error) {
        console.error('Error fetching result data:', error.message);
      }
    };

    fetchResultData();
  }, [resultId]);

  if (!resultData) {
    return <div>Loading...</div>;
  }

  return (
    <DashboardLayout>
    <DashboardNavbar />
    <Card>
        <MDBox
          variant="gradient"
          bgColor="info"
          borderRadius="lg"
          coloredShadow="success"
          mx={2}
          mt={-3}
          p={3}
          mb={1}
          textAlign="center"
        >
          <MDTypography variant="h4" fontWeight="medium" color="white" mt={1}>
            <div>
              <h1>Resultat: {resultData.id}</h1>
              <h2>Ficher: {resultData.uploaded_file}</h2>
            </div>

          </MDTypography>
        </MDBox>
  
        </Card>

        <MDTypography variant="h4" fontWeight="medium" mt={1}>
            <div>
              <h1>{resultData.graph !== 'noGraph' ? 'Visualisation:' : 'Valeurs:'}</h1>
              {resultData.graph !== 'noGraph' ? (
                <iframe  width="100%" height="800px"
                src={`http://localhost:5000/${resultData.graph}`} // Update the URL as needed
                title="Graph"
                style={{ width: '100%', height: '400px', border: 'none' }}
              />
              ) : (
                <div
                  dangerouslySetInnerHTML={{ __html: resultData.result_text }}
                />
              )}
            </div>

        </MDTypography>
  
      
      </DashboardLayout>
  );
}

export default Results;
