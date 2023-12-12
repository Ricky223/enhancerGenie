import {useContext, useEffect} from 'react'
import { Box, Text, Center, Stack, Card, CardBody, Heading, Image, Flex } from '@chakra-ui/react'
import UploadForm from '../Components/UploadForm';
import AuthContext from "../Components/AuthProvider";

const Home = () => {

	const { auth } = useContext(AuthContext);

	useEffect(() => {
		fetch('/api/test').then(res => res.json()).then(data => {
			console.log(data)
		});
	}, []);

	const methods = [
		{
			name: 'Distance',
			description: (<>Based on proximity of enhancer and gene<br />
				Supports hg38 and hg19 for all tissues</>)
		},
		{
			name: 'Chromatin Loop',
			description: (<>Based on chromatin loop predictions from Peakachu which uses genome-wide contact maps from Hi-C datasets</>)
		},
		{
			name: 'eQTL',
			description: (<>Based on genetic variants associated with gene expression</>)
		},
		{
			name: 'Activity by Contact',
			description: (<>Based on enhancer activity and enhancer-promoter contact frequency<br />
				Only supports hg19</>)
		}
	]

	return (
		<Box mx='100px'>
			<Center>
				<UploadForm />
			</Center>
			<Flex direction='column' mb='100px'>
				<Heading textAlign='center'>Visualize the similarities and differences between enhancer-gene linking strategies</Heading>

				{/* Section 1 */}
				<Flex my='50px' justify='space-around' alignItems='center' flexWrap='wrap'>
					<Flex>
						<Flex direction='column'>
							<Flex>
								<Image src='/static/chia.jpg' htmlWidth='200px' htmlHeight='auto' />
								<Image src='/static/eqtl.jpg' htmlWidth='200px' htmlHeight='auto' />
							</Flex>
							<Image src='/static/distanceBased1.png' htmlWidth='400px' htmlHeight='auto' />
						</Flex>
					</Flex>
					<Flex direction='column'>
						<Heading color='blue.900' mb='15px' fontSize='2rem'>Get enhancer-gene links & view charts for these methods:</Heading>
						<Stack>
							{methods.map(method => (
								<Card>
									<CardBody>
										<Heading size='md'>{method.name}</Heading>
										<Text>{method.description}</Text>
									</CardBody>
								</Card>
							))}
						</Stack>
					</Flex>
				</Flex>

				{/* Section 2 */}
				<Flex my='50px' justify='space-around' alignItems='center' flexWrap='wrap'>
					<Flex direction='column' width='50%'>
						<Heading color='blue.900' mb='15px' fontSize='2rem'>Bar plots: Know the numbers</Heading>
						<Text width='70%'>
							Users can use the knowledge of number of unique genes and enhancer linked as well
							as their to choose what sort of ratio/numbers they are looking in their respective
							data set.
						</Text>
					</Flex>
					<Flex flexWrap='wrap'>
						<Image src='/static/enhancerGene.png' htmlWidth='300px' htmlHeight='auto' />
						<Image src='/static/uniqueEnhancersByMethod.png' htmlWidth='300px' htmlHeight='auto' />
					</Flex>
				</Flex>

				{/* Section 3 */}
				<Flex my='50px' justify='space-around' alignItems='center' flexWrap='wrap'>
					<Flex flexWrap='wrap'>
						<Image src='/static/enhancerGeneVenn.png' htmlWidth='300px' htmlHeight='auto' />
						<Image src='/static/AllGeneComparsion.png' htmlWidth='300px' htmlHeight='auto' />
					</Flex>
					<Flex direction='column' width='50%'>
						<Heading color='blue.900' mb='15px' fontSize='2rem'>Venn Diagrams: Know your overlaps</Heading>
						<Text>
							Users can use this data, to compare the unique enhancers,gene and their linkages among all
							three methods and can analyze their enhancer data set based on the overlap. They can also
							use the average p-value, which shows the strength of enhancer-gene link
						</Text>
					</Flex>
				</Flex>

				{/* Section 4 */}
				<Flex my='50px' justify='space-around' alignItems='center' flexWrap='wrap'>
					<Flex direction='column' width='50%'>
						<Heading color='blue.900' mb='15px' fontSize='2rem'>Histograms: Know your frequency</Heading>
						<Text>
							Knowing how many times your enhancer has linked to different genes can let you know about the
							nature of the enhancers in your data set. It can help you to choose one among three methods based
							on the type of result you are expecting from the data set based on frequency.
						</Text>
					</Flex>
					<Flex flexWrap='wrap'>
						<Image src='/static/PeakachuHisto.png' htmlWidth='300px' htmlHeight='auto' />
						<Image src='/static/eqtlHisto.png' htmlWidth='300px' htmlHeight='auto' />
					</Flex>
				</Flex>

			</Flex>
		</Box >
	);
}

export default Home;
