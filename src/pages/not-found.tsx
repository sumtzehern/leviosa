
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

export default function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background">
      <div className="max-w-md text-center">
        <h1 className="text-6xl font-bold text-marine">404</h1>
        <p className="text-xl mt-4 mb-8">Page not found</p>
        <Button onClick={() => navigate("/")}>Return to Home</Button>
      </div>
    </div>
  );
}
