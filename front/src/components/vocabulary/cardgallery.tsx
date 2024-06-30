import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover"

interface CardGalleryProps {
    words: Vocabulary[]
}

export interface Vocabulary {
    id: number;
    keb: string[];
    reb: string[];
    sense: string[];
}

export default function CardGallery({ words }: CardGalleryProps ) {
    return (
        <div className="flex flex-col gap-4">
            {words.map((word: Vocabulary) =>
                <div className="flex flex-row gap-12 p-8 shadow-md rounded-lg bg-white items-center" key={word.id}>
                    {
                        // Check if keb exists
                        (word.keb[0]) ? 
                        (
                            // Check if more than one keb exists
                            <div className="flex flex-col">
                                {(word.keb[1]) ? 
                                (<Popover>
                                    <PopoverTrigger className="bg-slate-200 p-2 rounded-lg">
                                        <h1 className="text-4xl">{word.keb[0]}</h1>
                                    </PopoverTrigger>
                                    <PopoverContent className="text-center">
                                        <h2 className="text-md">{word.keb.slice(1, -1).map(keb => keb.concat(" / ")).concat(word.keb.slice(-1)[0])}</h2>
                                        <p className="text-xs text-slate-500">variants</p>
                                    </PopoverContent>
                                </Popover>) : 
                                (<h1 className="text-center p-4 text-4xl">{word.keb[0]}</h1>)}
                                
                                <h3 className="text-center p-2 text-slate-500 text-sm">
                                    {word.reb.slice(1,-1).map(reb => reb.concat(" / ")).concat(word.reb.slice(-1)[0])}
                                </h3>
                            </div>
                        ) :
                        // Only a reb exists
                        (<h1 className="text-center p-4 text-4xl">{word.reb[0]}</h1>)
                    }
                    <ol className="list-decimal">
                        {word.sense.map(sense =><li key={word.id}>{sense}</li>)}
                    </ol>
                </div>
            )}
        </div>
    )
}