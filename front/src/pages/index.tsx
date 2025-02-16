import Image from "next/image";
import { Inter } from "next/font/google";
import Results from "@/components/results";
import LogoImage from "../../public/logo.png";

const inter = Inter({ subsets: ["latin"] });

export default function Home() {
  return (
    <>
    <title>Anishelf</title>
      <main
        className={`flex bg-slate-100 min-h-screen flex-col gap-10 items-center justify-between px-6 sm:px-12 md:px-24 lg:px-48 py-8 sm:py-12 md:py-16 ${inter.className}`}
      >
        <Image src={LogoImage} alt="Logo" height={150} width={437} />
        <Results />
      </main>
    </>
  );
}
