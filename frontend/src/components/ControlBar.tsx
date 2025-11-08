import { Slider } from "@/components/ui/slider"
import useChatStore from '@/store/chatStore'

const ControlBar = () => {
    const { temperature, similarity, setTemperature, setSimilarity } = useChatStore();

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
                    onValueChange={(val)=>setTemperature(val[0])}
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
                    onValueChange={(val)=>setSimilarity(val[0])}
                    min={0}
                    max={1}
                    step={0.1}
                />
            </div>
        </div>
    )
}

export default ControlBar