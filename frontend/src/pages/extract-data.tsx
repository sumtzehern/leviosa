
import { Layout } from "@/components/layout";

export default function ExtractDataPage() {
  return (
    <Layout>
      <div className="flex items-center justify-center h-[calc(100vh-180px)]">
        <div className="glass-card p-8 max-w-lg text-center">
          <h1 className="text-2xl font-semibold mb-4">Extract Data</h1>
          <p className="text-muted-foreground mb-4">
            This feature is coming soon! Extract structured data from your documents.
          </p>
          <div className="p-6 border border-dashed rounded-lg">
            <p className="text-sm text-muted-foreground">
              Future functionality will include:
            </p>
            <ul className="mt-2 text-sm space-y-1 text-left list-disc pl-4">
              <li>Table extraction from documents</li>
              <li>Form field detection</li>
              <li>Data export (CSV, JSON)</li>
              <li>Custom extraction templates</li>
            </ul>
          </div>
        </div>
      </div>
    </Layout>
  );
}
