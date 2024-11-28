<template>
  <v-app>
    <v-main>
      <v-container>
        <h1 class="text-h4 mb-4" align="center">LILA RESEARCH PORTAL</h1>

        <!-- Chat Box Section -->
        <v-card class="mb-4">
          <v-card-title><h5>Local AI (Chat Bot)</h5></v-card-title>
          <v-card-text>
            <div class="chat-messages" ref="chatMessagesRef">
              <div
                v-for="(message, index) in chatMessages"
                :key="index"
                class="message"
                :class="message.sender"
              >
                <strong>{{ message.sender === "user" ? "You" : "AI" }}:</strong>
                <span v-if="message.sender === 'user'">{{ message.text }}</span>
                <div v-else v-html="parseMarkdown(message.text)"></div>
              </div>
            </div>
            <div class="d-flex align-center mt-4">
              <v-text-field
                v-model="question"
                label="Enter your question"
                @keyup.enter="submitQuery"
                :disabled="querying"
                class="flex-grow-1 mr-2"
                hide-details
              ></v-text-field>
              <v-btn
                fab
                small
                color="black"
                @click="submitQuery"
                :disabled="!isValidQuestion || querying"
                :loading="querying"
                class="ml-2 square-button"
              >
                <v-icon size="23">mdi-send</v-icon>
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-container>
    </v-main>

    <!-- Notifications -->
    <v-snackbar v-model="snackbar" :color="snackbarColor">
      {{ snackbarText }}
      <template v-slot:actions>
        <v-btn color="white" text @click="snackbar = false">Close</v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script>
import { ref, watch, computed } from "vue";
import axios from "axios";

export default {
  name: "App",
  setup() {
    const question = ref("");
    const querying = ref(false);
    const snackbar = ref(false);
    const snackbarText = ref("");
    const snackbarColor = ref("success");
    const chatMessages = ref([]);
    const chatMessagesRef = ref(null);

    const API_BASE_URL = "http://localhost:8000"; // Refer to local host

    const isValidQuestion = computed(() => {
      return question.value.trim().length > 0;
    });

    const parseMarkdown = (text) => {
      // Apply Markdown parsing
      return text
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>")
        .replace(/^### (.*$)/gm, "<h3>$1</h3>")
        .replace(/^## (.*$)/gm, "<h2>$1</h2>")
        .replace(/^# (.*$)/gm, "<h1>$1</h1>")
        .replace(/^\* (.*$)/gm, "<li>$1</li>")
        .replace(/^\d+\. (.*$)/gm, "<li>$1</li>")
        .replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>")
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2">$1</a>')
        .replace(/\n/g, "<br>");
    };

    const submitQuery = async () => {
      if (!isValidQuestion.value || querying.value) return;

      querying.value = true;
      const trimmedQuestion = question.value.trim();
      chatMessages.value.push({ sender: "user", text: trimmedQuestion });
      question.value = "";

      try {
        const url = `${API_BASE_URL}/question/?question=${encodeURIComponent(
          trimmedQuestion
        )}`;
        const response = await axios.get(url);
        chatMessages.value.push({
          sender: "ai",
          text: response.data.answer,
        });
      } catch (error) {
        console.error("Error querying document:", error);
        showSnackbar("Error querying document", "error");
      } finally {
        querying.value = false;
      }
    };

    const showSnackbar = (text, color) => {
      snackbarText.value = text;
      snackbarColor.value = color;
      snackbar.value = true;
    };

    // Scroll to bottom of chat messages when new message is added
    watch(
      chatMessages,
      () => {
        setTimeout(() => {
          if (chatMessagesRef.value) {
            chatMessagesRef.value.scrollTop =
              chatMessagesRef.value.scrollHeight;
          }
        }, 0);
      },
      { deep: true }
    );

    return {
      question,
      querying,
      snackbar,
      snackbarText,
      snackbarColor,
      chatMessages,
      chatMessagesRef,
      submitQuery,
      parseMarkdown,
      isValidQuestion,
    };
  },
};
</script>

<style scoped>
.chat-messages {
  height: 300px;
  overflow-y: auto;
  border: 1px solid #ccc;
  padding: 10px;
  margin-bottom: 10px;
}

.message {
  margin-bottom: 10px;
  padding: 5px;
  border-radius: 5px;
}

.user {
  background-color: #0b0b0b;
  text-align: right;
}

.ai {
  background-color: #0c0c0c;
  text-align: left;
}

.ai h1,
.ai h2,
.ai h3 {
  margin-top: 10px;
  margin-bottom: 5px;
}

.ai ul {
  margin-left: 20px;
}

.ai li {
  margin-bottom: 5px;
}

.square-button {
  border-radius: 4px !important;
  height: 50px !important;
}
</style>
