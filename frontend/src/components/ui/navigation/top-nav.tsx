import NavItem from "./nav-item";
import Dropdown from "./dropdown";
import { Link } from "react-router-dom";
import { CircleUserIcon } from "lucide-react";
import useAuthStore from "@/lib/hooks/useAuthStore";
import { queryClient } from "@/main";

export default function TopNav() {
  const { logout } = useAuthStore()
  return (
    <nav className="bg-gray-800 p-3 z-30">
      <ul className="flex flex-row items-center justify-between">
        <div className="flex flex-row">
          <li className="text-white text-xl">MyApp</li>
          <NavItem to="/" label="Dashboard" />
          <NavItem to="/data" label="Data" />
          <Dropdown textColor="text-white" label="Strategies" animation={true}>
            <Link to="/select-strategy" className="block text-white px-4 py-2">View all</Link>
            <Link to="/create-strategy" className="block text-white px-4 py-2">Create new strategy</Link>
          </Dropdown>
        </div>
        <div className="flex space-x-4">
          <Dropdown textColor="text-white" icon={CircleUserIcon} animation={false} direction="right">
            <button onClick={() => { logout(queryClient) }} className="block text-white px-4 py-2">Logout</button>
            <Link to="/profile" className="block text-white px-4 py-2">Create new profile</Link>
          </Dropdown>
        </div>

      </ul>
    </nav >
  );
}