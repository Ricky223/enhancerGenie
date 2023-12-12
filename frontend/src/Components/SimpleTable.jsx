// Joe Cranney's Simple Table Component
import {
  Box,
  Text,
  HStack,
  Table,
  Th,
  Thead,
  Tr,
  Tbody,
  Icon,
  Input,
  InputGroup,
  InputLeftElement,
  Stack,
  useBreakpointValue,
  ButtonGroup,
  Button,
  Flex,
  Skeleton,
  Tooltip,
} from "@chakra-ui/react";
// import { FiSearch } from "react-icons/fi";
import SimpleTableItem from "./SimpleTableItem";

const SimpleTable = ({
  headers,
  rowData,
  actions,
  onSearchChange,
  onSearchSubmit,
  onNext,
  onPrevious,
  onRowClick = () => {},
  onThumbnailClick = () => {},
  page,
  totalResults,
  isLoading = true,
  isClipTable = false,
  nextButtonLoading = false,
  prevButtonLoading = false,
}) => {
  const isMobile = useBreakpointValue({
    base: true,
    md: false,
  });

  // remove id from headers
  headers = headers.filter((h) => h.toLowerCase() !== "id");

  return (
    <Box
      bg="bg.surface"
      boxShadow={{
        base: "none",
        md: "sm",
      }}
      borderRadius={{
        base: "none",
        md: "lg",
      }}
    >
      <Stack spacing="5">
        <Box pt="5">
          <Stack
            direction={{
              base: "column",
              md: "row",
            }}
            justify="end"
          >
            <InputGroup maxW="xs">
              {/* <InputLeftElement pointerEvents="none">
                <Icon as={FiSearch} color="fg.muted" boxSize="5" />
              </InputLeftElement> */}
              <Tooltip label="Search by assembly or tissue" placement="top">
                <Input
                  placeholder="Search"
                  onChange={(e) => onSearchChange(e.target.value.toLowerCase())}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      onSearchSubmit();
                    }
                  }}
                />
              </Tooltip>
            </InputGroup>
          </Stack>
        </Box>
        <Box overflowX="auto">
          <Table>
            <Thead>
              <Tr>
                <Th>
                  <HStack spacing="3">
                    <HStack spacing="1">
                      <Text>{headers[0]}</Text>
                    </HStack>
                  </HStack>
                </Th>
                {headers.slice(1).map((header, index) => (
                  <Th key={index}>{header}</Th>
                ))}
                {actions ? <Th>Actions</Th> : undefined}
              </Tr>
            </Thead>
            <Tbody>
              {rowData.map((data) => {
                let tableData = data;
                if ("id" in data) {
                  const objWithoutId = { ...data };
                  delete objWithoutId.id;
                  tableData = objWithoutId;
                }

                if ("url" in data && isClipTable) {
                  const objWithoutUrl = { ...tableData };
                  delete objWithoutUrl.url;
                  tableData = objWithoutUrl;
                }

                return (
                  <SimpleTableItem
                    rowData={tableData}
                    actions={actions}
                    actionData={data}
                    onClick={() => onRowClick(data)}
                    onThumbnailClick={() => onThumbnailClick(data)}
                  />
                );
              })}
            </Tbody>
          </Table>
          {isLoading ? (
            <Stack py={2}>
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((row) => (
                <Skeleton height="30px" />
              ))}
            </Stack>
          ) : rowData.length === 0 ? (
            <Flex justify="center" p={4}>
              <Text fontWeight="medium">There is no data to display</Text>
            </Flex>
          ) : undefined}
        </Box>
        <Box
          px={{
            base: "4",
            md: "6",
          }}
          pb="5"
        >
          <HStack spacing="3" justify="space-between">
            {!isMobile && (
              <Text color="fg.muted" textStyle="sm">
                Showing 1 to {Math.min(10, rowData.length)} of {totalResults}{" "}
                results
              </Text>
            )}
            <ButtonGroup
              spacing="3"
              justifyContent="space-between"
              width={{
                base: "full",
                md: "auto",
              }}
            >
              <Button
                onClick={onPrevious}
                isDisabled={page < 2}
                isLoading={prevButtonLoading}
              >
                Previous
              </Button>
              <Button
                onClick={onNext}
                isDisabled={totalResults / 10 <= page}
                isLoading={nextButtonLoading}
              >
                Next
              </Button>
            </ButtonGroup>
          </HStack>
        </Box>
      </Stack>
    </Box>
  );
};

export default SimpleTable;
