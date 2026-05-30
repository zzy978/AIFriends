<script setup>
import SendIcon from '../../icons/SendIcon.vue';
import MicIcon from '../../icons/MicIcon.vue';
import { useTemplateRef, ref, onUnmounted } from 'vue';
import streamApi from '@/js/http/streamApi';
import MicroPhone from './MicroPhone.vue';

const inputRef = useTemplateRef('input-ref')
const emits = defineEmits(['pushBackMessage', 'addToLastMessage'])
const message = ref('')
const props = defineProps(['friendID'])
let processId = 0
const showMic = ref(false)

let mediaSource = null;
let sourceBuffer = null;
let audioPlayer = new Audio(); // 全局播放器实例
let audioQueue = [];           // 待写入 Buffer 的二进制队列
let isUpdating = false;        // Buffer 是否正在写入

const initAudioStream = () => {
    audioPlayer.pause();
    audioQueue = [];
    isUpdating = false;

    mediaSource = new MediaSource();
    audioPlayer.src = URL.createObjectURL(mediaSource);

    mediaSource.addEventListener('sourceopen', () => {
        try {
            sourceBuffer = mediaSource.addSourceBuffer('audio/mpeg');
            sourceBuffer.addEventListener('updateend', () => {
                isUpdating = false;
                processQueue();
            });
        } catch (e) {
            console.error("MSE AddSourceBuffer Error:", e);
        }
    });

    audioPlayer.play().catch(e => console.error("等待用户交互以播放音频"));
};

const processQueue = () => {
    if (isUpdating || audioQueue.length === 0 || !sourceBuffer || sourceBuffer.updating) {
        return;
    }

    isUpdating = true;
    const chunk = audioQueue.shift();
    try {
        sourceBuffer.appendBuffer(chunk);
    } catch (e) {
        console.error("SourceBuffer Append Error:", e);
        isUpdating = false;
    }
};

const stopAudio = () => {
    audioPlayer.pause();
    audioQueue = [];
    isUpdating = false;

    if (mediaSource) {
        if (mediaSource.readyState === 'open') {
            try {
                mediaSource.endOfStream();
            } catch (e) {
            }
        }
        mediaSource = null;
    }

    if (audioPlayer.src) {
        URL.revokeObjectURL(audioPlayer.src);
        audioPlayer.src = '';
    }
};

const handleAudioChunk = (base64Data) => {  // 将语音片段添加到播放器队列中
    try {
        const binaryString = atob(base64Data);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        audioQueue.push(bytes);
        processQueue();
    } catch (e) {
        console.error("Base64 Decode Error:", e);
    }
};

onUnmounted(() => {
    audioPlayer.pause();
    audioPlayer.src = '';
});

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

async function handleSend(event, audio_msg) {
    let content
    if (audio_msg) {
        content = audio_msg.trim()
    } else {
        content = message.value.trim()
    }
    if (!content) return

    initAudioStream()

    const curId = ++ processId

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
                if (curId !== processId) return
                if (data.content) {
                    emits('addToLastMessage', data.content)
                }
                if (data.audio) {
                    handleAudioChunk(data.audio)
                }
            },
            onerror(error) {
            }
        })
    } catch (error) {
    }

}

function handleStop() {
    ++ processId
    stopAudio()
}

function close() {
    ++ processId
    showMic.value = false
    stopAudio()
}

defineExpose({
    focus, close
})
</script>

<template>
    <form v-if="!showMic" @submit.prevent="handleSend" class="absolute bottom-4 left-2 h-12 w-86 flex items-center">
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
        <div @click="showMic = true" class="absolute right-10 w-8 h-8 flex justify-center items-center cursor-pointer">
            <MicIcon />
        </div>
    </form>
    <MicroPhone 
        v-else
        @close="showMic = false"
        @send="handleSend"
        @stop="handleStop"
    />
</template>

<style scoped>

</style>