import { useEffect, useState } from "react";
import { useParams } from "react-router-dom"
import axios from "axios"
import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  Box, Flex,
} from "@chakra-ui/react";
import { Carousel } from "react-responsive-carousel";
import "react-responsive-carousel/lib/styles/carousel.min.css";

const ViewResults = () => {
  const { fp } = useParams();
  const [filename, setFilename] = useState("")
  const [BarPlots, setBarPlots] = useState([]);
  const [Histograms, setHistograms] = useState([]);
  const [VennDiagrams, setVennDiagrams] = useState([]);

  useEffect(() => {
    axios.post("/api/history/results", {
      "fp": fp,
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    }).then(res => {
      if (res.status === 200) {
        setFilename(res.data.filename)

        const fetchImages = async () => {
          try {
            let paths = [];
            const basePath = './temp';

            if (filename === 'No file passed') {
              paths = [
                './static/results/BarPlots/enhancerGene.jpg',
                './static/results/BarPlots/TotalcountComparsion.jpg',
                './static//results/BarPlots/uniqueEnhancersByMethod.jpg',
                './static/results/BarPlots/uniqueGenesByMethod.jpg',
                './static/results/histograms/DistanceHisto.jpg',
                './static/results/histograms/eqtlHisto.jpg',
                './static/results/VennDiagram/AllEnhancerComparsion.jpg',
                './static/results/VennDiagram/AllGeneComparsion.jpg',
                './static//results/VennDiagram/enhancerGeneVenn.jpg'
              ];
            } else {
              paths = [
                `${basePath}${res.data.filename}/BarPlots/enhancerGene.png`,
                `${basePath}${res.data.filename}/BarPlots/TotalcountComparsion.png`,
                `${basePath}${res.data.filename}/BarPlots//uniqueEnhancersByMethod.png`,
                `${basePath}${res.data.filename}/BarPlots/uniqueGenesByMethod.png`,
                `${basePath}${res.data.filename}/histograms/DistanceHisto.png`,
                `${basePath}${res.data.filename}/histograms/eqtlHisto.png`,
                `${basePath}${res.data.filename}/VennDiagram/AllEnhancerComparsion.png`,
                `${basePath}${res.data.filename}/VennDiagram/AllGeneComparsion.png`,
                `${basePath}${res.data.filename}/VennDiagram/enhancerGeneVenn.png`
              ];
            }

            const response = await axios.post('/api/checkFilesExist', paths);

            if (response.data && Array.isArray(response.data.existingFiles)) {
              setBarPlots(response.data.existingFiles.filter(path => path.includes('BarPlots')));
              setHistograms(response.data.existingFiles.filter(path => path.includes('histograms')));
              setVennDiagrams(response.data.existingFiles.filter(path => path.includes('VennDiagram')));
            }
          } catch (error) {
            console.error('Error fetching image paths', error);
          }
        };

        fetchImages();
      }
    })
  }, [])

  const CarouselSettings = {
    showArrows: true,
    interval: 3500,
    dynamicHeight: true,
    stopOnHover: true,
    infiniteLoop: true,
    showStatus: false,
    transitionTime: 500,
    showThumbs: true,
    showIndicators: true,
    emulateTouch: true,
    autoPlay: true,
    thumbWidth: 30,
  };

  return (
    <>
      <Flex justify="center" align="center" mt={5} mb={5}>
        <Box width={["100%", "80%", "80%", "80%"]}>

          <Accordion defaultIndex={[0]} allowMultiple allowToggle fontFamily='monospace'>
            <AccordionItem border="1px solid"
              borderColor="gray.200"
              borderRadius="md"
              boxShadow="md"
              mb={4}>
              <h2>
                <AccordionButton _expanded={{ bg: 'teal.500', color: 'white', fontWeight: "bold" }}
                  _hover={{ bg: 'teal.200' }}
                  borderRadius="md">
                  <Box as="span" flex='1' textAlign='left' width='80%' alignItems='center'>
                    Bar Plots
                  </Box>
                  <AccordionIcon />
                </AccordionButton>
              </h2>
              <AccordionPanel pb={4} display="flex" justifyContent="center" alignItems="center">
                <Box width="50%" height="auto">
                  <Carousel {...CarouselSettings}>
                    {BarPlots.map((images) => (
                      <div>
                        <img src={images} alt="" style={{ width: '100%', height: 'auto' }} />
                      </div>
                    ))}
                  </Carousel>
                </Box>
              </AccordionPanel>
            </AccordionItem>

            <AccordionItem border="1px solid"
              borderColor="gray.200"
              borderRadius="md"
              boxShadow="md"
              mb={4}>
              <h2>
                <AccordionButton _expanded={{ bg: 'teal.500', color: 'white', fontWeight: "bold" }}
                  _hover={{ bg: 'teal.200' }}
                  borderRadius="md">
                  <Box as="span" flex='1' textAlign='left'>
                    Histograms
                  </Box>
                  <AccordionIcon />
                </AccordionButton>
              </h2>
              <AccordionPanel pb={4} display="flex" justifyContent="center" alignItems="center">
                <Box width="50%" height="auto">
                  <Carousel {...CarouselSettings}>
                    {Histograms.map((images) => (
                      <div>
                        <img src={images} alt="" style={{ width: '100%', height: 'auto' }} />
                      </div>
                    ))}
                  </Carousel>
                </Box>
              </AccordionPanel>
            </AccordionItem>

            <AccordionItem border="1px solid"
              borderColor="gray.200"
              borderRadius="md"
              boxShadow="md"
              mb={4}>
              <h2>
                <AccordionButton _expanded={{ bg: 'teal.500', color: 'white', fontWeight: "bold" }}
                  _hover={{ bg: 'teal.200' }}
                  borderRadius="md">
                  <Box as="span" flex='1' textAlign='left'>
                    Venn Diagram
                  </Box>
                  <AccordionIcon />
                </AccordionButton>
              </h2>
              <AccordionPanel pb={4} display="flex" justifyContent="center" alignItems="center">
                <Box width="50%" height="auto">
                  <Carousel {...CarouselSettings}>
                    {VennDiagrams.map((images) => (
                      <div>
                        <img src={images} alt="" style={{ width: '100%', height: 'auto' }} />
                      </div>
                    ))}
                  </Carousel>
                </Box>
              </AccordionPanel>
            </AccordionItem>
          </Accordion>

        </Box>
      </Flex>
    </>
  )
}

export default ViewResults