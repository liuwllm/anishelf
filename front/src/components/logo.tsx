import Link from "next/link";
import Image from "next/image";
import LogoImage from "../../public/logo.png";

export default function Logo() {
    return (
        <Link href="/" className="hover:cursor-pointer">
            <Image src={LogoImage} alt="Logo" height={60} width={175} />
        </Link>
    )
}