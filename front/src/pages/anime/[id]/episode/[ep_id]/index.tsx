import { GetServerSideProps, GetServerSidePropsContext } from 'next';
import CardGallery, { WordGroup } from "@/components/cardgallery";
import NavBar from "@/components/navbar";
import Logo from "@/components/logo";
import Export from "@/components/export";
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import Link from "next/link";

interface Data {
    vocab: WordGroup[];
    prev: boolean;
    next: boolean;
}

interface VocabPageProps {
    data: Data;
    title: string;
    show_id: string;
    ep_id: string;
    offset: string;
}

export const getServerSideProps: GetServerSideProps = async (context: GetServerSidePropsContext) => {
    let show_id: string = context.query.id as string;
    let ep_id: string = context.query.ep_id as string;
    let offset: string = context.query.offset as string;
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
            `${process.env.NEXT_PUBLIC_BACK}get_subtitles?`+ new URLSearchParams({
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
            `${process.env.NEXT_PUBLIC_BACK}analyze_episode?` + new URLSearchParams({
                anilist_id: show_id,
                episode: ep_id,
            }),
            {
                method: 'POST',
                body: formData
            }
        )
    }

    const lookupRes = await fetch(
        `${process.env.NEXT_PUBLIC_BACK}get_episode?` + new URLSearchParams({
            anilist_id: show_id,
            episode: ep_id,
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
    return { props: { data, title, show_id, ep_id, offset } }
}

export default function Vocab({ data, title, show_id, ep_id, offset }: VocabPageProps) {
    return (
        <>
        <title>Anishelf - {title}: Episode {ep_id} Vocabulary</title>
        <div className=" flex flex-col">
            <div className="flex flex-col px-6 sm:px-12 md:px-24 lg:px-48 py-8 sm:py-12 md:py-16 gap-4 min-h-screen bg-slate-100">
                <Logo />
                <div className="flex flex-row justify-between w-full">
                    <Link href={`/anime/${show_id}`}>
                        <div className="flex flex-row items-center gap-4 text-slate-800 hover:text-slate-500 hover:cursor-pointer">
                            <ArrowBackIcon />
                            <h1 className="text-lg sm:text-xl md:text-2xl lg:text-3xl font-semibold">{title}</h1>
                        </div>
                    </Link>
                    <Export id={show_id} episode={ep_id} />
                </div>
                <h2 className="text-lg sm:text-xl md:text-2xl lg:text-3xl font-semibold text-slate-800">Episode {ep_id}</h2>
                <h3 className="text-md sm:text-lg md:text-xl lg:text-2xl font-medium text-slate-800">Vocabulary</h3>
                <CardGallery words={data.vocab} />
                <NavBar prev={data.prev} next={data.next} id={show_id} episode={ep_id} title={title} offset={offset}/>
            </div>
        </div>
        </>
    )
}