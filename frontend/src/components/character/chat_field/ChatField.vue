<script setup>
import { useTemplateRef, computed, nextTick, ref } from 'vue';
import InputField from './input_field/InputField.vue';
import ChatHistory from './chat_history/ChatHistory.vue';
import CharacterPhotoField from './character_photo_field/CharacterPhotoField.vue';

const props = defineProps(['friend'])
const modalRef = useTemplateRef('modal-ref')
const inputRef = useTemplateRef('input-ref')
const chatHistoryRef = useTemplateRef('chat-history-ref')
const history = ref([])

async function showModal() {
    modalRef.value.showModal()
    await nextTick()
    inputRef.value.focus()
}

const modalStyle = computed(() => {
  if (props.friend) {
    return {
      backgroundImage: `url(${props.friend.character.background_image})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
    }
  } else {
    return {}
  }
})

function handlePushBackMessage(msg) {
  history.value.push(msg)
  chatHistoryRef.value.scrollToBottom()
}

function handleAddToLastMessage(delta) {
  history.value.at(-1).content += delta
  chatHistoryRef.value.scrollToBottom()
}

function handlePushFrontMessage(msg) {
  history.value.unshift(msg)
}

function handleClose() {
  inputRef.value.close()
}

defineExpose({
    showModal,
})
</script>

<template>
    <dialog ref="modal-ref" class="modal" @close="handleClose">
        <div class="modal-box w-90 h-150" :style="modalStyle">
            <button @click="modalRef.close()" class="btn btn-sm btn-circle btn-ghost bg-transparent absolute right-1 top-1">✕</button>
            <ChatHistory
              ref="chat-history-ref" 
              v-if="props.friend"
              :history="history"
              :friendID="props.friend.id"
              :character="props.friend.character"
              @pushFrontMessage="handlePushFrontMessage"
            />
            <InputField 
              v-if="props.friend"
              ref="input-ref"
              :friendID="props.friend.id"
              @pushBackMessage="handlePushBackMessage"
              @addToLastMessage="handleAddToLastMessage"
             />
            <CharacterPhotoField v-if="props.friend" :character="props.friend.character"/>
        </div>
    </dialog>
</template>

<style scoped>

</style>