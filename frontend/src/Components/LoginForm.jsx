import React, { useContext, useEffect, useRef, useState } from "react";
import {
  Alert,
  Button,
  Flex,
  FormControl,
  FormLabel,
  Input,
  Link,
  Text,
} from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import AuthContext from "./AuthProvider";
import axios from "axios";

const LoginForm = () => {
  const navigate = useNavigate();

  const { setAuth } = useContext(AuthContext);

  const userRef = useRef();
  const errorRef = useRef();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [success, setSuccess] = useState(false);
  const [displayName, setDisplayName] = useState("");
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
      return;
    }

    try {
      const response = await axios.post(
        "/api/login",
        JSON.stringify({ username, password }),
        {
          headers: { "Content-Type": "application/json" },
          withCredentials: true,
        }
      );

      setSubmitLoading(false);
      if (response.data.token) {
        localStorage.setItem(
          "user",
          JSON.stringify({ username, token: response.data.token })
        );
        setAuth({ username, accessToken: response.data.token });
      }

      setDisplayName(username);
      setUsername("");
      setPassword("");
      setSuccess(true);
    } catch (err) {
      setSubmitLoading(false);
      if (!err?.response) {
        setErrorMsg("No Server Response");
      } else if (err.response?.status === 400) {
        setErrorMsg("Missing Username or Password");
      } else if (err.response?.status === 401) {
        setErrorMsg("Wrong Username or Password");
      } else if (err.response?.status === 402) {
        setErrorMsg("User Doesn't Exist");
      } else {
        setErrorMsg("Login Failed");
      }
    }
  };

  const handleGoToHome = () => {
    navigate("/home");
  };

  return (
    <Flex
      direction="column"
      align="center"
      style={{ minHeight: "100vh"}}
    >
      {" "}
      {success ? (
        <Flex
          direction="column"
          my="50px"
          width="auto"
          style={{
            border: "1px solid gray",
            padding: "20px",
            borderRadius: "5px",
          }}
        >
          <Text fontSize="2xl" fontWeight="bold" align="center">
            Welcome, {displayName}
          </Text>
          <br />
          <Text
            align="center"
            onClick={handleGoToHome}
            style={{ cursor: "pointer" }}
          >
            Go to Home
          </Text>
        </Flex>
      ) : (
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
          {errorMsg && (
            <Alert ref={errorRef} aria-live="assertive">
              {errorMsg}
            </Alert>
          )}
          <Text fontSize="2xl" textAlign="center" fontWeight="bold">
            Sign In
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
                Sign In
              </Button>
            </Flex>
          </FormControl>

          <Text mt="20px" align="center">
            Need an Account?
            <br />
            <Link href="/register" fontWeight="bold" color="blue.900">
              Sign Up
            </Link>
          </Text>
        </Flex>
      )}
    </Flex>
  );
};

export default LoginForm;
