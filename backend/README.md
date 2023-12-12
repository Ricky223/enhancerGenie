# enhancerGenePro
![alt text](https://github.com/yudeep-rajbhandari/enhancerGenePro/blob/master/flowDiagram.png?raw=true)

Since a docker container is used, no other programming language,libraries or software are required to be installed
except the following:
##  Git
You can install git in your system easily by either downloading the installer or via the command line.
## Docker
For Windows and Mac, it is better to install Docker desktop.
For linux/Ubuntu install Docker Engine.
Once both of them are installed, follow the following steps to run the tool.
##  Clone the Repository
####  git clone repository-url

Cloning the repository may take some time as there are supporting files with large sizes.
##  Build the Docker Image
Go inside the directory with: cd enhancerGenePro. Run the following command.
#### sudo docker build -t my-app-image .

This command will build a Docker image named "my-app-image" using the Dockerfile present in the current
directory.
## Run the Server
#### sudo docker run -dp 8080:8080 my-app-image

This command will start a Docker container based on the "my-app-image" image and map port 8080 from the
container to port 8080 on your local machine. The server will be running inside the container.
## Access the Server
The server should now be available at: http://localhost:8080. You can access it in your web browser.
##  Check Logs:
To check the logs of the running container, use the following command:
### docker logs -f <container-id>
Replace ‘<container-id>‘ with the actual ID of the container. The ‘-f‘ flag is used to follow the logs in real-time.
## Get Container ID
To obtain the ID of the running container, execute the command:
#### docker ps
This will display a list of running containers along with their IDs, names, and other details.

## Contribute

After cloning the project, type `docker compose up` to start the container in developer mode. This will allow you to make changes and see your changes live.