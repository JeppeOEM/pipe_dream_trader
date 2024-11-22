import { Outlet } from "react-router-dom";
import Navbar from "@/components/shared/navigation/Navbar"

function Root() {
  return (
    <div>
      <Navbar></Navbar>
      <Outlet />
    </div>
  );
}

export default Root;
