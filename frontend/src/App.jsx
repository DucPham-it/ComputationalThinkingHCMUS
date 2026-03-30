/**
 * Root React component.
 *
 * Input:
 * - route state from react-router
 * - auth/app providers from context
 *
 * Output:
 * - page layout with routed content
 */
import MainLayout from "./layouts/MainLayout";
import AppRoutes from "./routes/AppRoutes";

export default function App() {
  return (
    <MainLayout>
      <AppRoutes />
    </MainLayout>
  );
}
