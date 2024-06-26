import Image from "next/image";
import { Inter } from "next/font/google";
import Results from "@/components/results";

const inter = Inter({ subsets: ["latin"] });

export default function Home() {
  return (
    <main
      className={`flex bg-slate-100 min-h-screen flex-col items-center justify-between p-24 ${inter.className}`}
    >
      <Results />
    </main>
  );
}
