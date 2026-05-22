<script setup>
import Message from './message/Message.vue';
import { useTemplateRef, nextTick } from 'vue';
import api from '@/js/http/api.js';
import { onMounted, onBeforeUnmount } from 'vue';

const props = defineProps(['history', 'friendID', 'character'])
const scrollRef = useTemplateRef('scroll-ref')
const sentinelRef = useTemplateRef('sentinel-ref')
const emits = defineEmits(['pushFrontMessage'])
let isLoading = false
let hasMessages = true
let lastMessageID = 0

function checkSentinelVisible() {  // 判断哨兵是否能被看到
  if (!sentinelRef.value) return false

  const sentinelRect = sentinelRef.value.getBoundingClientRect()
  const scrollRect = scrollRef.value.getBoundingClientRect()
  return sentinelRect.top < scrollRect.bottom && sentinelRect.bottom > scrollRect.top
}

async function loadMore() {
    if (isLoading || !hasMessages) return 
    isLoading = true

    let newMessages = []
    try {
        const res = await api.get('/api/friend/message/get_history/', {
            params: {
                last_message_id: lastMessageID,
                friend_id: props.friendID,
            }
        })
        const data = res.data
        if (data.result === 'success') {
            newMessages = data.messages
        }
    } catch (error) {
    } finally {
        isLoading = false
        if (newMessages.length === 0) {
            hasMessages = false
        } else {
            const oldHeight = scrollRef.value.scrollHeight
            const oldTop = scrollRef.value.scrollTop

            for (const m of newMessages) {
                emits('pushFrontMessage', {
                    role: 'AI',
                    content: m.output,
                    id: crypto.randomUUID(),
                })
                emits('pushFrontMessage', {
                    role: 'user',
                    content: m.user_message,
                    id: crypto.randomUUID(),
                })
                lastMessageID = m.id
            }

            await nextTick()

            const newHeight = scrollRef.value.scrollHeight
            scrollRef.value.scrollTop = oldTop + newHeight - oldHeight

            if (checkSentinelVisible()) {
                await loadMore()
            }
        }
    }
}

let observer = null
onMounted(async () => {
    await loadMore()
    observer = new IntersectionObserver(
        entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    loadMore()
                }
            })
        },
        {root: null, rootMargin: '2px', threshold: 0}
    )
    observer.observe(sentinelRef.value)
})

onBeforeUnmount(() => {
    observer?.disconnect()
})

async function scrollToBottom() {
    await nextTick()
    scrollRef.value.scrollTop = scrollRef.value.scrollHeight
}

defineExpose({
    scrollToBottom,
})
</script>

<template>
    <div ref="scroll-ref" class="absolute top-18 left-0 w-90 h-112 overflow-y-scroll no-scrollbar">
        <div ref="sentinel-ref" class="h-2"></div>
        <Message
          v-for="msg in props.history"
          :key="msg.id"
          :message="msg"
          :character="props.character"
        />
    </div>
</template>

<style scoped>
/* 隐藏 Chrome, Safari 和 Opera 的滚动条 */
    .no-scrollbar::-webkit-scrollbar {
    display: none;
    }

    /* 隐藏 IE, Edge 和 Firefox 的滚动条 */
    .no-scrollbar {
    -ms-overflow-style: none; /* IE and Edge */
    scrollbar-width: none; /* Firefox */
    }
</style>