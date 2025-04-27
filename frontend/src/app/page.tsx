import Image from "next/image";
import Chat from '@/components/Chat';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-4 lg:p-8 bg-gray-50">
      <div className="w-full max-w-6xl">
        <header className="mb-8 text-center">
          <h1 className="text-4xl font-bold mb-3 text-gray-800">Tool-Use Agent Demo</h1>
          <div className="flex items-center justify-center gap-2 text-gray-600 mb-4">
            <span>Powered by</span>
            <div className="flex items-center gap-2">
              <Image src="/next.svg" alt="Next.js" width={80} height={20} className="dark:invert" />
              <span>+</span>
              <span className="font-semibold">FastAPI</span>
              <span>+</span>
              <span className="text-blue-600 font-semibold">LangChain</span>
              <span>+</span>
              <span className="text-purple-600 font-semibold">LangGraph</span>
              <span>+</span>
              <span className="text-yellow-600 font-semibold">Gemini 2.0</span>
            </div>
          </div>
          <p className="max-w-2xl mx-auto text-gray-500">
            This demo showcases an AI agent that can use external tools to accomplish tasks. 
            The agent is built with LangChain, LangGraph, and Google&apos;s Gemini 2.0 Flash model.
          </p>
        </header>
        
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
          <div className="lg:col-span-3">
            <div className="bg-white shadow-lg rounded-lg border h-[70vh]">
              <Chat />
            </div>
          </div>
          
          <div className="lg:col-span-1">
            <div className="bg-white shadow-lg rounded-lg border p-4 h-full">
              <h2 className="text-lg font-semibold mb-3">About this Demo</h2>
              
              <div className="space-y-4 text-sm">
                <section>
                  <h3 className="font-medium text-gray-800">Available Tools</h3>
                  <ul className="mt-1 space-y-1 list-disc list-inside">
                    <li><span className="font-medium text-blue-600">get_weather</span> - Get weather information for a location</li>
                    <li><span className="font-medium text-blue-600">search_web</span> - Search the web for information</li>
                    <li><span className="font-medium text-blue-600">calculate</span> - Evaluate mathematical expressions</li>
                    <li><span className="font-medium text-blue-600">lookup_definition</span> - Find definitions of terms</li>
                  </ul>
                </section>
                
                <section>
                  <h3 className="font-medium text-gray-800">Implementation Details</h3>
                  <p className="mt-1">
                    The backend uses LangChain and LangGraph to orchestrate a workflow that integrates Gemini 2.0 Flash with external tools. The frontend is built with Next.js and uses a modern React architecture.
                  </p>
                </section>
                
                <section>
                  <h3 className="font-medium text-gray-800">Try Asking</h3>
                  <ul className="mt-1 space-y-1 text-gray-600">
                    <li>• &ldquo;What&apos;s the weather in Tokyo?&rdquo;</li>
                    <li>• &ldquo;Calculate the square root of 144&rdquo;</li>
                    <li>• &ldquo;Search for information on NLP&rdquo;</li>
                    <li>• &ldquo;What&apos;s the definition of LangGraph?&rdquo;</li>
                    <li>• &ldquo;Tell me about yourself&rdquo;</li>
                  </ul>
                </section>
                
                <section>
                  <h3 className="font-medium text-gray-800">Technical Stack</h3>
                  <div className="mt-1 text-xs text-gray-600 space-y-1">
                    <div><span className="font-medium">Frontend:</span> Next.js, React, TypeScript, Tailwind CSS</div>
                    <div><span className="font-medium">Backend:</span> FastAPI, LangChain, LangGraph</div>
                    <div><span className="font-medium">Model:</span> Gemini 2.0 Flash</div>
                  </div>
                </section>
              </div>
            </div>
          </div>
        </div>
        
        <footer className="text-center text-sm text-gray-500">
          <p className="mb-1">
            Built with Next.js (frontend) and FastAPI + LangChain + LangGraph + Gemini 2.0 Flash (backend)
          </p>
          <p>
            © {new Date().getFullYear()} Tool-Use Agent Demo
          </p>
        </footer>
      </div>
    </main>
  );
}
