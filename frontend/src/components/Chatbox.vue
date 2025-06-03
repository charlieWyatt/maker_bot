<script setup lang="ts">
import { ref, nextTick } from "vue";
import axios from "axios";

const message = ref("");
const messages = ref<{ text: string; isUser: boolean }[]>([]);
const messagesContainer = ref<HTMLDivElement | null>(null);
const isWaiting = ref(false);

async function sendMessage() {
	if (!message.value || isWaiting.value) return;

	isWaiting.value = true;
	messages.value.push({
		text: message.value,
		isUser: true,
	});

	try {
		const res = await axios.post(
			"https://charliewyatt--maker-bot-fastapi-app.modal.run/llm_chat",
			{ 
        input_msg: message.value, 
        messages: messages
      }
		);
		messages.value.push({
			text: res.data.generated_text,
			isUser: false,
		});
	} catch (err) {
		messages.value.push({
			text: "Error: " + (err as Error).message,
			isUser: false,
		});
	}

	message.value = "";
	isWaiting.value = false;

	// Scroll to bottom after DOM updates
	await nextTick();
	if (messagesContainer.value) {
		messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
	}
}
</script>

<template>
	<div class="chat-container">
		<div class="messages" ref="messagesContainer">
			<div
				v-for="(msg, index) in messages"
				:key="index"
				:class="['message', msg.isUser ? 'user-message' : 'agent-message']"
			>
				{{ msg.text }}
			</div>
		</div>

		<div class="chat-box">
			<input
				type="text"
				v-model="message"
				:placeholder="
					isWaiting ? 'Waiting for response...' : 'Type a message...'
				"
				@keyup.enter="sendMessage"
				:disabled="isWaiting"
			/>
			<button
				@click="sendMessage"
				:disabled="isWaiting"
				:class="{ 'button-disabled': isWaiting }"
			>
				Send
			</button>
		</div>
	</div>
</template>

<style scoped>
.chat-container {
	display: flex;
	flex-direction: column;
	width: 90vw; /* Wider on mobile */
	margin-left: auto;
	margin-right: auto;
	height: 80vh; /* Taller on mobile */
	box-sizing: border-box;
	border: 1px solid #ccc;
	border-radius: 8px;
	overflow: hidden;
	margin: 0 auto; /* Center the container horizontally */
}

/* Media query for larger screens */
@media (min-width: 768px) {
	.chat-container {
		width: 50vw;
		height: 50vh;
	}
}

/* Messages take up all vertical space except chat box */
.messages {
	flex: 1;
	padding: 15px; /* Slightly reduced padding on mobile */
	overflow-y: auto;
	background-color: #f8f8f8;
	display: flex;
	flex-direction: column;
	gap: 10px;
}

.message {
	max-width: 85%; /* Wider messages on mobile */
	padding: 10px 15px;
	border-radius: 15px;
	word-wrap: break-word;
}

@media (min-width: 768px) {
	.message {
		max-width: 70%;
	}
}

.user-message {
	align-self: flex-end;
	background-color: #007bff;
	color: white;
	border-bottom-right-radius: 5px;
}

.agent-message {
	align-self: flex-start;
	background-color: white;
	color: black;
	border: 1px solid #e0e0e0;
	border-bottom-left-radius: 5px;
}

/* Input box */
.chat-box {
	display: flex;
	gap: 8px; /* Slightly reduced gap on mobile */
	padding: 8px; /* Slightly reduced padding on mobile */
	border-top: 1px solid #ccc;
	background-color: white;
}

input[type="text"] {
	flex: 1;
	padding: 12px; /* Slightly larger touch target */
	border: 1px solid #ccc;
	border-radius: 5px;
	font-size: 16px; /* Prevent zoom on mobile */
}

input[type="text"]:disabled {
	background-color: #f5f5f5;
	color: #666;
}

button {
	padding: 12px 20px; /* Larger touch target */
	background-color: #007bff;
	color: white;
	border: none;
	border-radius: 5px;
	cursor: pointer;
	font-size: 16px; /* Larger text for mobile */
	min-width: 80px; /* Ensure button isn't too small */
}

button:hover {
	background-color: #0056b3;
}

.button-disabled {
	background-color: #cccccc;
	cursor: not-allowed;
}

.button-disabled:hover {
	background-color: #cccccc;
}
</style>
