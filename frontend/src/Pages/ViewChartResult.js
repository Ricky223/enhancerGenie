import React, { useEffect, useRef, useState } from "react";
import axios from "axios";
import { useParams } from "react-router-dom";
import { Bar } from "react-chartjs-2";
import {
  Button,
  Flex,
  Modal,
  ModalBody,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Spinner,
  Text,
  useDisclosure,
  Tooltip as ChakraToolTip,
} from "@chakra-ui/react";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import JSZip from "jszip";
import { saveAs } from "file-saver";
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Title,
  Tooltip,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const ViewChartResults = () => {
  const { fp } = useParams();
  const [chartData, setChartData] = useState({});
  const [chartTitle, setChartTitle] = useState("");
  const [chartKey, setChartKey] = useState(0);
  const [responseData, setResponseData] = useState([]);
  const chartRef = useRef(null);
  const [xAxisLabel, setXAxisLabel] = useState("");
  const [yAxisLabel, setYAxisLabel] = useState("");
  const [selectedButton, setSelectedButton] = useState(0);
  const [isDownloading, setIsDownloading] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();

  useEffect(() => {
    axios
      .post(
        "/api/history/results",
        {
          fp: fp,
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      )
      .then((res) => {
        if (res.status === 200 && Array.isArray(res.data)) {
          setResponseData(res.data);
          if (res.data && res.data.length > 0) {
            setChartData(res.data[0]);
            setChartTitle(res.data[0].title);
          }
        } else {
          console.error("Response data is not an array");
        }
      });
  }, [fp]);

  const options = {
    responsive: true,
    // maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top",
      },
      title: {
        display: true,
        text: chartTitle,
        font: {
          size: 18,
        },
      },
    },
    scales: {
      y: {
        title: {
          display: true,
          text: yAxisLabel,
          font: {
            size: 15,
          },
        },
      },
      x: {
        title: {
          display: true,
          text: xAxisLabel,
          font: {
            size: 15,
          },
        },
      },
    },
  };

  const getChartTypeDescription = (chartTitle) => {
    switch (chartTitle) {
      case "Chromatin Loop Matches By Loop Score":
        return "Sorts all chromatin loop matches into bins based on loop score, which is the contact frequency in 3D space of the region that the enhancer resides in with the region the gene resides in. Higher loop scores means higher contact frequency, which indicates a stronger match";
      case "Distance Matches By Distance Score":
        return "Sorts all distance matches into bins based on distance score (log scale). Lower distance scores indicate closer proximity between the enhancer and the associated gene.";
      case "eQTL Matches By Distance Score":
        return "Sorts all eQTL matches into bins based on distance scores (log scale). Lower distance scores indicate closer proximity between the enhancer and the associated gene.";
      case "eQTL Matches By Pval Score":
        return "Sorts all eQTL matches into bins based on pval score. Pval represents the statistical significance of the association of the eQTL variant (and enhancer) with its matched gene. Smaller pvals indicate more significant matches.";
      case "Activity by Contact Matches by ABC Score":
        return "Sorts all activity-by-contact matches into bins based on their ABC (activity-by-contact) score, which indicates the effect of the enhancer on its matched gene. Higher ABC scores suggest stronger matches. ABC score = (enhancer activity x enhancer/gene contact frequency) / sum of (activity x contact frequency)";
      case "Total Count Comparisons":
        return `Displays how many unique enhancers, genes, and enhancer-gene
        matches occur for each method. Higher counts indicate more
        matches. Note: Clicking any dataset(s) in the chart's legend will
        remove the respective data from the chart for ease of use. This
        can be undone.`;
      case "Enhancer Redundancy":
        return `Displays how many times x enhancers matched with the same gene.
        Can provide information about the redundancy of enhancers. Note:
        Clicking any method name(s) in the chart's legend will remove the
        respective method(s) from the chart for ease of use. This can be
        undone.`;
      default:
        return "No description available.";
    }
  };

  const renderChart = () => {
    if (chartData && chartData.datasets) {
      return (
        <Flex justifyContent="center" alignItems="center" w="100%">
          <Flex ref={chartRef} h="50%" w="80%" justify="center">
            <Bar options={options} data={chartData} key={chartKey} />
          </Flex>
        </Flex>
      );
    }
    return (
      <Text align="auto">
        No chart data available. Please select a chart.
        If no chart options are visible, there was no meaningful data to display.
      </Text>
    );
  };

  const downloadChart = () => {
    const chartContainer = chartRef.current;

    if (chartContainer) {
      html2canvas(chartContainer).then((canvas) => {
        const imageData = canvas.toDataURL("image/png");
        const pdf = new jsPDF("l", "mm", "a4");

        const imgProps = pdf.getImageProperties(imageData);
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;

        pdf.addImage(imageData, "PNG", 0, 0, pdfWidth, pdfHeight);
        pdf.save(chartTitle + ".pdf");
      });
    }
  };

  const downloadResultFile = (fp) => {
    axios({
      url: "/api/download",
      method: "POST",
      data: { fingerprint: fp },
      responseType: "blob",
    })
      .then((response) => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", "results.zip");
        document.body.appendChild(link);
        link.click();
        window.URL.revokeObjectURL(url);
        link.remove();
      })
      .catch((error) => {
        console.error("Download failed", error);
      });
  };

  const downloadAllCharts = async () => {
    onOpen();
    setIsDownloading(true);
    const zip = new JSZip();

    for (let i = 0; i < responseData.length; i++) {
      const pdf = new jsPDF("l", "mm", "a4");
      const item = responseData[i];
      handleButtonClick(item, item.title);
      await new Promise((r) => setTimeout(r, 1000));

      const chartContainer = chartRef.current;
      if (chartContainer) {
        await html2canvas(chartContainer).then((canvas) => {
          const imageData = canvas.toDataURL("image/png");
          const imgProps = pdf.getImageProperties(imageData);
          const pdfWidth = pdf.internal.pageSize.getWidth();
          const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
          pdf.addImage(imageData, "PNG", 0, 0, pdfWidth, pdfHeight);
          zip.file(`${item.title}.pdf`, new Blob([pdf.output("blob")]));
        });
      }
    }
    zip.generateAsync({ type: "blob" }).then((content) => {
      saveAs(content, "chartResults.zip");
    });
    setIsDownloading(false);
    onClose();
  };

  const handleButtonClick = (item, title, index, yAxisLabel, xAxisLabel) => {
    setSelectedButton(index);
    setChartData({
      datasets: item.datasets,
      labels: item.labels,
    });
    setChartTitle(title);
    setYAxisLabel(yAxisLabel);
    setXAxisLabel(xAxisLabel);
  };

  return (
    <Flex direction="column" align="center" w="100%" pt="15px">
      {isDownloading && (
        <Modal isOpen={isOpen} onClose={onClose} isCentered>
          <ModalOverlay />
          <ModalContent>
            <ModalHeader justify="center" align="center">
              Downloading Charts
            </ModalHeader>
            <ModalBody>
              <Flex direction={"column"} justify="center" align="center">
                <Spinner size="xl" />
                <Text mt={"10px"} justify="center" align="center">
                  Please wait while charts are being downloaded...
                </Text>
              </Flex>
            </ModalBody>
          </ModalContent>
        </Modal>
      )}
      <Flex wrap="wrap" justifyContent="center" gap="5px" marginTop="0.5%">
        {responseData.map((item, index) => (
          <ChakraToolTip label={getChartTypeDescription(item.title)}>
            <Button
              key={index}
              fontSize="15px"
              px="3"
              py="2"
              bg={selectedButton === index ? "white" : "blue.500"}
              borderColor={selectedButton === index ? "blue.700" : undefined}
              border={selectedButton === index ? "2px" : undefined}
              color={selectedButton === index ? "blue.500" : "white"}
              onClick={() =>
                handleButtonClick(
                  item,
                  item.title,
                  index,
                  item.ylabel,
                  item.xlabel
                )
              }
            >
              {item.title}
            </Button>
          </ChakraToolTip>
        ))}
      </Flex>
      <Flex w="80%" justifyContent="center" alignItems="center" marginTop="1%">
        {renderChart()}
      </Flex>
      <Flex gap="20px" mt="20px" justifyContent="space-around" mb={"40px"}>
        <Button bg="blue.500" color="white" onClick={downloadChart}>
          Download Current Chart
        </Button>
        <Button bg="blue.500" color="white" onClick={downloadAllCharts}>
          Download All Charts
        </Button>
        <Button
          bg="blue.500"
          color="white"
          onClick={() => downloadResultFile(fp)}
        >
          Download All .bed Files
        </Button>
      </Flex>
    </Flex>
  );
};

export default ViewChartResults;
