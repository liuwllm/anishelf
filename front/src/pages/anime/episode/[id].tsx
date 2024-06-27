import { GetServerSideProps, GetServerSidePropsContext } from 'next';


interface VocabPageProps {
    data: Vocabulary
}

interface Vocabulary {
    id: number;
    keb: string[];
    reb: string[];
    sense: string[];
}

export const getServerSideProps: GetServerSideProps = async (context: GetServerSidePropsContext) => {
    const id = context.query.id
    
    // Pass data to the page via props
    return { props: { } }
}

export default function Vocab({ }: VocabPageProps) {

}