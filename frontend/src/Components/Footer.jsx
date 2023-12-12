import { Button, Flex, Text } from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";

const Footer = ({ ...children }) => {
  const handleResetTutorial = () => {
    localStorage.removeItem("isFirstVisit");
    window.location = "/home";
  };

  return (
    <Flex
      {...children}
      bg="gray.50"
      borderTop={"1px"}
      borderTopColor="gray.200"
    >
      {localStorage.getItem("isFirstVisit") === "false" ? (
        <Button variant="link" ml={5} onClick={handleResetTutorial}>
          Reset tutorial
        </Button>
      ) : undefined}
      <Text p={2} align="center" color="gray.600" w="100%" h={"40px"}>
        © {new Date().getFullYear()} Copyright: Connect with us on{" "}
        <a
          href="https://github.com/Ricky223/enhancerGenie"
          target="_blank"
          rel="noreferrer"
        >
          <b>Github</b>
        </a>
      </Text>
    </Flex>
  );
};

export default Footer;
