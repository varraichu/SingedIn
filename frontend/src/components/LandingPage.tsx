import NavBar from './NavBar'
import PromptInputBox from './PromptInputBox';
import FormattedMessage from './FormattedMessage';
import CopyText from './CopyText';
import ControlBar from './ControlBar';

const LandingPage = () => {

    return (
        <div className="h-screen flex flex-col bg-background">
            <NavBar />
            {/* <Sidebar/> */}
            <div className='flex flex-row flex-1 min-h-0'>

                <div className="flex flex-col flex-1 min-h-0 m-4">
                    <div className="relative flex-1 mb-1 rounded-xl border overflow-hidden">
                        <div className="h-full overflow-y-auto">
                            <FormattedMessage />
                        </div>
                    </div>

                    <div className='flex mb-1 w-full items-center justify-start'>
                        <CopyText />
                    </div>

                    <div className="flex-shrink-0">
                        <PromptInputBox showSuggestions={false} />
                    </div>
                </div>

                <ControlBar/>
            </div>
        </div>
    )
}

export default LandingPage