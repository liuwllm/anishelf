import { GetServerSideProps, GetServerSidePropsContext } from 'next';
import CardGallery, { Vocabulary } from "@/components/vocabulary/cardgallery";
import NavBar from "@/components/vocabulary/navbar";
import Logo from "@/components/logo";
import Export from "@/components/export";
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import Link from "next/link";

interface Data {
    vocab: Vocabulary[];
    prev: boolean;
    next: boolean;
}

interface VocabPageProps {
    data: Data;
    title: string;
    show_id: string;
    offset: string;
}

export const getServerSideProps: GetServerSideProps = async (context: GetServerSidePropsContext) => {
    let show_id: string = context.query.id as string;
    let offset: string = context.query.offset as string;
    let title: string = context.query.title as string;
    let num_ep: string = context.query.num_ep as string;

    for (let i = 1; i <= parseInt(num_ep); i++) {
        const checkEpisodeRes = await fetch(
            "http://127.0.0.1:5000/check_episode?" + new URLSearchParams({
                anilist_id: show_id,
                episode: i.toString(),
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
                "http://127.0.0.1:5000/get_subtitles?" + new URLSearchParams({
                    anilist_id: show_id,
                    episode: i.toString(),
                }),
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            )
            const getSubtitleData = await getSubtitleRes.json();
            const subUrl = getSubtitleData.subtitle_url;
            
            const formData = new FormData();
            formData.append('url', subUrl);
            if (subUrl.endsWith('.srt')) {
                formData.append('type', '.srt')
            }
            else if (subUrl.endsWith('.ass')) {
                formData.append('type', '.ass')
            }

            const analysisRes = await fetch(
                "http://127.0.0.1:5000/analyze_episode?" + new URLSearchParams({
                    anilist_id: show_id,
                    episode: i.toString(),
                }),
                {
                    method: 'POST',
                    body: formData
                }
            )
        }
    }

    const lookupRes = await fetch(
        "http://127.0.0.1:5000/get_show?" + new URLSearchParams({
            anilist_id: show_id,
            offset: offset
        }),
        {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        }
    )
    const data = await lookupRes.json();
    
    console.log(data);

    // Pass data to the page via props
    return { props: { data, title, show_id, offset } }
}

export default function Vocab({ data, title, show_id, offset }: VocabPageProps) {
    return (
        <div className=" flex flex-col">
            <div className="flex flex-col px-48 py-12 gap-4 min-h-screen bg-slate-100">
                <Logo />
                <div className="flex flex-row justify-between w-full">
                    <Link href={`/anime/${show_id}`}>
                        <div className="flex flex-row items-center gap-4 text-slate-800 hover:text-slate-500 hover:cursor-pointer">
                            <ArrowBackIcon />
                            <h1 className="text-4xl font-semibold">{title}</h1>
                        </div>
                    </Link>
                </div>
                <h2 className="text-2xl font-medium text-slate-800">Vocabulary</h2>
                <CardGallery words={data.vocab} />
            </div>
        </div>
    )
}