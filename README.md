# Enhancer Genie

# User Documentation
## Prerequisites
1. Install Git
2. Install Docker Desktop

## Installation
1. Navigate to the project repository
2. Clone the repository onto your local machine using git clone <repository link>
3. cd into the cloned repository
4. Open Docker Desktop
5. In command line, type docker compose up

Once the installation steps are followed, a local server will be started on port 3000. You can access this server by navigating to http://localhost:3000 in your web browser. 

## Project Overview
Enhancer Genie is an application which matches enhancers to their corresponding target gene using up to 4 different algorithms: distance, eQTL, 3D chromatin looping, and activity-by-contact. It generates enhancer-gene links determined by each algorithm as well as multiple charts which can be used for data visualization. Use the generated charts as a tool to determine which method is the best fit for your enhancer data.


## About the Input
Assembly & Tissue Selections: The application requires an assembly and tissue selection in addition to an input file containing the list of enhancer locations. The currently supported human genomes are assembly GRCh38 (hg38) and GRCh37 (hg19). Using any other species or assembly may be processed but the results will not be accurate. Some tissue selections will limit the algorithm options since some algorithms are only available for certain tissues.

Input Filename: It is recommended that the filename contains the name of the selected tissue. If not, a warning will popup that must be manually overridden each time the application is run. For example, if the selected tissue is adrenal gland, include ‘adrenal-gland’ in the filename.
 
Input File Format: The supported file formats are .bed and .bed.gz files. The file should not contain a header and should contain at least 3 columns: chromosome, start position, and end position. It is recommended to supply a large number of enhancers to increase the likelihood of receiving meaningful matches. For more information on the BED file format, you may refer to the link here.

## About the Output
Charts: Each chart generated will have a short description explaining the chart and how to interpret it. These charts should be used to decide which algorithm best suits the user’s needs. The charts are available for download as pdfs using the buttons on the result page.

BED Files: One .bed file will be generated for each algorithm, which will contain the enhancer-gene links determined via that algorithm. All .bed files can be downloaded using the “Download all .bed files” button on the result page. Each .bed file contains the enhancer on the left matched with its corresponding gene on the right. Insignificant matches will be omitted from the output.

Each .bed file will have a header. Here is an explanation of each possible column header:
1. The first few columns come directly from the inputted enhancer file and give information about the enhancer:
enh_chr, enh_start, enh_end, enh_id
2. The following columns give information about the corresponding target gene:
gene_chr, gene_start, gene_end, gene_id, gene_name
3. The following columns will contain the scores used to evaluate each method:
dist_score: distance in base pairs from enhancer to gene
var_pval: p-value representing the statistical significance of the association of the eQTL variant with its target gene. Click here for more information.
loop_score: contact frequency in 3D space of the region that the enhancer resides in with the region the gene resides in. Click here for more information.
ABC_score: indicates the effect of the enhancer of its matched gene. Takes into account enhancer activity and contact frequency. Click here for more information.


## About the Algorithms
This project supports multiple algorithms, each with their own benefits and drawbacks. It is up to the user to decide which algorithm best fits their needs using the output and data visualizations provided. These are the supported methods:

1. Distance based: Based on proximity of enhancer and gene.
2. eQTL based: Based on genetic variants associated with gene expression level.
3. Chromatin loop based: Based on chromatin loop predictions from Peakachu which uses genome-wide contact maps from Hi-C datasets. Click here for more information.
4. Activity-by-contact based: Based on enhancer activity and enhancer-promoter contact frequency. Click here for more information.

## Data Sources
* Distance: Ensembl BioMart
* Chromatin loop: raw data available for download here (3D genome), github (Peakachu)
* ABC: raw data available for download here, download raw data
* eQTL: raw data available for download here (GTEx)
* All algorithms use the python library pybedtools

## FAQs
1. Some of my enhancers are missing from the results?
Not all enhancers will have a match, and the matches heavily depend on the method(s) used. Only significant matches are displayed, which are filtered out based on the different scores for each method.
2. What does this score mean? 
See “About the Output”
3. Where do you get your gene data from?
See “Data Sources”
4. Why are no charts showing? Why is my .bed file empty?
This happens because there were no significant matches. This occurs most often with the chromatin loop method since it is pulling from a smaller database and is much pickier with its matches. It is recommended to include more enhancers in the input file for a higher probability of significant matches.
5. Why is an algorithm missing from my charts?
This happens because no significant matches were found for that particular algorithm.


# Developer Documentation
## Prerequisites
1. Install Git
2. Install Docker Desktop

## Installation
1. Navigate to the project repository
2. Clone the repository onto your local machine
3. cd to the cloned repository
4. Open Docker Desktop
5. In command line, type docker compose up
If access denied, run with sudo
If build failed, try run rm  ~/.docker/config.json

Once the installation steps are followed, a local server will be started on port 3000. You can access this server by navigating to http://localhost:3000 in your web browser. Any changes that are made in the repository folder will automatically be reflected on the running server.

## Docker Architecture
Docker compose is used to set up the project automatically in a single command. Behind the scenes, there are two images built; one for the backend Python api, and one for the frontend React web server. Each image is then deployed into its own container. The backend container can be accessed on port 8080, and the frontend container is accessible on port 3000. 

On the frontend web server, all unknown requests are automatically proxied to the backend server on port 8080. What this means is that we can access the backend server directly on the frontend. This is all automatically handled in Docker.

## Database
The app uses MongoDB as a database. The connection uri of the database is specified as an environment variable called “CONN_STR”. In order to specify this url along with the support of Docker, it must be specified in the docker-compose.yml file found at the root of the repository. Currently, a string is already defined, but it is not a database that is owned or hosted by Baylor. Maintainability is not guaranteed and we recommend putting your own connection string for future development/production purposes.

## API Routes
The api routes can be found in the Executor.py file for more specifics.

```GET /api/database_download/<filename>```
**DEPRECATED** Downloads provided filename from local file system.

```GET /api/download/<filename>```
**DEPRECATED** Downloads provided filename as an attachment

```[GET, POST] /api/upload```
Expects form data to be sent in the following format:

organ string*
assembly string*
algorithms []string*
email string
file File

* required

```GET /api/tissues```
Returns supported tissues

```GET /temp/<path:path>```
        /results/temp/<path:path>
Allows you to access local files from temp or results folder

```[POST] /api/checkFilesExist```
Expects json data to be sent in the following format:

string[]

```[GET] /api/history```
Returns run history

```[POST] /api/history/metadata```
Returns history data that is rendered on the History table

```[POST] /api/history/delete```
Removes a history entry

```[POST] /api/history/results```
Fetches the chart data for a specific history item

```[POST] /api/register```
Creates a new user

```[POST] /api/login```
Generates a login session

