import { Slider } from "@/components/ui/slider"
import useChatStore from '@/store/chatStore'
import { useState } from "react";
import { Button } from "./ui/button";

const ControlBar = () => {
    const { temperature, similarity, setTemperature, setSimilarity } = useChatStore();
    const [loading, setLoading] = useState(false);
    const [lyricsFetched, setLyricsFetched] = useState(false);

    const getLikedSongs = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/get_liked_songs');
            if (!response.ok) {
                throw new Error(`Response Status: ${response.status}`)
            }
            const data = await response.json()
            console.log("Response: ", data?.message);
            return data;

        } catch (error) {
            console.log("Error in getting liked songs: ", getLikedSongs)
        }
    }

    const getSongsLyrics = async () => {
        try {
            setLyricsFetched(false);
            const response = await fetch('http://127.0.0.1:8000/api/get_lyrics');
            if(!response.ok){
                throw new Error(`Response status: ${response.status}`)
            }
            
            const data = await response.json()
            console.log("Lyrics response: ", data?.message)
            setLyricsFetched(true);
            return data

        } catch (error) {
            console.log("Error getting lyrics: ", error)
        }
    }

    const getLyricsHandler = async () => {
        try {
            setLoading(true);
            const likedSongs = await getLikedSongs();
            const lyrics = await getSongsLyrics();
            setLoading(false);
        } catch (error) {
            console.log("error: ", error)
        }
    }

    return (
        <div className='border rounded-xl m-4 p-4 w-60 flex-shrink-0 space-y-6'>
            <h3 className='font-semibold text-lg mb-4'>Controls</h3>

            <div className='space-y-2'>
                <div className='flex justify-between items-center'>
                    <label className='text-sm font-medium'>Temperature</label>
                    <span className='text-sm text-muted-foreground'>{temperature.toFixed(1)}</span>
                </div>
                <Slider
                    value={[temperature]}
                    onValueChange={(val) => setTemperature(val[0])}
                    min={0}
                    max={1}
                    step={0.1}
                />
            </div>

            <div className='space-y-2'>
                <div className='flex justify-between items-center'>
                    <label className='text-sm font-medium'>Similarity</label>
                    <span className='text-sm text-muted-foreground'>{similarity.toFixed(1)}</span>
                </div>
                <Slider
                    value={[similarity]}
                    onValueChange={(val) => setSimilarity(val[0])}
                    min={0}
                    max={1}
                    step={0.1}
                />
            </div>

            <div className="flex flex-1">
                <Button
                    size="sm"
                    className="text-sm flex flex-1"
                    onClick={getLyricsHandler}
                    disabled={loading}
                >
                    {loading ? "Loading..." : !lyricsFetched ? "Fetch Lyrics" : "Lyrics Fetched"}
                </Button>
            </div>
        </div>
    )
}

export default ControlBar