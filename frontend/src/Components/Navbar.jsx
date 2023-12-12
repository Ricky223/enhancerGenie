import {
  Box,
  Button,
  Flex,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  Text,
} from "@chakra-ui/react";
import React, { useContext } from "react";
import { useNavigate } from "react-router-dom";
import AuthContext from "./AuthProvider";

const Navbar = () => {
  const navigate = useNavigate();

  const { auth, setAuth } = useContext(AuthContext);

  const handleLogout = () => {
    setAuth({});
    localStorage.removeItem("user");
    navigate("/home");
  };

  return (
    <Box
      bg="blue.700"
      w="100%"
      p={2}
      color="white"
      display="flex"
      flexDir="row"
      justifyContent="space-between"
      alignItems="center" // Aligns items vertically
    >
    <Flex
      alignItems="flex-end" // Align items to the bottom
      justifyContent="space-between" // Distribute space between the elements
    >
      <Text
        fontSize="3xl"
        fontWeight="bold"
        onClick={() => navigate("home")}
        _hover={{ cursor: "pointer" }}
        mb={0}
      >
        Enhancer Genie
      </Text>

      <Text fontSize="md" color="white" ml={3} mb={1}>
        Visualize and compare enhancer-gene linking strategies
        </Text>
      </Flex>


      <Flex gap={8} mx={5}>
        <Button
          color="white"
          variant="link"
          onClick={() => navigate("home")}
        >
          Home
        </Button>
        <Button
          color="white"
          variant="link"
          onClick={() => navigate("/usage")}
          className="nav-usage"
        >
          Usage
        </Button>
        <Button
          className="nav-history"
          color="white"
          variant="link"
          onClick={() => navigate("/history")}
        >
          User History
        </Button>
        {auth && auth.username ? (
          <Menu placement="bottom-end">
            <MenuButton
              className="nav-login"
              as={Button}
              variant="link"
              color="white"
              _hover={{ color: "lightgrey" }}
              _expanded={{ color: "lightgrey" }}
            >
              Hello, {auth.username}
            </MenuButton>
            <MenuList
              bg="blue.500"
              borderColor="white"
              borderWidth="1px"
              minWidth="100px"
              mt={2}
            >
              <MenuItem
                bg="blue.500"
                color="white"
                _hover={{ bg: "blue.700", color: "white" }}
                p={1}
                fontSize="md"
                onClick={handleLogout}
                display="flex"
                justifyContent="center"
                alignItems="center"
              >
                Logout
              </MenuItem>
            </MenuList>
          </Menu>
        ) : (
          <Button
            color="white"
            variant="link"
            onClick={() => navigate("/login")}
            className="nav-login"
          >
            Login
          </Button>
        )}
      </Flex>
    </Box>
  );
};

export default Navbar;
