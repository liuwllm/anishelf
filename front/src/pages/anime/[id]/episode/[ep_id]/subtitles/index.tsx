import Logo from "@/components/logo";
import Link from "next/link";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button";
import { GetServerSideProps, GetServerSidePropsContext } from 'next';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

interface Data {
    id: number;
    name: string;
    link: string;
    size: number;
    last_modified: string;
}

interface SubtitlePageProps {
    data: Data[];
    show_id: string;
    title: string;
}


export const getServerSideProps: GetServerSideProps = async (context: GetServerSidePropsContext) => {
    let show_id: string = context.query.id as string;
    let ep_id: string = context.query.ep_id as string;
    let title: string = context.query.title as string;

    const checkEpisodeRes = await fetch(
        `${process.env.NEXT_PUBLIC_BACK}check_episode?` + new URLSearchParams({
            anilist_id: show_id,
            episode: ep_id,
        }),
        {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        }
    )
    const checkEpisodeData = await checkEpisodeRes.json();

    if (checkEpisodeData.episode_exists === false) {
        const getSubtitleRes = await fetch(
            `${process.env.NEXT_PUBLIC_BACK}get_subtitles?` + new URLSearchParams({
                anilist_id: show_id,
                episode: ep_id,
            }),
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        )
    }

    const dlSubsRes = await fetch(
        `${process.env.NEXT_PUBLIC_BACK}download_subtitles?` + new URLSearchParams({
            anilist_id: show_id,
            episode: ep_id,
        }),
        {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        }
    )
    const data = await dlSubsRes.json();
    
    data.forEach((sub: Data) => {
        const date = new Date(sub.last_modified).toLocaleString();
        sub.last_modified = date
    })

    return { props: { data, show_id, title } }
}

export default function Show({ data, show_id, title }: SubtitlePageProps) {
    return (
        <>
        <title>Anishelf - {title} Subtitles</title>
        <div className="flex gap-12 flex-col min-h-screen bg-slate-100 px-48 py-12">
            <Logo />
            <Link href={`/anime/${show_id}`}>
                <div className="flex flex-row items-center gap-4 text-slate-800 hover:text-slate-500 hover:cursor-pointer">
                    <ArrowBackIcon />
                    <h2 className="text-xl">Back</h2>
                </div>
            </Link>
            <h1 className="text-slate-800 font-bold text-3xl">{title} Subtitles</h1>
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Size</TableHead>
                        <TableHead>Last Modified</TableHead>
                        <TableHead>Link</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {data.map(subtitle => {
                        return (
                            <TableRow key={subtitle.id}>
                                <TableCell>{subtitle.name}</TableCell>
                                <TableCell>{subtitle.size} B</TableCell>
                                <TableCell>{subtitle.last_modified}</TableCell>
                                <TableCell>
                                    <Link href={subtitle.link}>
                                        <Button>Download</Button>
                                    </Link>
                                </TableCell>
                            </TableRow>
                        )
                    })}
                </TableBody>
            </Table>
        </div>
        </>
    )
}