<script setup>
import SendIcon from '../../icons/SendIcon.vue';
import MicIcon from '../../icons/MicIcon.vue';
import { useTemplateRef, ref } from 'vue';
import streamApi from '@/js/http/streamApi';

const inputRef = useTemplateRef('input-ref')
const emits = defineEmits(['pushBackMessage', 'addToLastMessage'])
const message = ref('')
const props = defineProps(['friendID'])
let isProcessing = false

function focus() {
    inputRef.value.focus()
}

function handleKeydown(e) {
  // Enter发送
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()

    handleSend()
  }
}

async function handleSend() {
    if (isProcessing) return
    isProcessing = true

    const content = message.value.trim()
    if (!content) return
    message.value = ''

    emits('pushBackMessage', {
        role: 'user',
        content: content,
        id: crypto.randomUUID(),
    })
    emits('pushBackMessage', {
        role: 'AI',
        content: '',
        id: crypto.randomUUID(),
    })

    try {
        await streamApi('/api/friend/message/chat/', {
            body: {
                friend_id: props.friendID,
                message: content,
            },
            onmessage(data, isDone) {
                if (isDone) {
                    isProcessing = false
                } else if (data.content) {
                    emits('addToLastMessage', data.content)
                }
            },
            onerror(error) {
                isProcessing = false
            }
        })
    } catch (error) {
        isProcessing = false
    }

}

defineExpose({
    focus,
})
</script>

<template>
    <form @submit.prevent="handleSend" class="absolute bottom-4 left-2 h-12 w-86 flex items-center">
        <textarea 
            ref="input-ref"
            v-model="message"
            @keydown="handleKeydown"
            rows="1"
            class="bg-black/30 backdrop-blur-sm text-white text-base w-full rounded-2xl p-3 pr-20 resize-none outline-none leading-6"
            placeholder="文本输入..."
        ></textarea>
        <div class="absolute right-2 w-8 h-8 flex justify-center items-center cursor-pointer">
            <SendIcon @click="handleSend" />
        </div>
        <div class="absolute right-10 w-8 h-8 flex justify-center items-center cursor-pointer">
            <MicIcon />
        </div>
    </form>
</template>

<style scoped>

</style>