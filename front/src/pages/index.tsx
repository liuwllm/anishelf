import Image from "next/image";
import { Inter } from "next/font/google";
import Results from "@/components/home/results";
import LogoImage from "../../public/logo.png";

const inter = Inter({ subsets: ["latin"] });

export default function Home() {
  return (
    <>
    <title>Anishelf</title>
      <main
        className={`flex bg-slate-100 min-h-screen flex-col gap-10 items-center justify-between px-48 py-16 ${inter.className}`}
      >
        <Image src={LogoImage} alt="Logo" height={150} width={437} />
        <Results />
      </main>
    </>
  );
}
