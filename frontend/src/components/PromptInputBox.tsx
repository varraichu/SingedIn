import React, { useState } from 'react'
import {
    PromptInput,
    PromptInputActionAddAttachments,
    PromptInputActionMenu,
    PromptInputActionMenuContent,
    PromptInputActionMenuItem,
    PromptInputActionMenuTrigger,
    PromptInputAttachment,
    PromptInputAttachments,
    PromptInputBody,
    PromptInputButton,
    PromptInputSubmit,
    PromptInputTextarea,
    PromptInputToolbar,
    PromptInputTools,
    usePromptInputAttachments,
    PromptInputModelSelect,
    PromptInputModelSelectContent,
    PromptInputModelSelectItem,
    PromptInputModelSelectTrigger,
    PromptInputModelSelectValue,
} from '@/components/ai-elements/prompt-input';
import { Suggestion, Suggestions } from '@/components/ai-elements/suggestion';
import { useNavigate } from "react-router";
import useChatStore from '@/store/chatStore';
import { json } from 'stream/consumers';

const suggestions = [
    'Can you explain how to play tennis?',
    'What is the weather in Tokyo?',
    'How do I make a really good fish taco?',
];
const models = [
    { id: 'gpt-4o', name: 'GPT-4o' },
];
type PromptInputBoxProps = {
    showSuggestions?: boolean;
};

const PromptInputBox = ({ showSuggestions = false }: PromptInputBoxProps) => {
    const [model, setModel] = useState<string>(models[0].id);
    const [input, setInput] = useState('');
    const addChatMessage = useChatStore((state) => state.addMessage);

    let navigate = useNavigate();

    const sendMessage = async () => {
        console.log("input: ", input);
        addChatMessage("user", input)
        
        addChatMessage("bot", "")
        
        navigate("/chat/response");

        try {
            const url = 'http://127.0.0.1:8000/api/chat'
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: input })
            })
            setInput('')
            const botResponse = await response.json()
            // console.log("botReponse: ", botResponse)
            // addChatMessage("bot", botResponse.Massage)
            useChatStore.getState().updateLastBotMessage(botResponse.message);
        }
        catch (error) {
            console.log("an error occured when sending a message: ", error)
        }
    }

    const handleSuggestionClick = (suggestion: string) => {
        setInput(suggestion)
    };

    return (
        <div className='flex flex-col items-center gap-5'>
            <div className='w-full'>
                <PromptInput onSubmit={sendMessage} className="relative">
                    <PromptInputBody>
                        <PromptInputTextarea
                            value={input}
                            placeholder="Say something..."
                            onChange={(e) => setInput(e.currentTarget.value)}
                        />
                    </PromptInputBody>
                    <PromptInputToolbar>
                        <PromptInputTools>
                            <PromptInputActionMenu>
                            </PromptInputActionMenu>
                            <PromptInputModelSelect
                                onValueChange={(value) => {
                                    setModel(value);
                                }}
                                value={model}
                            >
                                <PromptInputModelSelectTrigger>
                                    <PromptInputModelSelectValue />
                                </PromptInputModelSelectTrigger>
                                <PromptInputModelSelectContent>
                                    {models.map((model) => (
                                        <PromptInputModelSelectItem key={model.id} value={model.id}>
                                            {model.name}
                                        </PromptInputModelSelectItem>
                                    ))}
                                </PromptInputModelSelectContent>
                            </PromptInputModelSelect>
                        </PromptInputTools>
                        <PromptInputSubmit
                            disabled={false}
                            status={'ready'}
                        />
                    </PromptInputToolbar>
                </PromptInput>
            </div>
            {showSuggestions && (
                <div className='hidden sm:block'>
                    <Suggestions>
                        {suggestions.map((suggestion) => (
                            <Suggestion
                                key={suggestion}
                                onClick={handleSuggestionClick}
                                suggestion={suggestion}
                            />
                        ))}
                    </Suggestions>
                </div>
            )}
        </div>
    )
}

export default PromptInputBox
