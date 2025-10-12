import {create} from "zustand";

const chatStore = (set:any, get:any) => ({
    chatMessages: [],

    addMessage: (role:string, message:string) => {
        set((state:any)=>({chatMessages: [...state.chatMessages, {role,message}]}))
    },

    updateLastBotMessage: (msg:string) =>
    set((state) => ({
      chatMessages: state.chatMessages.map((m, i) =>
        i === state.chatMessages.length - 1 && m.role === "bot"
          ? { ...m, message: msg }
          : m
      ),
    })),
    
    clearMessages : () => {set({chatMessages: []})}
})


const useChatStore = create(chatStore);

export default useChatStore