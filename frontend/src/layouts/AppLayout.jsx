import { Outlet } from "react-router-dom";
import TopNav from "../components/TopNav";

const AppLayout = () => {
  return (
    <div className="app-shell">
      <TopNav />
      <main className="container app-main">
        <Outlet />
      </main>
    </div>
  );
};

export default AppLayout;
