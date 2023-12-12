import React from "react";
import styles from "./Styles/Usage.module.css";
import file1 from "./Files/liver-testBed.bed";
import file2 from "./Files/liver-testBed2.bed";
import {
  Center,
  Flex,
  Heading,
  Image,
  Link,
  ListItem,
  OrderedList,
  Text,
  UnorderedList,
} from "@chakra-ui/react";
import { DownloadIcon, ExternalLinkIcon } from "@chakra-ui/icons";

function Usage() {
  return (
    <Flex direction="column" height="100%" width="100%" ml="2%">
      <Center width="100%">
        <Heading padding="2%" size="lg" color="#003073">
          Usage Instructions
        </Heading>
      </Center>

      <Flex direction="column" ml={5} gap={5}>
        <Heading
          size="md"
          color="#003073"
          lineHeight="200%"
        >
          Project Overview
        </Heading>
        <Text lineHeight="200%" width={"1300px"}>
          Enhancer Genie is an application which matches enhancers to their corresponding
          target gene using up to 4 different algorithms: distance, eQTL, 3D chromatin looping,
          and activity-by-contact. It generates enhancer-gene links determined by each algorithm
          as well as multiple charts which can be used for data visualization. Use the generated
          charts as a tool to determine which method is the best fit for your enhancer data.
        </Text>
      </Flex>

      <Flex direction="column" ml={5} gap={5}>
        <Heading
          size="md"
          color="#003073"
          lineHeight="200%"
        >
          About the Input
        </Heading>
        <Text lineHeight="200%" width={"1300px"}>
          Assembly & Tissue Selections: The application requires an assembly and tissue selection in
          addition to an input file containing the list of enhancer locations. The currently supported
          human genomes are assembly GRCh38 (hg38) and GRCh37 (hg19). Using any other species or assembly
          may be processed but the results will not be accurate. Some tissue selections will limit the
          algorithm options since some algorithms are only available for certain tissues.
        </Text>
        <Text lineHeight="200%" width={"1300px"}>
          Input Filename: It is recommended that the filename contains the name of the selected tissue.
          If not, a warning will popup that must be manually overridden each time the application is run.
          For example, if the selected tissue is adrenal gland, include ‘adrenal-gland’ in the filename.
        </Text>
        <Text lineHeight="200%" width={"1300px"}>
          Input File Format: The supported file formats are .bed and .bed.gz files. The file should not
          contain a header and should contain at least 3 columns: chromosome, start position, and end position.
          It is recommended to supply a large number of enhancers to increase the likelihood of receiving meaningful
          matches. For more information on the BED file format, you may refer to the link <Link
            href="https://useast.ensembl.org/info/website/upload/bed.html"
            isExternal
          >here<ExternalLinkIcon />{" "}
          </Link>. Here are some test files to get started.
          <UnorderedList lineHeight="200%" width={"1300px"}>
            <ListItem>
              {" "}
              <a href={file1}>
                file 1 <DownloadIcon />{" "}
              </a>
            </ListItem>
            <ListItem>
              {" "}
              <a href={file2}>
                file 2 <DownloadIcon />{" "}
              </a>
            </ListItem>
          </UnorderedList>
        </Text>
      </Flex>

      <Flex direction="column" ml={5} gap={5}>
        {/* <div className={styles.left}>
          
        </div> */}
        <Heading
          size="md"
          color="#003073"
          lineHeight="200%"
        >
          About the Algorithms
        </Heading>
        <Text lineHeight="200%" width={"1300px"}>
          This project supports multiple algorithms, each with their own benefits and drawbacks.
          It is up to the user to decide which algorithm best fits their needs using the output
          and data visualizations provided. These are the supported methods:
        </Text>
        <Text>
          <OrderedList ml={6}>
            <ListItem>
              <Text width={"1300px"}>
                Distance based: Based on proximity of enhancer and gene.
              </Text>
            </ListItem>
            <ListItem>
              <Text width={"1300px"}>
                eQTL based: Based on genetic variants associated with gene expression level.
              </Text>
            </ListItem>
            <ListItem>
              <Text width={"1300px"}>
                Chromatin loop based: Based on chromatin loop predictions from Peakachu which
                uses genome-wide contact maps from Hi-C datasets. Click <Link
                  href="https://www.nature.com/articles/s41467-020-17239-9" isExternal>here<ExternalLinkIcon />{" "}
                </Link> for more information.
              </Text>
            </ListItem>
            <ListItem>
              <Text width={"1300px"}>
                Activity-by-contact based: Based on enhancer activity and enhancer-promoter
                contact frequency. Click <Link
                  href="https://www.nature.com/articles/s41588-019-0538-0" isExternal>here<ExternalLinkIcon />{" "}
                </Link> for more information.
              </Text>
            </ListItem>
          </OrderedList>
        </Text>
        <div className={styles.right}>
          <Image width="300px" height="auto" src="/static/img.png" alt={""} />
          <Image width="300px" height="auto" src="/static/img_1.png" alt={""} />
        </div>
      </Flex>

      <Flex direction="column" ml={5} gap={5} mb={20}>
        <Heading
          size="md"
          color="#003073"
          lineHeight="200%"
        >
          About the Output
        </Heading>
        <Text width={"1300px"}>
          Charts: Each chart generated will have a short description explaining the chart and
          how to interpret it. These charts should be used to decide which algorithm best suits
          the user’s needs. The charts are available for download as pdfs using the buttons on
          the result page.
        </Text>
        <Text width={"1300px"}>
          BED Files: One .bed file will be generated for each algorithm, which will contain
          the enhancer-gene links determined via that algorithm. All .bed files can be downloaded
          using the “Download all .bed files” button on the result page. Each .bed file contains the
          enhancer on the left matched with its corresponding gene on the right. Insignificant matches
          will be omitted from the output.
        </Text>
        <Text width={"1300px"}>
          Each .bed file will have a header. Here is an explanation of each possible column header:
        </Text>
        <UnorderedList>
          <ListItem>
            <Text width={"1300px"}>
              The first few columns come directly from the inputted enhancer file and give
              information about the enhancer: enh_chr, enh_start, enh_end, enh_id
            </Text>
          </ListItem>
          <ListItem>
            <Text width={"1300px"}>
              The following columns give information about the corresponding target gene:
              gene_chr, gene_start, gene_end, gene_id, gene_name
            </Text>
          </ListItem>
          <ListItem>
            <Text width={"1300px"}>
              The following columns will contain the scores used to evaluate each method:
            </Text>
            <OrderedList>
              <ListItem>
                <Text>
                  dist_score: distance in base pairs from enhancer to gene
                </Text>
              </ListItem>
              <ListItem>
                <Text width={"1300px"}>
                  var_pval: p-value representing the statistical significance of the
                  association of the eQTL variant with its target gene. Click <Link
                  href="https://www.gtexportal.org/home/" isExternal>here<ExternalLinkIcon />{" "}
                </Link> for more information.
                </Text>
              </ListItem>
              <ListItem>
                <Text width={"1300px"}>
                  loop_score: contact frequency in 3D space of the region that the enhancer
                  resides in with the region the gene resides in. Click <Link
                  href="https://www.nature.com/articles/s41467-020-17239-9" isExternal>here<ExternalLinkIcon />{" "}
                </Link> for more information.
                </Text>
              </ListItem>
              <ListItem>
                <Text width={"1300px"}>
                  ABC_score: indicates the effect of the enhancer of its matched gene. Takes into
                  account enhancer activity and contact frequency. Click <Link
                  href="https://www.nature.com/articles/s41588-019-0538-0" isExternal>here<ExternalLinkIcon />{" "}
                </Link> for more information.
                </Text>
              </ListItem>
            </OrderedList>
          </ListItem>
        </UnorderedList>
        <Flex direction="column" gap={5} mb={20}>
        <Heading
          size="md"
          color="#003073"
          lineHeight="200%"
        >
          FAQs
        </Heading>
        <OrderedList>
          <ListItem>
            <Text width={"1300px"}>
              Some of my enhancers are missing from the results? Not all enhancers will have a match,
              and the matches heavily depend on the method(s) used. Only significant matches are displayed,
              which are filtered out based on the different scores for each method.
            </Text>
          </ListItem>
          <ListItem>
            <Text width={"1300px"}>
              Why are no charts showing? Why is my .bed file empty? This happens because there were no
              significant matches. This occurs most often with the chromatin loop method since it is
              pulling from a smaller database and is much pickier with its matches. It is recommended
              to include more enhancers in the input file for a higher probability of significant matches.
            </Text>
          </ListItem>
          <ListItem>
            <Text width={"1300px"}>
              Why is an algorithm missing from my charts? This happens because no significant matches
              were found for that particular algorithm.
            </Text>
          </ListItem>
          <ListItem>
            <Text>
              What does this score mean? See “About the Output”
            </Text>
          </ListItem>
          <ListItem>
            <Text width={"1300px"}>
              Where do you get your gene data from? View the README.md in the project github.
            </Text>
          </ListItem>

        </OrderedList>
        </Flex>
      </Flex>
    </Flex>
  );
}

export default Usage;
