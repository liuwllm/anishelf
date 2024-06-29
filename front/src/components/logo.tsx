import Link from "next/link";

export default function Logo() {
    return (
        <Link href="/">
            <h1 className="text-5xl text-blue-600 hover:text-blue-300 hover:cursor-pointer font-bold">Anishelf</h1>
        </Link>
    )
}