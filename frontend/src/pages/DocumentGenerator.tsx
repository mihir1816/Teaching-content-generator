import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import GeneratorForm from "@/components/GeneratorForm";
import { GeneratorFormData } from "@/types/generator";

const DocumentGenerator = () => {
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
            <h1 className="text-4xl font-bold mb-4">Document Generator</h1>
            <p className="text-muted-foreground">
              Upload documents to generate presentations
            </p>
          </div>
          
          <GeneratorForm variant="document" onSubmit={handleSubmit} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
};

export default DocumentGenerator;
