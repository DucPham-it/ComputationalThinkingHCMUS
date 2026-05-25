import Navbar from "../components/common/Navbar";
import Footer from "../components/common/Footer";

export default function MainLayout({ children }) {
  return (
    <div className="app-shell">
      <div className="ambient-stage" aria-hidden="true">
        <div className="ambient-panels" />
        <div className="ambient-routes" />
        <div className="ambient-grid" />
        <div className="ambient-scan" />
      </div>
      <Navbar />
      <main className="container app-main">{children}</main>
      <Footer />
    </div>
  );
}
