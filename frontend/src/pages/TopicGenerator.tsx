import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import GeneratorForm from "@/components/GeneratorForm";
import { GeneratorFormData } from "@/types/generator";

const TopicGenerator = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (data: GeneratorFormData) => {
    setIsLoading(true);
    sessionStorage.setItem("generatorData", JSON.stringify(data));
    setTimeout(() => {
      navigate("/plan-editor");
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="pt-24 pb-12 px-4">
        <div className="container mx-auto max-w-3xl">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold mb-4">Topic Generator</h1>
            <p className="text-muted-foreground">
              Create presentations based on a topic name
            </p>
          </div>
          
          <GeneratorForm variant="topic" onSubmit={handleSubmit} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
};

export default TopicGenerator;
