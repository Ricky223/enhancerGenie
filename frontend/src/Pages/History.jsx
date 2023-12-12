import {
  Badge,
  Button,
  Flex,
  Table,
  TableContainer,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
  useToast,
} from "@chakra-ui/react";
import axios from "axios";
import { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AuthContext, { useAuth } from "../Components/AuthProvider";
import SimpleTable from "../Components/SimpleTable";
import { ViewIcon, DeleteIcon } from "@chakra-ui/icons";

const History = () => {
  const [historyData, setHistoryData] = useState([]);
  const navigate = useNavigate();
  const [tableLoading, setTableLoading] = useState(false);
  const { auth, setAuth } = useContext(AuthContext);
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [resultCount, setResultCount] = useState(0);
  const toast = useToast();
  const { deleteAccessToken } = useAuth();

  useEffect(() => {
    getLocalHistory();
  }, [auth, page]);

  const getLocalHistory = () => {
    const history = localStorage.getItem("history");

    let headers = {
      "Content-Type": "application/json",
    };

    if (auth && auth.accessToken !== undefined) {
      headers["Authorization"] = `Bearer ${auth.accessToken}`;
    }

    if (history) {
      const histArr = history.split(",");

      axios
        .post(
          "/api/history/metadata",
          {
            fps: histArr.map((item) => item.split("_")[0]),
          },
          {
            headers: headers,
            params: {
              page: page,
              query: searchQuery,
            },
          }
        )
        .then((res) => {
          if (res.data) {
            for (let i = 0; i < res.data.results.length; i++) {
              for (let j = 0; j < histArr.length; j++) {
                const storedHistoryValue = histArr[j].split("_");
                if (
                  res.data.results[i]["fingerprint"] === storedHistoryValue[0]
                ) {
                  res.data.results[i]["lastUpdated"] = storedHistoryValue[1];
                }
              }
            }
            setHistoryData(res.data.results);
            setResultCount(res.data.count);
          }
        })
        .catch((err) => {
          if (err.response.status === 401) {
            deleteAccessToken().then((res) => {
              setAuth({});
              navigate("/home");
              toast({
                title: "Logged out",
                description:
                  "Your login session has expired, please login again.",
                status: "error",
                duration: 3000,
                isClosable: true,
                position: "top",
                variant: "left-accent",
              });
            });
          }
        });
    }
  };

  const handleRemove = (data) => {
    if (auth && auth.accessToken !== undefined) {
      // remove from db
      axios
        .post(
          "/api/history/delete",
          {
            fp: data.fingerprint,
          },
          {
            headers: {
              Authorization: `Bearer ${auth.accessToken}`,
            },
          }
        )
        .then((res) => {
          toast({
            title: "History item deleted",
            description:
              "You've successfully removed result from your history.",
            status: "success",
            duration: 5000,
            isClosable: true,
            position: "top",
            variant: "left-accent",
          });
        })
        .catch((err) => {
          toast({
            title: "Failed to delete",
            description: "There was an issue deleting your history, try again.",
            status: "error",
            duration: 5000,
            isClosable: true,
            position: "top",
            variant: "left-accent",
          });
        });
    } else {
      // remove from localStorage
      let history = localStorage.getItem("history");
      var values = history.split(",");

      for (var i = 0; i < values.length; i++) {
        var currentFingerprint = values[i].split("_")[0];

        if (currentFingerprint === data.fingerprint) {
          values.splice(i, 1);
          break;
        }
      }

      var resultString = values.join(",");
      localStorage.setItem("history", resultString);

      toast({
        title: "History item deleted",
        description: "You've successfully removed result from your history.",
        status: "success",
        duration: 5000,
        isClosable: true,
        position: "top",
        variant: "left-accent",
      });
    }

    getLocalHistory();
  };

  return (
    <Flex p={6} direction="column">
      <Flex direction="column">
        <Text fontWeight="bold" fontSize="2xl">
          History
        </Text>

        {auth && auth.accessToken ? (
          <Text color="blackAlpha.600" fontSize="sm">
            History is saved to your account and can be accessed across multiple
            devices.
          </Text>
        ) : (
          <Text color="blackAlpha.600" fontSize="sm">
            Local history is stored in browser cache. To persist your history
            across multiple devices, please login.
          </Text>
        )}
      </Flex>
      <SimpleTable
        headers={["Assembly", "Tissue", "Algorithms", "Last updated", ""]}
        rowData={
          historyData &&
          historyData.map((h) => ({
            assembly: h.assembly,
            tissue: h.tissue,
            algorithms: h.algorithms,
            lastUpdated: h.lastUpdated,
            fingerprint: h.fingerprint,
          }))
        }
        isLoading={tableLoading}
        page={page}
        totalResults={resultCount}
        onSearchChange={(newValue) => setSearchQuery(newValue)}
        onSearchSubmit={() => getLocalHistory()}
        actions={[
          {
            name: "View",
            onClick: (data) => navigate(`/chart_results/${data.fingerprint}`),
            buttonIcon: <ViewIcon />,
          },
          {
            name: "Delete",
            onClick: handleRemove,
            buttonIcon: <DeleteIcon />,
            colorScheme: "red",
          },
        ]}
      />
    </Flex>
  );
};

export default History;
