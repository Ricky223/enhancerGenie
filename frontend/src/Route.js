import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  Outlet,
} from "react-router-dom";
import Home from "./Pages/Home";
import Usage from "./Pages/Usage";
import History from "./Pages/History";
import Navbar from "./Components/Navbar";
import Footer from "./Components/Footer";
import Result from "./Pages/Result";
import Login from "./Pages/Login";
import ViewResults from "./Pages/ViewResults";
import Register from "./Pages/Register";
import ViewChartResult from "./Pages/ViewChartResult";
import NewHome from "./Pages/NewHome";

const RouteTable = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          element={
            <>
              <Navbar />
              <Outlet />
              <Footer position="fixed" w="100%" bottom="0" />
            </>
          }
        >
          <Route path="/home" element={<NewHome />} />
          <Route path="/oldhome" element={<Home />} />
          <Route path="/usage" element={<Usage />} />
          <Route path="/history" element={<History />} />
          <Route path="/result" element={<Result />} />
          <Route path="/results/:fp" element={<ViewResults />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/chart_results/:fp" element={<ViewChartResult />} />
          <Route path="/" element={<Navigate replace to="/home" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default RouteTable;
