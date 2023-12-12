import React, { useEffect, useRef, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Flex,
  FormControl,
  FormLabel,
  Input,
  Text,
  useToast,
} from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const RegisterForm = () => {
  const navigate = useNavigate();
  const toast = useToast();

  const userRef = useRef();
  const passwordRef = useRef();
  const errorRef = useRef();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [success, setSuccess] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);

  useEffect(() => {
    userRef.current.focus();
  }, []);

  useEffect(() => {
    setErrorMsg("");
  }, [username, password]);

  const validatePassword = (password) => {
    return password.length >= 8;
  };

  const handleSubmit = async (e) => {
    setSubmitLoading(true);
    e.preventDefault();

    if (!validatePassword(password)) {
      setErrorMsg("Invalid password. It must be at least 8 characters.");
      setSubmitLoading(false);
      return;
    }

    try {
      const response = await axios.post(
        "/api/register",
        JSON.stringify({ username, password }),
        {
          headers: { "Content-Type": "application/json" },
          withCredentials: true,
        }
      );

      setSubmitLoading(false);
      console.log(JSON.stringify(response.data));
      setUsername("");
      setPassword("");
      setSuccess(true);
      toast({
        title: "Registration successful!",
        description: "You will be redirected to the login page.",
        status: "success",
        duration: 9000,
        isClosable: true,
        position: "top",
      });

      navigate("/login");
    } catch (err) {
      setSubmitLoading(false);
      if (!err?.response?.status === 500) {
        setErrorMsg("Failed to register user");
      } else if (err.response?.status === 400) {
        setErrorMsg("Username already exists");
      } else if (err.response?.status === 401) {
        setErrorMsg("Missing username or password");
      } else {
        setErrorMsg("Login Failed");
      }
    }
  };

  return (
    <Flex direction="column" align="center" style={{ minHeight: "100vh" }}>
      <Flex
        direction="column"
        my="50px"
        width="400px"
        style={{
          border: "1px solid gray",
          padding: "20px",
          borderRadius: "5px",
        }}
      >
        {success && (
          <Box mb="4" bgColor="green.200" p="3" borderRadius="md">
            Registration successful! Redirecting...
          </Box>
        )}
        {errorMsg && (
          <Alert ref={errorRef} status="error" mb="4" borderRadius="md">
            {errorMsg}
          </Alert>
        )}
        <Text fontSize="2xl" textAlign="center" fontWeight="bold">
          Register
        </Text>
        <FormControl>
          <FormLabel mt="10px">Username:</FormLabel>
          <Input
            type="text"
            ref={userRef}
            autoComplete="off"
            onChange={(e) => setUsername(e.target.value)}
            value={username}
            required
          />
          <FormLabel mt="10px">Password:</FormLabel>
          <Input
            type="password"
            ref={passwordRef}
            onChange={(e) => setPassword(e.target.value)}
            value={password}
            required
          />
          <Flex width="100%" justifyContent="center">
            <Button
              mt="20px"
              onClick={handleSubmit}
              bg="blue.900"
              color="white"
              alignSelf="center"
              _hover={{
                backgroundColor: "blue.100",
                color: "blue.900",
              }}
              isLoading={submitLoading}
            >
              Sign Up
            </Button>
          </Flex>
        </FormControl>
      </Flex>
    </Flex>
  );
};

export default RegisterForm;
