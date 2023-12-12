import React from 'react';
import ReactDOM from 'react-dom/client';
import RouteTable from "./Route.js";

import { ChakraProvider } from "@chakra-ui/react"
import {AuthProvider} from "./Components/AuthProvider";

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <ChakraProvider>
      <AuthProvider>
          <RouteTable />
      </AuthProvider>
  </ChakraProvider>
);
