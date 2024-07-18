import Image from "next/image";
import { Inter } from "next/font/google";
import { Search } from "@/components/ui/search";
import Results from "@/components/results";

const inter = Inter({ subsets: ["latin"] });

export default function Home() {
  return (
    <>
    <title>Anishelf</title>
      <main
        className={`flex bg-slate-100 min-h-screen flex-col gap-10 items-center justify-between px-48 py-24 ${inter.className}`}
      >
        <Results />
      </main>
    </>
  );
}
