import React, { useState } from 'react'
import NavBar from './NavBar'
import { MicVocal } from 'lucide-react';
import PromptInputBox from './PromptInputBox';

const LandingPage = () => {

    return (
        <div className='h-screen flex flex-col bg-background'>
            <NavBar></NavBar>
            <div className='flex flex-col items-center justify-center w-full flex-1 overflow-y-auto'>
                <div className='flex flex-row items-center justify-center mb-4'>
                    <h1>Hello, lets SING! </h1>
                    {/* <span><MicVocal /></span> */}
                </div>
                <div className='sm:w-7/12'>
                    <PromptInputBox showSuggestions={true} />
                </div>
            </div>
        </div>
    )
}

export default LandingPage
