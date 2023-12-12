import {
  Badge,
  Button,
  Flex,
  HStack,
  Td,
  Tr,
  Text,
  useColorMode,
  Image,
} from "@chakra-ui/react";

const SimpleTableItem = ({
  rowData,
  onClick,
  actions,
  actionData,
  onThumbnailClick,
}) => {
  const { colorMode } = useColorMode();

  return (
    <Tr
      key={rowData.id}
      _hover={{
        backgroundColor: colorMode === "light" ? "gray.50" : "gray.900",
        cursor: "pointer",
      }}
      transition="ease-in-out"
      transitionDuration="200ms"
      onClick={onClick}
    >
      <Td>
        <HStack spacing="3">
          <Text fontWeight="medium">
            {Object.keys(rowData)[0] === "thumbnail" ? (
              <Image
                src={rowData[Object.keys(rowData)[0]]}
                height="80px"
                borderRadius="5px"
                fallbackSrc="https://placehold.co/258x343"
                onClick={onThumbnailClick}
              />
            ) : (
              rowData[Object.keys(rowData)[0]]
            )}
          </Text>
        </HStack>
      </Td>
      {Object.entries(rowData)
        .slice(1)
        .map(([key, value]) => {
          if (typeof value === "number") {
            value = value.toLocaleString("en-US");
          }

          return (
            <Td key={key}>
              {key === "status" ? (
                <Badge
                  colorScheme={
                    value === "pending" ||
                    value === "processing" ||
                    value == "upcoming"
                      ? "yellow"
                      : value === "approved" ||
                        value === "succeeded" ||
                        value === "active"
                      ? "green"
                      : "red"
                  }
                >
                  {value}
                </Badge>
              ) : key === "platform" ||
                key === "currency" ||
                key === "mode" ||
                key === "interval" ? (
                <Badge>{value}</Badge>
              ) : key === "algorithms" ? (
                value.map((alg) => {
                  let algorithmText = "";
                  if (alg === "abc") {
                    algorithmText = "Activity by Contact";
                  } else if (alg === "chiaPet") {
                    algorithmText = "Chromatin Loop";
                  } else if (alg === "distance") {
                    algorithmText = "Distance";
                  } else if (alg === "eqtl") {
                    algorithmText = "eQTL";
                  }
                  return <Badge mx="2px">{algorithmText}</Badge>;
                })
              ) : key === "fingerprint" ? undefined : (
                value
              )}
            </Td>
          );
        })}

      {actions && (
        <Td>
          <Flex gap={2}>
            {actions.map((action) => (
              <Button
                size="sm"
                onClick={() => action.onClick(actionData)}
                leftIcon={action.buttonIcon}
                colorScheme={action.colorScheme}
                w="100px"
              >
                {action.name}
              </Button>
            ))}
          </Flex>
        </Td>
      )}
    </Tr>
  );
};

export default SimpleTableItem;
