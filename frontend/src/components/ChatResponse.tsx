import NavBar from './NavBar'
import PromptInputBox from './PromptInputBox'
import FormattedMessage from './FormattedMessage'

const ChatResponse = () => {
    return (
    <div className='h-screen flex flex-col bg-background'>
        <NavBar />
        
        <div className='flex-1 overflow-y-auto'>
            <FormattedMessage />
        </div>
        
        <div className='flex flex-col items-center justify-center py-4 flex-shrink-0'>
            <div className='w-4/5 md:w-7/12'>
                <PromptInputBox />
            </div>
        </div>
    </div>
)
}

export default ChatResponse
